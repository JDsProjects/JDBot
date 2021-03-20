import discord
from discord.ext import commands, tasks
import B
import ClientConfig
import os
import logging
import asyncio
import DatabaseConfig
import DatabaseControl

async def status_task():
  while True:
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="the return of JDBot"))
    await asyncio.sleep(40)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers | {len(client.users)} users"))
    await asyncio.sleep(40)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the new updates coming soon..."))
    await asyncio.sleep(40)

async def startup():
  await client.wait_until_ready()
  await status_task()

logging.basicConfig(level=logging.INFO)
client = ClientConfig.client

B.b()
client.loop.create_task(startup())
client.run(os.environ["classic_token"])
