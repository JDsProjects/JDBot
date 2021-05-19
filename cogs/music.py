from discord.ext import commands
import discord, wavelink, asyncio

class Music(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    if not hasattr(bot, 'wavelink'):
      self.bot.wavelink = wavelink.Client(bot=self.bot)

    self.bot.loop.create_task(self.start_nodes())

  async def start_nodes(self):
    await self.bot.wait_until_ready()
    await self.bot.wavelink.initiate_node(host='lava.link', port=80, rest_uri='https://lava.link', password='something.host', identifier='MusicBot', region='us_central')

  async def stop_nodes(self):
    await self.bot.wavelink.destroy_node( identifier="MusicBot")

  def cog_unload(self):
    self.bot.loop.create_task(self.stop_nodes())
    super().cog_unload()

  @commands.command(name='connect')
  async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
    if not channel:
      try:
        channel = ctx.author.voice.channel
      except AttributeError:
          raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

    player = self.bot.wavelink.get_player(ctx.guild.id)
    await ctx.send(f'Connecting to **`{channel.name}`**')
    await player.connect(channel.id)
  
  @connect_.error
  async def connect_error(self,ctx,error):
    await ctx.send(error)

  @commands.command()
  async def play(self, ctx, *, query: str):
    tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

    if not tracks:
      return await ctx.send('Could not find any songs with that query.')

    player = self.bot.wavelink.get_player(ctx.guild.id)
    if not player.is_connected:
      await ctx.invoke(self.connect_)

    await ctx.send(f'Added {str(tracks[0])} to the queue.')
    await player.play(tracks[0])

  @play.error
  async def play_error(self,ctx,error):
    await ctx.send(error)

  @commands.command()
  async def force_disconnect(self,ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    await player.destroy()

  @force_disconnect.error
  async def force_disconnect_error(self,ctx,error):
    await ctx.send(error)

  @commands.command(name="disconnect")
  async def disconnect_(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_connected:
      await player.disconnect()

    if player.is_connected is False:
      await ctx.send("Can't Disconnect from no channels")

  @disconnect_.error
  async def disconnect_error(self,ctx,error):
    await ctx.send(error)

  @commands.command()
  async def stop(self,ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    await player.stop()

  @stop.error
  async def stop_error(self,ctx,error):
    await ctx.send(error)

  @commands.command()
  async def pause(self,ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_paused:
      await player.set_pause(False)
    
    if player.is_paused is False:
      await player.set_pause(True)

  @commands.command()
  async def resume(self,ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_paused:
      await player.set_pause(True)

def setup(bot):
  bot.add_cog(Music(bot))