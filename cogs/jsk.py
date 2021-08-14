from discord.ext import commands
from jishaku.features.baseclass import Feature
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

#look into making more jishaku commands: https://jishaku.readthedocs.io/en/latest/cog.html

class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error

def setup(bot: commands.Bot):
  bot.add_cog(Jishaku(bot = bot))