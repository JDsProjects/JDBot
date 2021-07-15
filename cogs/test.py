from discord.ext import commands, menus
import discord, os, itertools, re, functools, typing, random, collections, io
import utils
from discord.ext.commands.cooldowns import BucketType

class Test(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ticket_make(self,ctx):
    await ctx.send("WIP, will make ticket soon..")

  @commands.command(brief="this command will error by sending no content")
  async def te(self, ctx):
    await ctx.send("this command will likely error...")
    await ctx.send("")

  @commands.command(brief = "WIP command to verify")
  async def verify(self, ctx):
    await ctx.send("WIP will make this soon..")

  async def cog_check(self, ctx):
    return ctx.author.id in self.bot.testers

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error
  
  @commands.command(brief = "a command to email you(work in progress)", help = "This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary")
  async def email(self, ctx, *args):
    print(args)
    await ctx.send("WIP")

  @commands.cooldown(1, 40, BucketType.user)
  @commands.command(brief = "a command that can scan urls(work in progress), and files", help = "please don't upload anything secret or send any secret url thank you :D")
  async def scan(self, ctx, *, args = None):
    await ctx.send("WIP")
    import vt
    vt_client = vt.Client(os.environ["virustotal_key"])
    used = None
    if args:
      used = True
      urls=re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",args)
      for u in urls:
        response = await vt_client.scan_url_async(u, wait_for_completion = True)
        print(response)

    if ctx.message.attachments:
      await ctx.send("If this takes a while, it probably means it was never on Virustotal before")
      used = True
    for f in ctx.message.attachments:
      analysis = await vt_client.scan_file_async(await f.read(),wait_for_completion = True)
      print(analysis)
      object_info = await vt_client.get_object_async("/analyses/{}", analysis.id)
    
    if used:
      await ctx.send(content="Scan completed")
    await vt_client.close_async()
    
  @commands.command(brief="work in progress")
  async def invert(self, ctx, Member: utils.BetterMemberConverter = None):
    Member = Member or ctx.author
    y = 0

    if ctx.message.attachments:
      for x in ctx.message.attachments:
        try:
          discord.utils._get_mime_type_for_image(await x.read())
          passes = True
        except commands.errors.CommandInvokeError:
          passes = False
        if passes is True:
          y += 1
          invert_time=functools.partial(utils.invert_func, await x.read())
          file = await self.bot.loop.run_in_executor(None, invert_time)
          await ctx.send(file=file)
        if passes is False:
          pass

    if not ctx.message.attachments or y == 0:
      url = Member.avatar_url_as(format="png")
      invert_time=functools.partial(utils.invert_func,await url.read() )

      file = await self.bot.loop.run_in_executor(None, invert_time)
      await ctx.send(file=file)

  @invert.error
  async def invert_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
  async def setprefix(self, ctx, *, arg = None):
    await ctx.send("WIP")

  @commands.command(brief = "WIP thing for birthday set up lol")
  async def birthday_setup(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief ="sleep time")
  async def set_sleeptime(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief = "wakeup time")
  async def set_wakeuptime(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief = "a command that takes a url and sees if it's an image.")
  async def image_check(self, ctx, *, args = None):
    if not args:
      return await ctx.send("please give args so it can do a url.")

  @commands.command(brief = "like other Bot info commands but more info?")
  async def about(self, ctx):
    await ctx.send("WIP for rn.")

  @commands.command(brief = "deletes a webhook by url")
  async def webhook_delete(self, ctx, *, args = None):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal
   
  @commands.command(brief = "tells you a webhook's avatar.")
  async def webhook_avatar(self, ctx, *, args = None):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "sees how compatitable something is(two things)")
  async def works(self, ctx, *args):

    if len(args) < 2:
      return await ctx.send("you didn't give me enough objects to checks the status of two items and make sure to have two objects.")

    item1 = args[0]
    item2 = args[-1]

    item_relationship = random.randint(1, 100)

    resp = "Place Holder"

    responses = ["They don't work well together at ALL :angry:", "They work quite poorly together...", "They work kinda good together, maybe", "They work REALLY good together, wow. Nice.", "Let them collaborate anytime."]

    import bisect

    breakpoints = [51, 70, 89, 100, 101]
    i = bisect.bisect(breakpoints, item_relationship)
    resp = responses[i]

    embed = discord.Embed(title = f"How well does {item1} and {item2} work together?",  description = f"They work at a rate {item_relationship}% \n**{resp}**", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_author(name=f"{ctx.author}", icon_url=(ctx.author.avatar_url))

    embed.set_footer(text = f"{ctx.author.id}")

    await ctx.send(embed = embed)

  @commands.command(brief = "sends tweet to JDBot Twitter")
  async def send_tweet(self, ctx, *, args = None):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "gets tweets from a username")
  async def tweet(self, ctx, *, args = None):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "add emoji to your guild lol")
  async def emoji_add(self, ctx):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "sends a emoji to me to review(a.k.a reviewed in the review channel)")
  async def emoji_save(self, ctx):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "runs something in le console")
  async def console(self, ctx):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal and other evals also well look at run commands too

  @commands.command(brief = "rips the source of commands by linking to the github.", name = "source")
  async def _source(self, ctx):
    
    await ctx.send("Eh okay, it's WIP btw.")

  #look at global_chat stuff for global_chat features, rank for well rank, add an update system too, add cc_ over. nick too, as well as kick and ban, ofc unban and other guild ban moderation stuff. Port over emoji_check but public and make that do it's best to upload less than 256 kB, try to freeze bot with suspend, or somehow, basically make it in unresponsive mode(maybe), and ofc an os emulation mode, as well as update mode, and nick.


  @commands.command(brief = "Gives info on pypi packages")
  async def npm(self, ctx, *, args = None):
    
    if args:
      npm_response=await self.bot.session.get(f"https://registry.npmjs.com/{args}")

      if npm_response.ok:

        npm_response = await npm_response.json()

        await ctx.send("WIP")

      else:
        await ctx.send(f"Could not find package **{args}** on npm.", allowed_mentions = discord.AllowedMentions.none())

    else:
      await ctx.send("Please look for a library to get the info of.")



def setup(bot):
  bot.add_cog(Test(bot))