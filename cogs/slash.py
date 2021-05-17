import discord
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
import json

class Slash(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command(brief="work in progress")
  async def wip(self,ctx):
    await ctx.send("Slash commands are in work in progress")

def setup(client):
  client.add_cog(Slash(client))