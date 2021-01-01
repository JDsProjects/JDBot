import discord
import re
from discord.ext import commands

async def get_prefix(client,message):
  extras = ["test*"]
  comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
  match = comp.match(message.content)
  if match is not None:
    extras.append(match.group(1))
  return commands.when_mentioned_or(*extras)(client, message)

client = commands.Bot(command_prefix=(get_prefix),intents = discord.Intents.all())

