from discord.ext import commands as Commands
import utils
import itertools

class JDBotHelp(Commands.MinimalHelpCommand):
  async def send_pages(self):
    menu = utils.SendHelp(self.paginator.pages, ctx = self.context, delete_message_after = True)

    await menu.send(self.context.channel)

  def add_bot_commands_formatting(self, heading):
    self.paginator.add_line(f'**{heading}**')

  async def send_bot_help(self, mapping):
    ctx = self.context
    bot = ctx.bot

    if bot.description:
      self.paginator.add_line(bot.description, empty = True)

    note = self.get_opening_note()

    if note:
      self.paginator.add_line(note, empty=True)

    no_category = f'\u200b{self.no_category}'

    def get_category(command, *, no_category=no_category):
      cog = command.cog
      return cog.qualified_name if cog is not None else no_category

    filtered = await self.filter_commands(bot.commands, sort = True, key=get_category)
    to_iterate = itertools.groupby(filtered, key=get_category)

    for category, commands in to_iterate:
      self.add_bot_commands_formatting(category)

    note = self.get_ending_note()
    if note:
      self.paginator.add_line()
      self.paginator.add_line(note)

    await self.send_pages()
      

class Help(Commands.Cog):
  "The Help Menu Cog"
  def __init__(self, bot):
    self.bot = bot
    self._original_help_command = bot.help_command
    self.bot.help_command = JDBotHelp()
    self.bot.help_command.cog = self

def cog_unload(self):
  self.help_command = self._original_help_command

def setup(bot):
  bot.add_cog(Help(bot))
