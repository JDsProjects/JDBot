import os
import logging
import discord
import re
import aiohttp
import traceback
import asyncpg
from discord.ext import commands
import dotenv

dotenv.load_dotenv()


async def get_prefix(bot, message):
    extras = ["test*", "te*", "t*", "jdbot.", "jd.", "test.", "te."]

    comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
    match = comp.match(message.content)
    if match is not None:
        extras.append(match.group(1))

    if await bot.is_owner(message.author) and bot.prefixless:
        extras.append("")

    return commands.when_mentioned_or(*extras)(bot, message)


class JDBotContext(commands.Context):
    async def send(self, *args, **kwargs):
        msg = await super().send(*args, **kwargs)
        view = kwargs.get("view")
        if view is not None:
            view.message = msg

        return msg


class JDBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.special_access = {}
        self.messages = {}
        self.suspended = False
        self.prefixless = False
        # used for testing purposes and to make the bot prefixless for owners only

    async def start(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        self.db = await asyncpg.create_pool(os.getenv("DB_key"))

        # loads up some bot variables

        self.testers = [u.get("user_id") for u in await self.db.fetch("SELECT * FROM testers_list;")]

        # does the DB connection and then assigns it a tester list

        self.blacklisted_users = dict(await self.db.fetch("SELECT * FROM BLACKLISTED_USERS;"))

        self.blacklisted_users.update(dict(await self.db.fetch("SELECT * FROM SUS_USERS;")))

        self.history = [h.get("response") for h in await self.db.fetch("SELECT * FROM RANDOM_HISTORY")]

        await super().start(*args, **kwargs)

    async def close(self):
        await self.session.close()
        await self.db.close()
        await super().close()

    async def on_error(self, event, *args, **kwargs):
        more_information = os.sys.exc_info()
        error_wanted = traceback.format_exc()
        traceback.print_exc()

        # print(event)
        # print(more_information[0])
        # print(args)
        # print(kwargs)
        # check about on_error with other repos of mine as well to update this.

    async def get_context(self, message, *, cls=JDBotContext):
        return await super().get_context(message, cls=cls)


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
async def check_command_access(ctx):
    if ctx.command.name == bot.special_access.get(ctx.author.id):
        await ctx.reinvoke()

    if ctx.author.id in bot.special_access:
        del bot.special_access[ctx.author.id]

    return True


@bot.check
async def check_blacklist(ctx):
    return not ctx.author.id in bot.blacklisted_users


@bot.check
async def check_suspended(ctx):
    return not ctx.bot.suspended or await ctx.bot.is_owner(ctx.author)


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{filename[:-3]}")
        except commands.errors.ExtensionError:
            traceback.print_exc()


logging.basicConfig(level=logging.INFO)

bot.run(os.environ["classic_token"])
