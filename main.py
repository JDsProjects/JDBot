from __future__ import annotations

import functools
import logging
import os
import re
import sys
import traceback
from typing import Any, Optional

import aiohttp
import asyncpg
import discord
import dotenv
from discord.ext import commands
from tweepy.asynchronous import AsyncClient

dotenv.load_dotenv()


async def get_prefix(bot: JDBot, message: discord.Message):
    extras = ["test*", "te*", "t*", "jdbot.", "jd.", "test.", "te."]

    if message.guild:
        if message.guild.id in bot.prefix_cache:
            prefix = bot.prefix_cache[message.guild.id]
            if prefix != None:
                extras.append(prefix)
        else:
            db = bot.db
            dbprefix = await db.fetchrow("SELECT prefix FROM PREFIXES WHERE is_dm = 0 AND id = $1", message.guild.id)
            if dbprefix:
                dbprefix = dbprefix.get("prefix")
            bot.prefix_cache[message.guild.id] = dbprefix
            if dbprefix:
                extras.append(dbprefix)

    if message.author.id in bot.prefix_cache:
        prefix = bot.prefix_cache[message.author.id]
        if prefix != None:
            extras.append(prefix)
    else:
        db = bot.db
        dbprefix = await db.fetchrow("SELECT prefix FROM PREFIXES WHERE is_dm = 1 AND id = $1", message.author.id)
        if dbprefix:
            dbprefix = dbprefix.get("prefix")
        bot.prefix_cache[message.author.id] = dbprefix
        if dbprefix:
            extras.append(dbprefix)

    comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
    match = comp.match(message.content)
    if match is not None:
        extras.append(match.group(1))

    if await bot.is_owner(message.author) and bot.prefixless:
        extras.append("")

    return commands.when_mentioned_or(*extras)(bot, message)


class JDBotContext(commands.Context):
    async def send(self, *args: Any, **kwargs: Any) -> discord.Message:
        msg = await super().send(*args, **kwargs)
        view = kwargs.get("view")
        if view is not None:
            view.message = msg

        return msg

    async def reply(self, *args: Any, **kwargs: Any) -> discord.Message:
        msg = await super().reply(*args, **kwargs)

        view = kwargs.get("view")
        if view is not None:
            view.message = msg

        return msg


class CustomRecordClass(asyncpg.Record):
    def __getattr__(self, name: str) -> Any:
        if name in self.keys():
            return self[name]
        return super().__getattr__(name)


class JDBot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.special_access: dict[int, str] = {}
        self.messages = {}
        self.suspended: bool = False
        self.prefixless: bool = False
        # used for testing purposes and to make the bot prefixless for owners only
        self.prefix_cache: dict[int, str] = {}

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self.session = aiohttp.ClientSession()
        self.db = await asyncpg.create_pool(os.getenv("DB_key"), record_class=CustomRecordClass)  # need to type fix
        # loads up some bot variables

        self.testers = [u.get("user_id") for u in await self.db.fetch("SELECT * FROM testers_list;")]

        # does the DB connection and then assigns it a tester list

        self.blacklisted_users: dict[int, str] = dict(await self.db.fetch("SELECT * FROM BLACKLISTED_USERS;"))
        self.sus_users: dict[int, str] = dict(await self.db.fetch("SELECT * FROM SUS_USERS;"))

        self.history: list[str] = [h.get("response") for h in await self.db.fetch("SELECT * FROM RANDOM_HISTORY")]
        self.images: list[str] = [image.name for image in self.db.fetch("SELECT name FROM my_images")]

        consumer_key = os.getenv("tweet_key")
        consumer_secret = os.getenv("tweet_secret")

        access_token = os.getenv("tweet_access")
        access_secret = os.getenv("tweet_token")
        bearer_token = os.getenv("tweet_bearer")

        self.tweet_client = AsyncClient(
            bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )

        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.session.close()
        await self.db.close()
        await super().close()

    async def on_error(self, event, *args: Any, **kwargs: Any) -> None:
        more_information = sys.exc_info()
        error_wanted = traceback.format_exc()
        traceback.print_exc()

        # print(event)
        # print(more_information[0])
        # print(args)
        # print(kwargs)
        # check about on_error with other repos of mine as well to update this.

    async def get_context(self, message, *, cls=JDBotContext) -> JDBotContext:
        return await super().get_context(message, cls=cls)

    async def try_user(self, id: int, /) -> Optional[discord.User]:
        maybe_user = self.get_user(id)

        if maybe_user is not None:
            return maybe_user

        try:
            return await self.fetch_user(id)
        except discord.errors.NotFound:
            return None

    async def try_member(self, guild: discord.Guild, member_id: int, /) -> Optional[discord.Member]:
        member = guild.get_member(member_id)

        if member:
            return member
        else:
            try:
                return await guild.fetch_member(member_id)
            except discord.errors.NotFound:
                return None

    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except commands.errors.ExtensionError:
                    traceback.print_exc()

    @functools.cached_property
    def support_webhook(self) -> discord.Webhook:
        webhook_url = os.environ["SUPPORT_WEBHOOK"]
        return discord.Webhook.from_url(webhook_url, session=self.session)


intents = discord.Intents.all()

bot = JDBot(
    command_prefix=(get_prefix),
    intents=intents,
    chunk_guilds_at_startup=False,
    strip_after_prefix=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
)

bot.launch_time = discord.utils.utcnow()


@bot.check
async def check_command_access(ctx: JDBotContext):
    if ctx.command.name == bot.special_access.get(ctx.author.id):
        await ctx.reinvoke()

    if ctx.author.id in bot.special_access:
        del bot.special_access[ctx.author.id]

    return True


@bot.check
async def check_blacklist(ctx: JDBotContext):
    return not ctx.author.id in bot.blacklisted_users and not ctx.author.id in bot.sus_users


@bot.check
async def check_suspended(ctx: JDBotContext):
    return not ctx.bot.suspended or await ctx.bot.is_owner(ctx.author)


logging.basicConfig(level=logging.INFO)

bot.run(os.environ["classic_token"])
