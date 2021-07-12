import discord
from discord.ext import commands
import json

class Slash(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="work in progress")
  async def wip(self, ctx):
    await ctx.send("Slash commands are in work in progress")

def setup(bot):
  bot.add_cog(Slash(bot))