import money_system, utils
from discord.ext import commands

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="Currently work in progress(WIP)")
  async def work(self,ctx,*,args=None):
    Member = ctx.author.id
    if args is None:
      money_system.add_money(Member,10,0)

  @commands.command(brief="a command to send how much money you have(work in progress)",help="using the JDBot database you can see how much money you have")
  async def balance(self,ctx,*, Member: utils.BetterMemberConverter = None):
    if Member is None:
      Member = ctx.author
    money_system.display_account(Member.id)

def setup(bot):
  bot.add_cog(Economy(bot))