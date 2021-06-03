import dbl
import discord
from discord.ext import commands, tasks
import os, logging, discordlists

class DSLCount(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.token = os.environ["topgg_key"]

    self.api = discordlists.Client(self.bot)  
    self.api.set_auth("disforge.com",os.environ["disforge_key"])
    self.api.start_loop()

    self.dblpy = dbl.DBLClient(self.bot,self.token)
    self.update_stats.start()
  
  @tasks.loop(minutes=5)
  async def update_stats(self):
    logger.info('Attempting to post server count')
    try:
      await self.dblpy.post_guild_count()
      logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
    except Exception as e:
      logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

  def cog_unload(self):
    self.update_stats.stop()
    self.api.stop()
    
    #not sure if doing self.api is okay, but it should be.
  
def setup(bot):
  global logger
  logger = logging.getLogger('bot')
  bot.add_cog(DSLCount(bot))