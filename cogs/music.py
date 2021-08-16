from discord.ext import commands
import discord, wavelink, asyncio, os

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self.bot.loop.create_task(self.start_nodes())

  async def start_nodes(self):
    await self.bot.wait_until_ready()
    
    self.bot.wavelink = await wavelink.NodePool.create_node(bot = self.bot, host = os.environ["wavelink_host"], port = int(os.environ["wavelink_port"]), password = os.environ["wavelink_pass"], identifier = "JDBot", region = 'us_central')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
      print(f'Node: <{node.identifier}> is ready!')

  async def stop_nodes(self):
    await self.bot.wavelink.disconnect()

  def cog_unload(self):
    self.bot.loop.create_task(self.stop_nodes())

  @commands.command(name='connect')
  async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
    if not channel:
      try:
        channel = ctx.author.voice.channel
      except AttributeError:
          raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')

    player = self.bot.wavelink.get_player(ctx.guild)
    await ctx.send(f'Connecting to **`{channel.name}`**', allowed_mentions = discord.AllowedMentions.none())
    
    await player.connect(channel.id)

    bot_permissions = channel.permissions_for(ctx.guild.me)
    if not bot_permissions.connect:
      await ctx.send(f"You forgot to give it permissions to join the channel or some error occured.")
  
  @connect_.error
  async def connect_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def play(self, ctx, *, query: str):
    
    #Adding support for these options: https://mystb.in/AllahIeeeBroker
    
    tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{query}')

    if not tracks:
      return await ctx.send('Could not find any songs with that query.')

    player = self.bot.wavelink.get_player(ctx.guild.id)
    if not player.is_connected:
      await ctx.invoke(self.connect_)

    await ctx.send(f'Added {str(tracks[0])} to the queue.', allowed_mentions = discord.AllowedMentions.none())
    await player.play(tracks[0])

    channel = self.bot.get_channel(player.channel_id)
    bot_permissions = channel.permissions_for(ctx.guild.me)
    
    if not bot_permissions.speak:
      await ctx.send(f"It likely can't play in this channel(due to not having speaking perms).")

  @play.error
  async def play_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def force_disconnect(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    await player.destroy()

  @force_disconnect.error
  async def force_disconnect_error(self,ctx,error):
    await ctx.send(error)

  @commands.command(name="disconnect")
  async def disconnect_(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_connected:
      return await player.disconnect()

    if player.is_connected is False:
      await ctx.send("Can't Disconnect from no channels")

  @disconnect_.error
  async def disconnect_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def stop(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    await player.stop()

  @stop.error
  async def stop_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def pause(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_paused:
      await player.set_pause(False)
    
    if player.is_paused is False:
      await player.set_pause(True)

  @pause.error
  async def pause_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def resume(self, ctx):
    player = self.bot.wavelink.get_player(ctx.guild.id)
    if player.is_paused:
      await player.set_pause(True)

  @resume.error
  async def resume_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief = "lists the queue of items in the playlist", aliases = ["q"])
  async def queue(self, ctx):
    
    if ctx.guild:
      player = self.bot.wavelink.get_player(ctx.guild.id)

      if player.is_connected is False:
        return await ctx.send("Sorry, the bot isn't connected to player and there is no queue.")

      print(player.queue)

      await ctx.send("There's a problem with finding queue stuff rn. Hold on")

    if not ctx.guild:
      await ctx.send("There is no guild right now, either it's a DM or a guild is unavaible")

  @queue.error
  async def queue_error(self, ctx, error):
    await ctx.send(error)
  
def setup(bot):
  bot.add_cog(Music(bot))