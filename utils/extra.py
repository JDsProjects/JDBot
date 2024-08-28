from __future__ import annotations

import enum
import io
import os
import pathlib
import random
import sys
import zlib
from typing import TYPE_CHECKING, Any, NamedTuple

import aiohttp
import black
import discord
import tabulate
import enum
from typing import Optional, Union
from discord import User, Guild, DMChannel, TextChannel

if TYPE_CHECKING:
    from ..main import JDBot


async def google_tts(bot: JDBot, text: str, language: str = "en") -> discord.File:
    async with bot.session.get(
        "https://api.jdjgbot.com/api/tts",
        params={"text": text, "language": language},
    ) as response:
        mp3_data = await response.read()

    mp3_fp = io.BytesIO(mp3_data)
    return discord.File(mp3_fp, f"{language}_tts.mp3")


async def latin_google_tts(bot: JDBot, text: str) -> discord.File:
    return await google_tts(bot, text, language="la")


def reference(message: discord.Message) -> Optional[discord.MessageReference]:
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        return message.reference.resolved.to_reference()
    return None


_ADDR_PAIRS = [
    ("8107EC20", "8107EC22"),
    ("8107EC28", "8107EC2A"),
    ("8107EC38", "8107EC3A"),
    ("8107EC40", "8107EC42"),
    ("8107EC50", "8107EC52"),
    ("8107EC58", "8107EC5A"),
    ("8107EC68", "8107EC6A"),
    ("8107EC70", "8107EC72"),
    ("8107EC80", "8107EC82"),
    ("8107EC88", "8107EC8A"),
    ("8107EC98", "8107EC9A"),
    ("8107ECA0", "8107ECA2"),
]


def _colored_addr_pair(addr1: str, addr2: str) -> str:
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    return f"{addr1} {r:02X}{g:02X}\n{addr2} {b:02X}00"


def cc_generate() -> str:
    return "\n".join(_colored_addr_pair(*addrs) for addrs in _ADDR_PAIRS)


async def post(bot: JDBot, code: str) -> str:
    paste_body = {
        "title": "JDBot Paste",
        "content": code,
        "description": "posted from jdbot",
        "text_colour": "#FFFFFF",
        "background_colour": "#000000",
        "embed_colour": "#FFFFFF",
    }

    async with bot.session.post(
        "https://api.senarc.net/paste",
        json=paste_body,
        headers={"accept": "application/json", "Content-Type": "application/json"},
    ) as response:
        json_data: dict = await response.json()
        return json_data.get("url")


async def get_paste(bot: JDBot, paste_id: str) -> Optional[str]:
    async with bot.session.get(
        f"https://api.senarc.net/bin/{paste_id}", headers={"accept": "application/json", "headless": "true"}
    ) as response:
        json_data: dict = await response.json()
        return json_data.get("content")


def groupby(iterable: list[Any], count: int) -> list[list[Any]]:
    return [iterable[i : i + count] for i in range(0, len(iterable), count)]


def npm_create_embed(data: dict) -> discord.Embed:
    e = discord.Embed(title=f"Package information for **{data.get('name')}**")
    e.add_field(name="**Latest Version:**", value=f"\n{data.get('latest_version', 'None Provided')}", inline=False)
    e.add_field(name="**Description:**", value=f"\n{data.get('description', 'None Provided')}", inline=False)

    formatted_author = ""
    authors = data.get("authors", [])
    if isinstance(authors, list):
        for author_data in authors:
            formatted_author += f"Email: {author_data.get('email', 'None Provided')}\nName: {author_data['name']}\n\n"
    else:
        formatted_author += f"Email: {authors.get('email', 'None Provided')}\n{authors['name']}"

    e.add_field(name="**Author:**", value=f"\n{formatted_author}", inline=False)
    e.add_field(name="**License:**", value=f"\n{data.get('license', 'None Provided')}", inline=False)

    dependencies = [[lib, min_version] for lib, min_version in data.get("dependencies", {}).items()]
    e.add_field(
        name="Dependencies:",
        value=f"\n{tabulate.tabulate(dependencies, ['Library', 'Minimum version'])}",
        inline=False,
    )

    if next_version := data.get("next_version"):
        e.add_field(name="**Upcoming Version:**", value=f"\n{next_version}")

    return e


