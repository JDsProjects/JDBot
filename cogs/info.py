from discord.ext import commands, menus
import re, discord , random , mystbin , typing, emoji, unicodedata, textwrap
import utils
from difflib import SequenceMatcher
from discord.ext.commands.cooldowns import BucketType
from doc_search import AsyncScraper

class Info(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help="gives you info about a guild",aliases=["server_info","guild_fetch","guild_info","fetch_guild","guildinfo",])
  async def serverinfo(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
    guild = guild or ctx.guild

    if guild is None:
      await ctx.send("Guild wanted has not been found")
    
    if guild:
      await utils.guildinfo(ctx,guild)

  @commands.command(aliases=["user_info","user-info"],brief="a command that gives information on users",help="this can work with mentions, ids, usernames, and even full names.")
  async def userinfo(self, ctx, *, user: utils.BetterUserconverter = None):
    user = user or ctx.author
    user_type = ['User', 'Bot'][user.bot]
    
    if ctx.guild:
      member_version=ctx.guild.get_member(user.id)
      if member_version:
        nickname = str(member_version.nick)
        joined_guild = member_version.joined_at.strftime('%m/%d/%Y %H:%M:%S')
        status = str(member_version.status).upper()
        highest_role = member_version.roles[-1]
      if not member_version:
        nickname = str(member_version)
        joined_guild = "N/A"
        status = "Unknown"
        for guild in self.bot.guilds:
          member=guild.get_member(user.id)
          if member:
            status=str(member.status).upper()
            break
            
        highest_role = "None Found"
    if not ctx.guild:
        nickname = "None"
        joined_guild = "N/A"
        status = "Unknown"
        for guild in self.bot.guilds:
          member=guild.get_member(user.id)
          if member:
            status=str(member.status).upper()
            break
        highest_role = "None Found"
    
    guilds_list=[guild for guild in self.bot.guilds if guild.get_member(user.id) and guild.get_member(ctx.author.id)]
    if not guilds_list:
      guild_list = "None"

    if guilds_list:
      guild_list= ", ".join(map(str, guilds_list))

    embed=discord.Embed(title=f"{user}",description=f"Type: {user_type}", color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
    embed.add_field(name="Username: ", value = user.name)
    embed.add_field(name="Discriminator:",value=user.discriminator)
    embed.add_field(name="Nickname: ", value = nickname)
    embed.add_field(name="Joined Discord: ",value = (user.created_at.strftime('%m/%d/%Y %H:%M:%S')))
    embed.add_field(name="Joined Guild: ",value = joined_guild)
    embed.add_field(name="Mutual Guilds:", value=guild_list)
    embed.add_field(name="ID:",value=user.id)
    embed.add_field(name="Status:",value=status)
    embed.add_field(name="Highest Role:",value=highest_role)
    embed.set_image(url=user.avatar_url)
    await ctx.send(embed=embed)

  @commands.command(brief="uploads your emojis into a mystbin link")
  async def look_at(self,ctx):
    if isinstance(ctx.message.channel, discord.TextChannel):
      message_emojis = ""
      for x in ctx.guild.emojis:
        message_emojis = message_emojis+" "+str(x)+"\n"
      mystbin_client = mystbin.Client(session=self.client.session)
      paste = await mystbin_client.post(message_emojis)
      await ctx.send(paste.url)
      
    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("We can't use that in DMS")

  @commands.command(help="gives the id of the current guild or DM if you are in one.")
  async def guild_get(self,ctx):
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=ctx.guild.id) 

    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send(ctx.channel.id)

  @commands.command(brief="a command to tell you the channel id")
  async def this(self,ctx):
    await ctx.send(ctx.channel.id)

  @commands.cooldown(1,30,BucketType.user)
  @commands.command(help="fetch invite details")
  async def fetch_invite(self,ctx,*invites:typing.Union[discord.Invite, str]):
    if len(invites) > 0:
      menu = menus.MenuPages(utils.InviteInfoEmbed(invites, per_page=1),delete_message_after=True)
      await menu.start(ctx)
    if len(invites) < 1:
      await ctx.send("Please get actual invites to attempt grab")

    if len(invites) > 50:
      await ctx.send("Reporting using more than 50 invites in this command. This is to prevent ratelimits with the api.")

      jdjg = self.bot.get_user(168422909482762240) or await self.bot.fetch_user(168422909482762240)
      await self.bot.get_channel(738912143679946783).send(f"{jdjg.mention}.\n{ctx.author} causes a ratelimit issue with {len(invites)} invites")

  @fetch_invite.error
  async def fetch_invite_error(self,ctx,error):
    await ctx.send(error)

  @commands.command(brief="gives info about a file")
  async def file(self,ctx):
    if len(ctx.message.attachments) < 1:
      await ctx.send(ctx.message.attachments)
      await ctx.send("no file submitted")
    if len(ctx.message.attachments) > 0:
      embed = discord.Embed(title="Attachment info",color=random.randint(0, 16777215))
      for x in ctx.message.attachments:
        embed.add_field(name=f"ID: {x.id}",value=f"[{x.filename}]({x.url})")
        embed.set_footer(text="Check on the url/urls to get a direct download to the url.")
      await ctx.send(embed=embed,content="\nThat's good")

  @commands.command(brief="a command to get the avatar of a user",help="using the userinfo technology it now powers avatar grabbing.",aliases=["pfp","av"])
  async def avatar(self,ctx,*,user: utils.BetterUserconverter = None): 
    user = user or ctx.author
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{user.name}'s avatar:",icon_url=(user.avatar_url))
    embed.set_image(url=(user.avatar_url))
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

  @commands.command(brief="this is a way to get the nearest channel.")
  async def closest_channel(self,ctx,*,args=None):
    if args is None:
      await ctx.send("Please specify a channel")
    
    if args:
      if isinstance(ctx.channel, discord.TextChannel):
        channel=discord.utils.get(ctx.guild.channels,name=args)
        if channel:
          await ctx.send(channel.mention)
        if channel is None:
          await ctx.send("Unforantely we haven't found anything")

      if isinstance(ctx.channel,discord.DMChannel):
        await ctx.send("You can't use it in a DM.")

  @commands.command(brief="a command to get the closest user.")
  async def closest_user(self,ctx,*,args=None):
    if args is None:
      await ctx.send("please specify a user")
    if args:
      userNearest = discord.utils.get(self.bot.users,name=args)
      user_nick = discord.utils.get(self.bot.users,display_name=args)
      if userNearest is None:
        userNearest = sorted(self.bot.users, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]
      if user_nick is None:
        user_nick = sorted(self.bot.users, key=lambda x: SequenceMatcher(None, x.display_name,args).ratio())[-1]
      await ctx.send(f"Username: {userNearest}")
      await ctx.send(f"Display name: {user_nick}")
    
    if isinstance(ctx.channel, discord.TextChannel):
      member_list = [x for x in ctx.guild.members if x.nick]
      
      nearest_server_nick = sorted(member_list, key=lambda x: SequenceMatcher(None, x.nick,args).ratio())[-1] 
      await ctx.send(f"Nickname: {nearest_server_nick}")

    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("You unforantely don't get the last value.")
  
  @commands.command(help="gives info on default emoji and custom emojis",name="emoji")
  async def emoji_info(self,ctx,*emojis: typing.Union[utils.EmojiConverter ,str]):
    if len(emojis) > 0:
      menu = menus.MenuPages(utils.EmojiInfoEmbed(emojis, per_page=1),delete_message_after=True)
      await menu.start(ctx)
    if len(emojis) < 1:
      await ctx.send("Looks like there was no emojis.")

  @commands.command()
  async def fetch_content(self, ctx, *, args = None):
    if args is None:
      await ctx.send("please send actual text")
    if args:
      args=discord.utils.escape_mentions(args)
      args=discord.utils.escape_markdown(args,as_needed=False,ignore_links=False)
    for x in ctx.message.mentions:
      args = args.replace(x.mention,f"\{x.mention}")
    emojis=emoji.emoji_lis(args)
    emojis_return = [d["emoji"] for d in emojis]
    for x in emojis_return:
      args = args.replace(x,f"\{x}")
    for x in re.findall(r':\w*:\d*',args):
        args=args.replace(x,f"\{x}")
    await ctx.send(f"{args}")


class DevTools(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    bot.loop.create_task(self.__ainit__())
  
  async def __ainit__(self):
    await self.bot.wait_until_ready()

    self.scraper = AsyncScraper(session = self.bot.session)

  async def rtfm_lookup(self, program = None, *, args = None):
    
    rtfm_dictionary = {
      "latest": "https://discordpy.readthedocs.io/en/latest",
      "latest-jp": "https://discordpy.readthedocs.io/ja/latest",
      "python": "https://docs.python.org/3",
      "python-jp": "https://docs.python.org/ja/3",
      "master": "https://discordpy.readthedocs.io/en/master",
      "jishaku" : "https://jishaku.readthedocs.io/en/latest",
      "asyncpg" : "https://magicstack.github.io/asyncpg/current",
      "tweepy" : "https://docs.tweepy.org/en/latest/",
      "aiogifs" : "https://aiogifs.readthedocs.io/en/latest/",
      "python-cse" : "https://python-cse.readthedocs.io/en/latest/",
      "wavelink" : "https://wavelink.readthedocs.io/en/latest/",
      "motor" : "https://motor.readthedocs.io/en/stable/",
      "motor-latest" : "https://motor.readthedocs.io/en/latest/",
      "dagpi" : "https://asyncdagpi.readthedocs.io/en/latest/",
      "pymongo" : "https://pymongo.readthedocs.io/en/stable/",
      "pymongo-latest" : "https://pymongo.readthedocs.io/en/latest/",
      "aiohttp" : "https://docs.aiohttp.org/en/stable/",
      "aiohttp-latest" : "https://docs.aiohttp.org/en/latest/",
      "wand" : "https://docs.wand-py.org/en/stable/",
      "pillow" : "https://pillow.readthedocs.io/en/stable/",
      "aiosqlite" : "https://aiosqlite.omnilib.dev/en/stable/",
      "pytube" : "https://pytube.io/en/latest/",

      }

    if not args:
      return rtfm_dictionary.get(program)

    else:
      url = rtfm_dictionary.get(program)

      results = await self.scraper.search(args, page=url)

      if not results:
        return f"Could not find anything with {args}."

      else:
        return results

  async def rtfm_send(self, ctx, results):

    if isinstance(results, str):
      await ctx.send(results, allowed_mentions = discord.AllowedMentions.none())

    else: 
      embed = discord.Embed(color = random.randint(0, 16777215))

      results = results[:10]
      embed.description = "\n".join(f"[`{result}`]({value})" for result, value in results)

      reference = utils.reference(ctx.message)
      await ctx.send(embed=embed, reference = reference)


  @commands.group(aliases=["rtd"], invoke_without_command = True, brief="most of this is based on R.danny including the reference. But it's my own implentation of it")
  async def rtfm(self, ctx, *, args = None):

    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="latest", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command using japanese discord.py (based on R.danny's command")
  async def jp(self, ctx, *, args = None):

    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="latest-jp", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to lookup stuff from python3 docs based on R.danny's command", aliases=["py"])
  async def python(self, ctx, *, args = None):

    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="python", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to lookup stuff from python3 docs based on R.danny's command(japanese)", aliases=["py-ja"], name="py-jp")
  async def python_jp(self, ctx, *, args = None):

    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="python-jp", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to lookup stuff from newer discord.py a.k.a newer version.")
  async def master(self, ctx, *, args = None):
    
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="master", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief="a command to look up stuff from jishaku", aliases=["jsk"])
  async def jishaku(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="jishaku", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse stuff from asyncpg")
  async def asyncpg(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="asyncpg", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief= "a command to parse from tweepy")
  async def tweepy(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="tweepy", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from aiogifs")
  async def aiogifs(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="aiogifs", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from python-cse",name="python-cse")
  async def python_cse(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="python-cse", args = args)
    await self.rtfm_send(ctx, results)
  
  @rtfm.command(brief = "a command to parse from wavelink")
  async def wavelink(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="wavelink", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.group(invoke_without_command = True, brief = "look up parser for motor")
  async def motor(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="motor", args = args)
    await self.rtfm_send(ctx, results)

  @motor.command(brief = "a command to parse from motor latest")
  async def latest(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="motor-latest", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from dagpi")
  async def dagpi(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="dagpi", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.group(brief = "a command to parse from pymongo", invoke_without_command = True)
  async def pymongo(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="pymongo", args = args)
    await self.rtfm_send(ctx, results)

  @pymongo.command(brief = "a command to parse from pymongo latest", name="latest")
  async def pymongo_latest(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="pymongo-latest", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.group(brief = "a command to parse from aiohttp", invoke_without_command = True)
  async def aiohttp(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="aiohttp", args = args)
    await self.rtfm_send(ctx, results)

  @aiohttp.command(brief = "a command to parse from aiohttp latest", name="latest")
  async def aiohttp_latest(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="aiohttp-latest", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from wand")
  async def wand(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="wand", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from pillow")
  async def pillow(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="pillow", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from aiosqlite")
  async def aiosqlite(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="aiosqlite", args = args)
    await self.rtfm_send(ctx, results)

  @rtfm.command(brief = "a command to parse from pytube")
  async def pytube(self, ctx, *, args = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="pytube", args = args)
    await self.rtfm_send(ctx, results)

  def charinfo_converter(self, string):
    digit = f"{ord(string):x}"
    name = unicodedata.name(string, "The unicode was not found")
    return f"`\\U{digit:>08}`: {name} - {string} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"

  @commands.command(brief = "Gives you data about charinfo (based on R.danny's command)")
  async def charinfo(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("That doesn't help out all :(")
    
    values = '\n'.join(map(self.charinfo_converter, set(args))) 

    content = textwrap.wrap(values, width=2000)

    menu = menus.MenuPages(utils.charinfoMenu(content, per_page=1),delete_message_after=True)

    await menu.start(ctx)
   

def setup(bot):
  bot.add_cog(Info(bot))
  bot.add_cog(DevTools(bot))