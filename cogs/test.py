from discord.ext import commands
import discord, functools, typing, yarl, random
import utils
from discord.ext.commands.cooldowns import BucketType

import collections, io, itertools
from jishaku.codeblocks import codeblock_converter

import async_tio

class Test(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ticket_make(self, ctx):
    await ctx.send("WIP, will make ticket soon.. Please Contact the owner with the support command")

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
  
  @commands.command(brief="work in progress")
  async def invert(self, ctx, Member: utils.BetterMemberConverter = None):
    Member = Member or ctx.author
    passes = False

    if ctx.message.attachments:
      for x in ctx.message.attachments:
        try:
          discord.utils._get_mime_type_for_image(await x.read())
          passes = True
        except discord.errors.InvalidArgument:
          passes = False

        if passes:
          invert_time = functools.partial(utils.invert_func, await x.read())
          file = await self.bot.loop.run_in_executor(None, invert_time)
          return await ctx.send(file = file)

    if not ctx.message.attachments or not passes:
      url = (Member.display_avatar.replace(format = "png"))
      invert_time = functools.partial(utils.invert_func, await url.read() )

      file = await self.bot.loop.run_in_executor(None, invert_time)
      await ctx.send(file = file)

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
  async def image_check(self, ctx, *, args : typing.Union[yarl.URL, str] = None):
    if not args:
      return await ctx.send("please give args so it can do a url.")

    if isinstance(args , yarl.URL):
      await ctx.send("Got a url :D")

    if isinstance(args , str):
      await ctx.send("got a string can't do much with it though.")

  @commands.command(brief = "gets tweets from a username")
  async def tweet(self, ctx, *, args = None):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "add emoji to your guild lol")
  async def emoji_add(self, ctx):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal  

 
  @commands.command(brief = "runs some code in a sandbox(based on Soos's Run command)", aliases = ["eval", "run",])
  async def console(self, ctx, *, code: codeblock_converter = None):

    if not code:
      return await ctx.send("You need to give me some code to use, otherwise I can not determine what it is.")

    #look at the JDJG Bot orginal and other evals also well look at run commands too

    if not code.language:
      return await ctx.send("You Must provide a language to use")

    if not code.content:
      return await ctx.send("No code provided")

    tio = await async_tio.Tio(session = self.bot.session)

    output = await tio.execute(f"{code.content}", language = f"{code.language}")

    print(output)

  #okay hold on: https://github.com/soosBot-com/soosBot/blob/bb544e4c702d8bc444a21eb6a6802c685a463001/extensions/programming.py#L10
  

  @commands.command(brief = "finds out where the location of the command on my github repo(so people can learn from my commands)", name = "source")
  async def _source(self, ctx, *, command = None):
    github_url = "https://github.com/JDJGInc/JDBot"
    
    if command is None:

      embed = discord.Embed(title = "Github link", description = f"{github_url}", color = 15428885, timestamp = ctx.message.created_at)
      await ctx.send("Here's the github link:", embed = embed)

    await ctx.send(f"finding out where the command is located is not around yet.")

  @commands.command(brief = "Gives info on pypi packages")
  async def npm(self, ctx, *, args = None):
    
    if args:
      npm_response = await self.bot.session.get(f"https://registry.npmjs.com/{args}")

      if npm_response.ok:
        npm_response = await npm_response.json()

        await ctx.send("WIP")

      else:
        await ctx.send(f"Could not find package **{args}** on npm.", allowed_mentions = discord.AllowedMentions.none())

    else:
      await ctx.send("Please look for a library to get the info of.")

  @commands.command(brief = "sends a gif of someone dancing to disco (animated)")
  async def disco(self, ctx):
    await ctx.send("WIP alright?")

  @commands.command(brief = "sends a gif of someone dancing to all but disco(animated)")
  async def dance(self, ctx):
    await ctx.send("WIP alright?")

  @commands.command(brief = "scans statuses to see if there is any bad ones.")
  async def scan_status(self, ctx):
    await ctx.send("will scan statuses in a guild to see if there is a bad one.")

  @commands.command(brief = "sets logs for a guild", name = "logging")
  async def _logging(self, ctx):
    await ctx.send("logging wip.")

  #look at global_chat stuff for global_chat features, rank for well rank, add an update system too, add cc_ over. nick too, as well as kick and ban, ofc unban and other guild ban moderation stuff. Port over emoji_check but public and make that do it's best to upload less than 256 kB, try to and ofc an os emulation mode, as well as update mode, and nick.
  
  #make the bot be able to lock commands to owners only, for testing purposes or not respond to commands.

  #Unrelated to Urban:
  #https://discordpy.readthedocs.io/en/master/api.html?highlight=interaction#discord.InteractionResponse.send_message
  #https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild.query_members

  #guild_prefixes table in my sql database
  #spyco data table in my sql database
  #Job_data in sql database
  #yes format will come later.

  @commands.command(brief = "trivia test")
  async def test_select(self, ctx):
    view = utils.gameChoice(ctx)
    await ctx.send("test time...", view = view)

class Slash(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief = "says hi to you", slash_command = False)
  async def hi(self, ctx):
    await ctx.send(f"hi {ctx.author}")


def setup(bot):
  bot.add_cog(Test(bot))
  bot.add_cog(Slash(bot))