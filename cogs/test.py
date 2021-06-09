from discord.ext import commands
import discord, os, itertools, re, functools, typing, random, collections, io
import utils

testers_list =  [652910142534320148,524916724223705108,168422909482762240,742214686144987150,813445268624244778,700210850513944576,717822288375971900,218481166142013450,703674286711373914]

class Test(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ticket_make(self,ctx):
    await ctx.send("WIP, will make ticket soon..")

  @commands.command()
  async def pypi(self,ctx,*,args=None):
    #https://pypi.org/simple/
    if args:
      pypi_response=await self.bot.session.get(f"https://pypi.org/pypi/{args}/json")
      if pypi_response.ok:
        print(await pypi_response.json())
      else:
        await ctx.send(f"Could not find package **{args}** on pypi.")

    else:
      await ctx.send("Please look for a library to get the info of.")


  @commands.command()
  async def emoji_id(self,ctx,*, emoji: utils.EmojiBasic=None):
    if emoji:
      embed = discord.Embed(description=f" Emoji ID: {emoji.id}",color=random.randint(0, 16777215))
      embed.set_image(url=emoji.url)
      await ctx.send(embed=embed)

    else:
      await ctx.send("Not a valid emoji id.")

  @commands.command(brief="this command will error by sending no content")
  async def te(self, ctx):
    await ctx.send("")

  async def cog_check(self, ctx):
    return ctx.author.id in testers_list

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      
    #I need to fix all cog_command_error
  
  @commands.command(brief="a command to email you(work in progress)",help="This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary")
  async def email(self,ctx,*args):
    print(args)
    await ctx.send("WIP")

  @commands.command(brief="a command that can scan urls(work in progress), and files",help="please don't upload anything secret or send any secret url thank you :D")
  async def scan(self,ctx, *, args = None):
    await ctx.send("WIP")
    import vt
    vt_client = vt.Client(os.environ["virustotal_key"])
    used = None
    if args:
      used = True
      urls=re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",args)
      for x in urls:
        print(x)

    if len(ctx.message.attachments) > 0:
      await ctx.send("If this takes a while, it probably means it was never on Virustotal before")
      used = True
    for x in ctx.message.attachments:
      analysis = await vt_client.scan_file_async(await x.read(),wait_for_completion=True)
      object_info = await vt_client.get_object_async("/analyses/{}", analysis.id)
    
    if used:
      await ctx.send(content="Scan completed")
    await vt_client.close_async()
    
  @commands.command(brief="work in progress")
  async def invert(self,ctx):
    y = 0

    if len(ctx.message.attachments) > 0:
      for x in ctx.message.attachments:
        try:
          discord.utils._get_mime_type_for_image(await x.read())
          passes = True
        except commands.errors.CommandInvokeError:
          passes = False
        if passes is True:
          y += 1
          invert_time=functools.partial(utils.invert_func,await x.read())
          file = await self.bot.loop.run_in_executor(None, invert_time)
          await ctx.send(file=file)
        if passes is False:
          pass

    if len(ctx.message.attachments) == 0 or y == 0:
      url = ctx.author.avatar_url_as(format="png")
      invert_time=functools.partial(utils.invert_func,await url.read() )

      file = await self.bot.loop.run_in_executor(None, invert_time)
      await ctx.send(file=file)

  @invert.error
  async def invert_error(self,ctx,error):
    await ctx.send(error)

  async def quick_convert(self, *emojis: typing.Union[discord.PartialEmoji , str]):
    return emojis

  @commands.command()
  async def emoji_dump(self,ctx):
    await ctx.send("emoji dump time.")
    import mystbin
    mystbin_client = mystbin.Client(session=self.bot.session)

    paste=await mystbin_client.get("https://mystb.in/CompetingGlobeParental")
    paste2 = await mystbin_client.get("https://mystb.in/PersianMentalMission")
    paste3 = await mystbin_client.get("https://mystb.in/FoldingTherapeuticPlain")
    paste4 = await mystbin_client.get("https://mystb.in/OrangePrintableSeven")

    list_results= await self.quick_convert(paste.paste_content.replace("\n"," "))+await self.quick_convert(paste2.paste_content.replace("\n"," "))+await self.quick_convert(paste3.paste_content.replace("\n"," "))+await self.quick_convert(paste4.paste_content.replace("\n"," "))
    for x in list_results:
      print(f"\n{x}")

    #webhook=await ctx.channel.create_webhook(name="emoji dump")

  @commands.command(brief="Lists the current used prefix",aliases=["prefix"])
  async def currentprefix(self,ctx):
    await ctx.send(f"{ctx.prefix}")

  @commands.command(brief="Lists the current prefixes that could be used.")
  async def prefixes(self,ctx):
    prefixes=await self.bot.get_prefix(ctx.message)
    await ctx.send(f"{prefixes}")

  @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
  async def setprefix(self,ctx,arg=None):
    await ctx.send("WIP")

  @commands.command()
  async def letsnot(self,ctx):
    emoji=discord.utils.get(self.bot.emojis,name="commandfail")
    await ctx.send(f"Let's not go like {emoji} instead let's try to be nice about this. \nGet a copy of this image from imgur: https://i.imgur.com/CykdOIz.png")

def setup(client):
  client.add_cog(Test(client))