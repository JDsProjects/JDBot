from discord.ext import commands
import discord, random, os, traceback, re
import utils
from discord.ext.menus.views import ViewMenuPages

class Events(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.Cog.listener('on_guild_join')
  async def guild_join_log(self, guild):
    channels = [channel for channel in guild.channels]
    roles = roles= [role for role in guild.roles]
    embed = discord.Embed(title = f"Bot just joined : {guild.name}", color=random.randint(0,16777215))
    
    embed.set_thumbnail(url = guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

    embed.add_field(name='Server Name:',value=f'{guild.name}')
    embed.add_field(name='Server ID:',value=f'{guild.id}')
    embed.add_field(name='Server region:',value=f'{guild.region}')
    embed.add_field(name='Server Creation Date:', value=f"{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}")
    embed.add_field(name='Server Owner:',value=f'{guild.owner}')
    embed.add_field(name='Server Owner ID:',value=f'{guild.owner_id}')
    embed.add_field(name='Member Count:',value=f'{guild.member_count}')
    embed.add_field(name='Amount of Channels:', value=f"{len(channels)}")
    embed.add_field(name='Amount of Roles:',value=f"{len(roles)}")
    await self.bot.get_channel(855217084710912050).send(embed=embed)

  @commands.Cog.listener('on_guild_remove')
  async def guild_remove_log(self, guild):
    channels = [channel for channel in guild.channels]
    roles = roles= [role for role in guild.roles]
    embed = discord.Embed(title = f"Bot just left : {guild.name}", color = random.randint(0,16777215))
    
    embed.set_thumbnail(url = guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

    embed.add_field(name = 'Server Name:', value = f'{guild.name}')
    embed.add_field(name = 'Server ID:', value = f'{guild.id}')

    try:
      embed.add_field(name = 'Server region:', value=f'{guild.region}')

    except:
      pass

    embed.add_field(name='Server Creation Date:', value=f"{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}")
    embed.add_field(name='Server Owner:',value=f'{guild.owner}')
    embed.add_field(name='Server Owner ID:',value=f'{guild.owner_id}')
    try:
      embed.add_field(name='Member Count:',value=f'{guild.member_count}')
    except:
      pass
    embed.add_field(name='Amount of Channels:',value=f"{len(channels)}")
    embed.add_field(name='Amount of Roles:',value=f"{len(roles)}")
    await self.bot.get_channel(855217084710912050).send(embed=embed)

  @commands.Cog.listener('on_ready')
  async def bot_startup(self):
    print("Bot is Ready")
    print(f"Logged in as {self.bot.user}")
    print(f"Id: {self.bot.user.id}")

  @commands.Cog.listener('on_message')
  async def message_checks(self, message):
    test = await self.bot.get_context(message)

    if message == "<@!347265035971854337>":
      await message.channel.send("My prefixes are `test*`, `te*`, `t*`, `jdbot.`, `jd.`, `test.`, and `te.`, you can use any of those prefixes for commands.")
    
    if isinstance(message.channel, discord.DMChannel):
      if test.prefix is None or self.bot.user.mentioned_in(message):
        if message.author.id != self.bot.user.id and test.valid is False:
          await message.channel.send("Ticket Support is coming soon. For now Contact our Developers: Shadi#9492 or JDJG Inc. Official#3493")

    if (test.valid) == False and test.prefix != None and test.command is None and test.prefix != "":
      
      embed_message = discord.Embed(title = f" {test.prefix}{test.invoked_with}", description = f"{discord.utils.format_dt(message.created_at, style = 'd')}{discord.utils.format_dt(message.created_at, style = 'T')}",color = random.randint(0, 16777215))

      embed_message.set_author(name=f"{message.author} tried to excute invalid command:", icon_url = (message.author.display_avatar.url))
      embed_message.set_footer(text = f"{message.author.id}")
      embed_message.set_thumbnail(url="https://i.imgur.com/bW6ergl.png")
      await self.bot.get_channel(855217084710912050).send(embed=embed_message)

    if re.fullmatch(rf"<@!?{self.bot.user.id}>", message.content):

      prefixes=await self.bot.get_prefix(message)
      pag = commands.Paginator()
      for p in prefixes:
        pag.add_line(f"{p}")

      pages = [page.strip("`") for page in pag.pages]

      menu = ViewMenuPages(utils.PrefixesEmbed(pages, per_page=1),delete_message_after=True)
      await menu.start(test)
  
<<<<<<< Updated upstream
  @commands.Cog.listener()
  async def on_error(event, *args, **kwargs):
=======
  @commands.Cog.listener('on_error')
  async def error_handler(event, *args, **kwargs):
    import traceback
>>>>>>> Stashed changes
    more_information=os.sys.exc_info()
    error_wanted=traceback.format_exc()
    traceback.print_exc()
    
    #print(more_information[0])

<<<<<<< Updated upstream
  #@commands.Cog.listener()
  #async def on_command_error(self, ctx, exception):

    #print(ctx)
    #print(exception)
    #traceback.print_exc()

    #wip and stuff, needs to check if something has a mini command handler, and such.

  @commands.Cog.listener()
  async def on_member_join(self, member):
=======
  @commands.Cog.listener('on_member_join')
  async def member_join_log(self, member):
>>>>>>> Stashed changes
    print(member)
    #currently wip btw

  @commands.Cog.listener('on_guild_available')
  async def guild_available_event(self, guild):
    print(f"{guild.name}({guild.id}) is avaible")

  @commands.Cog.listener('on_guild_unavailable')
  async def guild_unavailable_event(self, guild):
    print(f"{guild.name}({guild.id}) is unavaible")

def setup(bot):
  bot.add_cog(Events(bot))