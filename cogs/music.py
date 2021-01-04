from discord.etx import commands
import discord
import wavelink
import asyncio

class Music(commands.Cog):

  def __init__(self, client):
    self.client = client
  
def setup(client):
  client.add_cog(Music(client))

async def wavelink_start():
  await asyncio.create_subprocess_shell('java -jar Lavalink.jar')