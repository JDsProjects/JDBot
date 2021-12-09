from discord.ext import commands
import discord, typing, random
import utils
from discord.ext.commands.cooldowns import BucketType

import collections, itertools
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

  #Refer to this: https://github.com/soosBot-com/soosBot/blob/bb544e4c702d8bc444a21eb6a6802c685a463001/extensions/programming.py#L17
  #https://github.com/Tom-the-Bomb/async-tio

  @commands.command(brief = "finds out where the location of the command on my github repo(so people can learn from my commands)", name = "source")
  async def _source(self, ctx, *, command = None):
    github_url = "https://github.com/JDJGInc/JDBot"
    
    if command is None:

      embed = discord.Embed(title = "Github link", description = f"{github_url}", color = 15428885, timestamp = ctx.message.created_at)
      await ctx.send("Here's the github link:", embed = embed)

    await ctx.send(f"finding out where the command is located is not around yet.")

  @commands.command(brief = "Gives info on npm packages")
  async def npm(self, ctx, *, args = None):
    
    if args:
      npm_response = await self.bot.session.get(f"https://registry.npmjs.com/{args}")

      if npm_response.ok:
        npm_response = await npm_response.json()

        data = utils.get_required_npm(npm_response)
        await ctx.send(embed = utils.npm_create_embed(data))

      else:
        await ctx.send(f"Could not find package **{args}** on npm.", allowed_mentions = discord.AllowedMentions.none())

    else:
      await ctx.send("Please look for a library to get the info of.")

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
  #jobs for you to do will come later.

  class Pagination(discord.ui.View):
    def __init__(self, ctx, **kwargs):
      super().__init__(**kwargs)
      self.ctx = ctx
      #going to use https://github.com/oliver-ni/discord-ext-menus-views/blob/master/discord/ext/menus/views/__init__.py as a small check on how the interaction checks work for menus and the buttons, but otherwise the rest will be handled by me.
      #This is a reference.
    
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