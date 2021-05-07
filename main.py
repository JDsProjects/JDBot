import discord, os, logging, asyncio
from discord.ext import commands, tasks
import B, ClientConfig,  DatabaseConfig , DatabaseControl

logging.basicConfig(level=logging.INFO)
client = ClientConfig.client

B.b()
client.run(os.environ["classic_token"])