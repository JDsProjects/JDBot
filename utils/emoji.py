""" CREDITS: https://github.com/jay3332/pilmoji"""

from __future__ import annotations

from re import compile as re_compile
from re import escape as re_escape
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Dict, Final, List, Literal, Optional, Pattern
from urllib.parse import quote_plus

from discord import Intents, PartialEmoji
from discord.ext import commands
from emoji import unicode_codes

if TYPE_CHECKING:
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

language_pack: Dict[str, str] = unicode_codes.get_emoji_unicode_dict("en")  # type: ignore
_UNICODE_EMOJI_REGEX = "|".join(map(re_escape, sorted(language_pack.values(), key=len, reverse=True)))
_DISCORD_EMOJI_REGEX = "<a?:[a-zA-Z0-9_]{2,32}:[0-9]{17,22}>"

EMOJI_REGEX: Final[Pattern[str]] = re_compile(f"({_UNICODE_EMOJI_REGEX}|{_DISCORD_EMOJI_REGEX})")


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
        is_unicode: bool = False,
    ) -> None:
        super().__init__(name=name, animated=animated, id=id)
        self.emoji: Optional[str] = emoji
        self._style: Optional[ValidStyles] = style
        self.is_unicode: bool = is_unicode

    def is_unicode_emoji(self) -> bool:
        if self.is_unicode:
            return False
        return super().is_unicode_emoji()

    @property
    def url(self) -> str:
        if self.is_unicode:
            return f"{self.EMOJI_URL}{quote_plus(self.emoji)}" + (f"?style={self._style}" if self._style else "")  # type: ignore
        return super().url

    @classmethod
    def as_unicode(cls, item: str, style: Optional[ValidStyles] = None) -> Self:
        digit = f"{ord(str(item)):x}"
        unicode = f"\\U{digit:>08}"
        emoji_name = item.replace(":", "")
        print("as uni", item, style, digit, unicode, emoji_name)
        return cls(emoji=item, name=unicode, id=digit, animated=False, style=style, is_unicode=True)  # type: ignore

    @classmethod
    def as_emoji(cls, emoji: str) -> Self:
        obj = cls.from_str(str(emoji))
        return cls(emoji=str(obj), name=obj.name, id=obj.id, animated=obj.animated)

    def with_style(self, style: ValidStyles) -> Optional[Self]:
        return self.__class__(name=self.name, animated=self.animated, id=self.id, emoji=self.emoji, style=style)

    async def is_valid(self) -> bool:
        try:
            await self.read()
        except Exception:
            return False
        else:
            return True

    async def read(self) -> bytes:
        print("url used:", self.url, self.emoji)
        return await super().read()


class EmojiConverter(commands.Converter[Any]):
    def _parse_line(self, line: str, /) -> List[CustomEmoji]:
        emojis = []
        for i, chunk in enumerate(EMOJI_REGEX.split(line)):
            if not chunk:
                continue

            if not i % 2:
                continue

            if len(chunk) > 18:  # This is guaranteed to be a Discord emoji
                node = CustomEmoji.as_emoji(chunk)
            else:
                node = CustomEmoji.as_unicode(chunk)

            emojis.append(node)

        return emojis

    def parse_emojis(self, text: str, /) -> List[List[CustomEmoji]]:
        return [self._parse_line(line) for line in text.splitlines()]

    async def convert(self, ctx: commands.Context, argument: str):
        valid_emojis = []
        emojis: List[List[CustomEmoji]] = self.parse_emojis(argument.strip())
        for line in emojis:
            for emoji in line:
                emoji._state = ctx.bot._connection  # type: ignore
                if result := await emoji.is_valid():
                    valid_emojis.append(emoji)

        return valid_emojis


# async def emoji(ctx: commands.Context, *, emojis: Annotated[List[CustomEmoji], EmojiConverter]):
# await ctx.send(f"{ctx.message.content}\n{emojis=}\n{[e.url for e in emojis]=}")
