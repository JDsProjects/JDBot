from discord.ext import commands
import utils

class JDBotHelp(commands.MinimalHelpCommand):
  async def send_pages(self):
    menu = utils.SendHelp(self.paginator.pages, ctx = self.context, delete_message_after = True)

    await menu.send(self.context.channel)

class Help(commands.Cog):
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
