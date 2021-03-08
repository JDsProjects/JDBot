import dbl
import discord
from discord.ext import commands, tasks
import os
import logging

class DSLCount(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.token = os.environ["topgg_key"]
    self.dblpy = dbl.DBLClient(self.client,self.token)
    self.update_stats.start()
  
  @tasks.loop(minutes=5)
  async def update_stats(self):
    logger.info('Attempting to post server count')
    try:
      await self.dblpy.post_guild_count()
      logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
    except Exception as e:
      logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

  
def setup(client):
  global logger
  logger = logging.getLogger('client')
  client.add_cog(DSLCount(client))