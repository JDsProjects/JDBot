from discord.ext import commands, tasks
import discord, random

class Global(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief = "wait for it to release")
  async def global_wip(self, ctx):
    await ctx.send("currently global chat is WIP for JDBot.")

def setup(bot):
  bot.add_cog(Global(bot))