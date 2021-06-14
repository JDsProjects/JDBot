from discord.ext import commands
import discord, wavelink, asyncio, os

class Music(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    if not hasattr(bot, 'wavelink'):
      self.bot.wavelink = wavelink.Client(bot=self.bot)

    self.bot.loop.create_task(self.start_nodes())

  async def start_nodes(self):
    await self.bot.wait_until_ready()
    await self.bot.wavelink.initiate_node(host=os.environ["wavelink_host"], port=int(os.environ["wavelink_port"]), rest_uri=os.environ["wavelink_uri"], password=os.environ["wavelink_pass"], identifier="JDBot", region='us_central')

  async def stop_nodes(self):
    await self.bot.wavelink.destroy_node( identifier="JDBot")

  def cog_unload(self):
    self.bot.loop.create_task(self.stop_nodes())

  @commands.command(name='connect')
  async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
    if not channel:
      try:
        channel = ctx.author.voice.channel
      except AttributeError:
          raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

    player = self.bot.wavelink.get_player(ctx.guild.id)
    await ctx.send(f'Connecting to **`{channel.name}`**')
    try:
      await player.connect(channel.id)
    
    except Exception as e:
      await ctx.send(f"You forgot to give it permissions to join or some error occured. Error from the bot was {e}")
  
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
    try:
      await player.play(tracks[0])

    except Exception as e:
      await ctx.send(f"It likely can't play in this channel if this is a problem provide the error {e} to the owner thanks :D")

  @play.error
  async def play_error(self, ctx, error):
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

  @pause.error
  async def pause_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def resume(self,ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_paused:
      await player.set_pause(True)

  @resume.error
  async def resume_error(self, ctx, error):
    await ctx.send(error)

def setup(bot):
  bot.add_cog(Music(bot))