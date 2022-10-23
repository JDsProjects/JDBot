""" CREDITS: https://github.com/jay3332/pilmoji"""

from __future__ import annotations

from re import compile as re_compile
from re import escape as re_escape
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Final, List, Literal, Optional, Pattern, Tuple, Union
from urllib.parse import quote_plus

from discord import PartialEmoji
from discord.ext.commands import BadArgument, Context, Converter
from emoji import unicode_codes

if TYPE_CHECKING:
    from discord.ext.commands import Context
    from typing_extensions import Self

    ValidStyles = Literal[
        "apple",
        "google",
        "microsoft",
        "samsung",
        "whatsapp",
        "twitter",
        "facebook",
        "messenger",
        "joypixels",
        "openemojis",
        "emojidex",
        "lg",
        "htc",
        "mozilla",
    ]

__all__: Tuple[str, ...] = ("CustomEmoji", "EmojiConverter", "InvalidEmojis")

language_pack: Dict[str, str] = unicode_codes.get_emoji_unicode_dict("en")  # type: ignore
_UNICODE_EMOJI_REGEX = "|".join(map(re_escape, sorted(language_pack.values(), key=len, reverse=True)))
_DISCORD_EMOJI_REGEX = "<a?:[a-zA-Z0-9_]{2,32}:[0-9]{17,22}>"

EMOJI_REGEX: Final[Pattern[str]] = re_compile(f"({_UNICODE_EMOJI_REGEX}|{_DISCORD_EMOJI_REGEX})")


class InvalidEmojis(BadArgument):
    """Raised when a string contains no valid emojis."""

    def __init__(self, full_input: str, splitted_text: List[str]) -> None:
        self.argument: str = full_input
        self.splitted_text: List[str] = splitted_text
        super().__init__(f"Invalid emojis: {self.splitted_text}")


class CustomEmoji(PartialEmoji):
    DISCORD_EMOJI_URL: ClassVar[str] = "https://cdn.discordapp.com/emojis/"
    EMOJI_URL: ClassVar[str] = "https://emojicdn.elk.sh/"

    def __init__(
        self,
        *,
        name: str,
        animated: bool = False,
        emoji: Optional[str] = None,
        id: Optional[int] = None,
        style: Optional[ValidStyles] = None,
        unicode: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, animated=animated, id=id)
        self.emoji: Optional[str] = emoji
        self._style: Optional[ValidStyles] = style
        self.unicode: Optional[str] = unicode

    def is_unicode_emoji(self) -> bool:
        if self.unicode:
            return False
        return super().is_unicode_emoji()

    @property
    def url(self) -> str:
        if self.unicode:
            return f"{self.EMOJI_URL}{quote_plus(self.emoji)}" + (f"?style={self._style}" if self._style else "")  # type: ignore
        return super().url

    @classmethod
    def as_unicode(cls, item: str, style: Optional[ValidStyles] = None) -> Self:
        digit = f"{ord(str(item)):x}"
        unicode = f"\\U{digit:>08}"
        name = item.replace(":", "")
        return cls(emoji=item, name=name, id=digit, animated=False, style=style, unicode=unicode)  # type: ignore

    @classmethod
    def as_emoji(cls, emoji: str) -> Self:
        obj = cls.from_str(str(emoji))
        return cls(emoji=str(obj), name=obj.name, id=obj.id, animated=obj.animated)

    def with_style(self, style: ValidStyles) -> Self:
        if not self.unicode:
            raise TypeError("Cannot set style for non-unicode emoji")

        return self.__class__(name=self.name, animated=self.animated, id=self.id, emoji=self.emoji, style=style)

    async def is_valid(self) -> bool:
        try:
            await self.read()
        except Exception:
            return False
        else:
            return True


class EmojiConverter(Converter[Any]):
    class ConvertedEmojis:
        def __init__(self, input: str, invalid_emojis: List[str], valid_emojis: List[CustomEmoji]) -> None:
            self.input: str = input
            self.invalid_emojis: List[str] = invalid_emojis
            self.valid_emojis: List[CustomEmoji] = valid_emojis

        @property
        def all(self) -> List[Union[str, CustomEmoji]]:
            return self.valid_emojis + self.invalid_emojis

    def _parse_line(self, line: str, /) -> List[Union[str, CustomEmoji]]:
        def try_unicode(text: str) -> bool:
            try:
                CustomEmoji.as_unicode(text)
            except Exception:
                return False
            else:
                return True

        def try_discord_emoji(text: str) -> bool:
            try:
                CustomEmoji.from_str(text)
            except Exception:
                return False
            else:
                return True

        emojis = []
        for i, chunk in enumerate(EMOJI_REGEX.split(line)):
            if not chunk:
                continue

            if not i % 2:
                emoji = chunk

            emoji = chunk
            if len(chunk) > 18 or try_discord_emoji(chunk):
                if try_discord_emoji(chunk):
                    emoji = CustomEmoji.as_emoji(chunk)
            elif try_unicode(chunk):
                emoji = CustomEmoji.as_unicode(chunk)
            else:
                emoji = chunk

            emojis.append(emoji)

        return emojis

    def parse_emojis(self, text: str, /) -> List[List[Union[str, CustomEmoji]]]:
        return [self._parse_line(line) for line in text.splitlines()]

    async def convert(self, ctx: Context, argument: str):
        valid_emojis = []
        invalid_emojis = []
        emojis: List[List[Union[str, CustomEmoji]]] = self.parse_emojis(argument.strip())
        for line in emojis:
            for emoji in line:
                if not isinstance(emoji, CustomEmoji):
                    invalid_emojis.append(emoji)
                    continue

                emoji._state = ctx.bot._connection  # type: ignore
                if await emoji.is_valid():
                    valid_emojis.append(emoji)
                else:
                    invalid_emojis.append(str(emoji))

        if not valid_emojis:
            raise InvalidEmojis(argument, invalid_emojis)

        return self.ConvertedEmojis(argument, invalid_emojis, valid_emojis)
