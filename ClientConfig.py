import discord
from discord.ext import commands
client = discord.Client(intents = discord.Intents.all())
discordprefix = "test*"
client = commands.Bot(command_prefix=commands.when_mentioned_or(discordprefix))