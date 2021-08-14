from discord.ext import commands
from jishaku.features.baseclass import Feature
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

#look into making more jishaku commands: https://jishaku.readthedocs.io/en/latest/cog.html

class Jishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
  pass

def setup(bot: commands.Bot):
  bot.add_cog(Jishaku(bot=bot))