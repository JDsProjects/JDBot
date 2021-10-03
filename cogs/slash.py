import discord
from discord.ext import commands

class Slash(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  #@commands.command(brief = "addes a slash command to a guild", #slash_command = True)
  #async def add_command(self, ctx):
    #await ctx.send("Slash commands are in work in progress")

def setup(bot):
  bot.add_cog(Slash(bot))