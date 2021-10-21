from discord.ext import commands
import discord, functools, typing, yarl, random
import utils
from discord.ext.commands.cooldowns import BucketType

#collections, io, itertools

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

  @commands.command(brief = "runs something in le console", aliases = ["eval"])
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

  class RpsGame(discord.ui.View):
    def __init__(self, authorized_user: typing.Union[discord.User, discord.Member] = None, **kwargs):
      super().__init__(**kwargs)
      self.authorized_user = authorized_user
      self.value: str = None
  
    def __authorized__(self, button: discord.ui.Button, interaction: discord.Interaction) -> bool:
      if self.authorized_user and self.authorized_user.id != interaction.user.id:
        return False

      return True

    @discord.ui.button(label = "Rock", style = discord.ButtonStyle.success, emoji = "🪨")
    async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):
      if not self.__authorized__(button, interaction):

        return await interaction.response.send_message(content = f"You Can't play this game, {self.authorized_user.mention} is the user playing this game.", ephemeral = True)

      self.clear_items()
      await interaction.response.edit_message(view = self)
      self.value = 1
      self.stop()

    @discord.ui.button(label="Paper", style = discord.ButtonStyle.success , emoji = "📰")
    async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):
      if not self.__authorized__(button, interaction):
        return await interaction.response.send_message(content = f"You Can't play this game, {self.authorized_user.mention} is the user playing this game.", ephemeral = True)

      self.clear_items()
      await interaction.response.edit_message(view = self)
      self.value = 2
      self.stop()

    @discord.ui.button(label="scissors", style = discord.ButtonStyle.success , emoji = "✂️")
    async def scissors(self, button: discord.ui.Button, interaction: discord.Interaction):
      if not self.__authorized__(button, interaction):
        return await interaction.response.send_message(content = f"You Can't play this game, {self.authorized_user.mention} is the user playing this game.", ephemeral = True)

      self.clear_items()
      await interaction.response.edit_message(view = self)
      self.value = 3
      self.stop()


  @commands.command(brief = "a nice rock scissors paper game")
  async def rps(self, ctx):
    view = self.RpsGame(ctx.author, timeout = 5.00)
    message = await ctx.send(" Rock paper Scissors Shoot.", view = view)

    await view.wait()

    if view.value is None:
      await message.edit("You didn't respond fast enough, you lost.")
    
    deciding = random.randint(1, 3)
    number_to_text = {1 : "rock", 2 : "paper", 3 : "scissors"}

    if view.value == deciding:
      await message.edit(f"a Tie occured. with you picking {number_to_text[view.value]} And the bot with {number_to_text[deciding]}")

    


class Slash(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  #@commands.command(brief = "addes a slash command to a guild", slash_command = True)
  #async def wip(self, ctx):
    #await ctx.send("this is a way to test slash commands")


def setup(bot):
  bot.add_cog(Test(bot))
  bot.add_cog(Slash(bot))