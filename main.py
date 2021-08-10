import discord, os, logging, asyncio
from discord.ext import commands, tasks
import B, BotConfig,  DatabaseConfig , DatabaseControl

logging.basicConfig(level = logging.INFO)

B.b()
BotConfig.bot.run(os.environ["classic_token"])