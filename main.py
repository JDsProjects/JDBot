import discord
from discord.ext import commands, tasks
import B
import ClientConfig
import os
import logging
import asyncio
import DatabaseConfig
import DatabaseControl

logging.basicConfig(level=logging.INFO)
client = ClientConfig.client

B.b()
client.run(os.environ["classic_token"])