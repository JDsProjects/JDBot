import discord
import utils
from discord.ext import commands

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief = "Currently work in progress(WIP)")
  async def work(self, ctx, *, args = None):
    member = ctx.author

    await ctx.send("Being Upgraded from mongodb to sql, please wait")

  @commands.command(brief = "a command to send how much money you have(work in progress)", help = "using the JDBot database you can see how much money you have", aliases = ["bal"])
  async def balance(self, ctx, *, member: utils.BetterMemberConverter = None):

    member = member or ctx.author

    await ctx.send("Being Upgraded from mongodb to sql, please wait")
  

def setup(bot):
  bot.add_cog(Economy(bot))