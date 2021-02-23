import discord
import re
from discord.ext import commands
import os

async def get_prefix(client,message):
  extras = ["test*","te*"]
  comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
  match = comp.match(message.content)
  if match is not None:
    extras.append(match.group(1))
  return commands.when_mentioned_or(*extras)(client, message)

client = commands.Bot(command_prefix=(get_prefix),intents = discord.Intents.all())

client.load_extension('jishaku')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
      try:
        client.load_extension(f'cogs.{filename[:-3]}')
      except commands.errors.NoEntryPointError:
        pass