def get_required_npm(data: dict) -> dict:
    latest = data["dist-tags"]["latest"]
    version_data = data["versions"][latest]

    return {
        "latest_version": latest,
        "next_version": data["dist-tags"].get("next"),
        "name": version_data["name"],
        "description": version_data["description"],
        "authors": data.get("author", data.get("maintainers")),
        "license": version_data.get("license"),
        "dependencies": {lib: ver.strip("^") for lib, ver in version_data.get("dependencies", {}).items()},
    }


def formatter(code: str, use_long_lines: bool = False) -> str:
    mode = black.Mode(line_length=120) if use_long_lines else black.Mode()
    return black.format_str(code, mode=mode)


def linecount() -> str:
    prefix = sys.prefix.replace("\\", "/")
    to_ignore = (str(prefix.split("/")[-1]), "src") if str(prefix) != str(sys.base_prefix) else "src"

    p = pathlib.Path("./")
    im = cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob("*.py"):
        if f.is_dir() or str(f).startswith(to_ignore):
            continue
        fc += 1
        with f.open() as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith("class "):
                    cl += 1
                elif l.startswith("def"):
                    fn += 1
                elif l.startswith("async def"):
                    cr += 1
                elif l.startswith(("from", "import")):
                    im += 1
                if "#" in l:
                    cm += 1
                ls += 1

    return f"Files: {fc}\nLines: {ls:,}\nClasses: {cl}\nFunctions: {fn}\nCoroutines: {cr}\nComments: {cm:,}\nImports: {im:,}"


class RtfmObject(NamedTuple):
    name: str
    url: str

    def __str__(self) -> str:
        return self.name


async def rtfm(bot: JDBot, url: str) -> list[RtfmObject]:
    async with bot.session.get(f"{url}objects.inv") as response:
        data = await response.read()

    lines = data.split(b"\n")
    header_lines = [line for line in lines[:10] if not line.startswith(b"#")]
    content_lines = lines[10:]

    full_data = zlib.decompress(b"\n".join(header_lines + content_lines))
    normal_data = full_data.decode()
    new_list = normal_data.split("\n")

    results = []
    for line in new_list:
        try:
            name, python_type, number, fragment, *label = line.split(" ")
            text = " ".join(label)
            label = text if text != "-" else name
            fragment = fragment.replace("$", name)
            results.append(RtfmObject(label, url + fragment))
        except ValueError:
            continue

    return results


async def asset_converter(ctx, assets):
    assets = list(assets)
    attachments = ctx.message.attachments

    if not attachments and not assets:
        assets.append(ctx.author)

    images = []

    for attachment in attachments:
        if attachment.content_type in ("image/png", "image/jpeg", "image/gif", "image/webp"):
            images.append(attachment)

    for asset in assets:
        if isinstance(asset, discord.PartialEmoji):
            images.append(asset)
        elif isinstance(asset, (discord.User, discord.Member)):
            images.append(asset.display_avatar)
        elif isinstance(asset, aiohttp.ClientResponse):
            if asset.content_type in ("image/png", "image/jpeg", "image/gif", "image/webp"):
                images.append(asset)

    if not images:
        images.append(ctx.author.display_avatar)

    return images[:10]


class TemperatureReadings(NamedTuple):
    celsius: float
    fahrenheit: float
    kelvin: float
    rankine: float


class Temperature(enum.Enum):
    celsius = "Celsius"
    fahrenheit = "Fahrenheit"
    kelvin = "Kelvin"
    rankine = "Rankine"

    def convert_to(self, value: float) -> TemperatureReadings:
        match self:
            case Temperature.celsius:
                c = value
                k = c + 273.15
                f = (c * 1.8) + 32
                r = f + 459.67
            case Temperature.fahrenheit:
                f = value
                c = (f - 32) * 0.5556
                k = c + 273.15
                r = f + 459.67
            case Temperature.kelvin:
                k = value
                c = k - 273.15
                f = (c * 1.8) + 32
                r = f + 459.67
            case Temperature.rankine:
                r = value
                f = r - 459.67
                c = (f - 32) * 0.5556
                k = c + 273.15

        return TemperatureReadings(round(c, 1), round(f, 1), round(k, 1), round(r, 1))


class SpeedReadings(NamedTuple):
    miles: float
    kilometers: float
    meters: float
    feet: float
    megameters: float
    light: float


