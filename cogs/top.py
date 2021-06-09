from discord.ext import commands, tasks
import os, logging, discordlists, discord, topgg

class DSLCount(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.token = os.environ["topgg_key"]

    self.api = discordlists.Client(self.bot)  
    self.api.set_auth("disforge.com",os.environ["disforge_key"])
    self.api.set_auth("discord-botlist.eu", os.environ["botlist_eu_key"])
    self.api.start_loop()

    self.topgg = topgg.DBLClient(self.bot ,self.token)
    self.update_stats.start()
  
  @tasks.loop(minutes=5)
  async def update_stats(self):
    logger.info('Attempting to post server count')
    try:
      await self.topgg.post_guild_count()
      logger.info('Posted server count ({})'.format(self.topgg.guild_count))
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