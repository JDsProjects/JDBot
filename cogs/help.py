from discord.ext import commands, menus
import discord
from discord.ext.menus.views import ViewMenuPages

class MyHelp(commands.MinimalHelpCommand):
  async def send_pages(self):
    menu = ViewMenuPages(SendHelp(self.paginator.pages, per_page = 1), delete_message_after = True)

    await menu.start(self.context)

class SendHelp(menus.ListPageSource):
  async def format_page(self, menu, item):
    
    emby = discord.Embed(description = item, color = 15428885)
    return emby

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self._original_help_command = bot.help_command
    self.bot.help_command = MyHelp
    self.bot.help_command.cog = self

  async def cog_command_error(self, ctx, error):
    await ctx.send(error)
    import traceback
    traceback.print_exc()

def cog_unload(self):
  self.help_command = self._original_help_command

def setup(bot):
  bot.add_cog(Help(bot))