class Speed(enum.Enum):
    miles = "Miles"
    kilometers = "Kilometers"
    meters = "Meters"
    feet = "Feet"
    megameters = "Megameters"
    light = "Light Speed"

    def convert_to(self, value: float) -> SpeedReadings:
        match self:
            case Speed.miles:
                miles = value
                kilometers = 1.609344 * miles
                meters = kilometers * 1000
                feet = 5280 * miles
                megameters = kilometers / 1000
                light = meters / 299792458
            case Speed.kilometers:
                kilometers = value
                meters = kilometers * 1000
                miles = kilometers / 1.609344
                feet = 5280 * miles
                megameters = kilometers / 1000
                light = meters / 299792458
            case Speed.meters:
                meters = value
                kilometers = meters / 1000
                megameters = kilometers / 1000
                light = meters / 299792458
                miles = kilometers / 1.609344
                feet = 5280 * miles
            case Speed.feet:
                feet = value
                miles = feet / 5280
                kilometers = miles * 1.609344
                meters = kilometers * 1000
                megameters = kilometers / 1000
                light = meters / 299792458
            case Speed.megameters:
                megameters = value
                kilometers = megameters * 1000
                meters = kilometers * 1000
                light = meters / 299792458
                miles = kilometers / 1.609344
                feet = 5280 * miles
            case Speed.light:
                light = value
                meters = light * 299792458
                kilometers = meters / 1000
                miles = kilometers / 1.609344
                feet = 5280 * miles
                megameters = kilometers / 1000

        return SpeedReadings(
            round(miles, 2),
            round(kilometers, 2),
            round(meters, 2),
            round(feet, 2),
            round(megameters, 2),
            round(light, 2),
        )


class InvalidateType(enum.IntEnum):
    GLOBAL = 0
    GUILD = 1
    DM = 2
    CHANNEL = 3


class InvalidationConfig:
    def __init__(self, entity_id: int, entity_type: InvalidateType, bot: "JDBot"):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.bot = bot

    @property
    def entity(self) -> Optional[Union[User, Guild, DMChannel, TextChannel]]:
        match self.entity_type:
            case InvalidateType.GLOBAL:
                return self.bot.get_user(self.entity_id)
            case InvalidateType.GUILD:
                return self.bot.get_guild(self.entity_id)
            case InvalidateType.DM:
                user = self.bot.get_user(self.entity_id)
                return user.dm_channel if user else None
            case InvalidateType.CHANNEL:
                return self.bot.get_channel(self.entity_id)
        return None


class InvalidationManager:
    def __init__(self, bot: "JDBot"):
        self.bot = bot

    async def add_entity(
        self, entity_id: int, entity_type: InvalidateType, in_chosen: bool = True
    ) -> InvalidationConfig:
        table = "invalidation_config" if in_chosen else "invalidation_out"
        await self.bot.db.execute(
            f"INSERT INTO {table} (entity_id, entity_type) VALUES ($1, $2)", entity_id, entity_type.value
        )
        return InvalidationConfig(entity_id, entity_type, self.bot)

    async def verify_entity(
        self, entity_id: int, entity_type: InvalidateType, in_chosen: bool = True
    ) -> Optional[dict]:
        table = "invalidation_config" if in_chosen else "invalidation_out"
        return await self.bot.db.fetchrow(
            f"SELECT * FROM {table} WHERE entity_id = $1 AND entity_type = $2", entity_id, entity_type.value
        )

    async def remove_entity(self, entity_id: int, entity_type: InvalidateType, in_chosen: bool = True) -> None:
        table = "invalidation_config" if in_chosen else "invalidation_out"
        await self.bot.db.execute(
            f"DELETE FROM {table} WHERE entity_id = $1 AND entity_type = $2", entity_id, entity_type.value
        )

    def check_invalidation(
        self, cache: list[InvalidationConfig], entity_id: int, entity_type: InvalidateType
    ) -> Optional[InvalidationConfig]:
        return next(
            (config for config in cache if config.entity_id == entity_id and config.entity_type == entity_type), None
        )


# Usage example:
# invalidation_manager = InvalidationManager(bot)
# await invalidation_manager.add_entity(user_id, InvalidateType.GLOBAL)
# result = await invalidation_manager.verify_entity(guild_id, InvalidateType.GUILD)
# await invalidation_manager.remove_entity(channel_id, InvalidateType.CHANNEL)
# config = invalidation_manager.check_invalidation(cache, user_id, InvalidateType.DM)
