""" CREDITS: https://github.com/jay3332/pilmoji"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Final, List, Literal, Optional, Pattern, Tuple, Union

import unicodedata
from re import compile as re_compile
from re import escape as re_escape
import unicodedata
from urllib.parse import quote_plus

from discord import PartialEmoji
from discord.asset import AssetMixin
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

    @property
    def url(self) -> str:
        if self.unicode:
            return f"{self.EMOJI_URL}{quote_plus(self.emoji)}" + (f"?style={self._style}" if self._style else "")  # type: ignore
        return super().url

    @classmethod
    def as_unicode(cls, item: str, style: Optional[ValidStyles] = None) -> Self:
        unicode = (item.encode("unicode-escape")).decode()
        _id = unicode[5:]
        name = unicodedata.name(item, item.replace(":", ""))
        return cls(emoji=item, name=name, id=_id, animated=False, style=style, unicode=unicode)  # type: ignore

    @classmethod
    def as_emoji(cls, emoji: str) -> Self:
        obj = cls.from_str(str(emoji))
        return cls(emoji=str(obj), name=obj.name, id=obj.id, animated=obj.animated)

    def with_style(self, style: ValidStyles) -> Self:
        if not self.unicode:
            raise TypeError("Cannot set style for non-unicode emoji")

        return self.__class__(
            name=self.name, animated=self.animated, id=self.id, emoji=self.emoji, style=style, unicode=self.unicode
        )

    async def is_valid(self) -> bool:
        try:
            await self.read()
        except Exception:
            return False
        else:
            return True

    async def read(self) -> bytes:
        return await AssetMixin.read(self)


class EmojiConverter(Converter[Any]):
    class ConvertedEmojis:
        def __init__(
            self,
            original_input: str,
            parsed_output: List[Tuple[List[str], List[CustomEmoji]]],
            invalid_emojis: List[str],
            valid_emojis: List[CustomEmoji],
        ) -> None:
            self.original_input: str = original_input
            self.parsed_output: List[Tuple[List[str], List[CustomEmoji]]] = parsed_output
            self.invalid_emojis: List[str] = invalid_emojis
            self.valid_emojis: List[CustomEmoji] = valid_emojis

        @property
        def all(self) -> List[Union[str, CustomEmoji]]:
            return self.valid_emojis + self.invalid_emojis

    def _parse_line(self, line: str, /) -> Tuple[List[str], List[CustomEmoji]]:
        texts: List[str] = []
        emojis: List[CustomEmoji] = []
        for i, chunk in enumerate(EMOJI_REGEX.split(line)):
            if not chunk:
                continue

            if not i % 2:
                texts.append(chunk)
                continue

            if len(chunk) > 18:
                emoji = CustomEmoji.as_emoji(chunk)
            else:
                try:
                    emoji = CustomEmoji.as_unicode(chunk)
                except (TypeError, ValueError):
                    texts.append(chunk)
                    continue

            if not emoji:
                texts.append(chunk)
                continue
            emojis.append(emoji)

        return texts, emojis

    def parse_emojis(self, text: str, /) -> List[Tuple[List[str], List[CustomEmoji]]]:
        return [self._parse_line(line) for line in text.splitlines()]

    async def convert(self, ctx: Context, argument: str):
        valid_emojis = []
        invalid_emojis = []
        parsed_output = self.parse_emojis(argument.strip())
        for (texts, line) in parsed_output:
            for text in texts:
                if text.strip():
                    invalid_emojis.append(text.strip())
            for emoji in line:
                emoji._state = ctx.bot._connection  # type: ignore
                if await emoji.is_valid():
                    valid_emojis.append(emoji)
                else:
                    invalid_emojis.append(str(emoji))

        if not valid_emojis:
            raise InvalidEmojis(argument, invalid_emojis)

        return self.ConvertedEmojis(argument, parsed_output, invalid_emojis, valid_emojis)
