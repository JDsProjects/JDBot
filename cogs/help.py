from discord.ext import commands, menus
import discord

class MyHelp(commands.MinimalHelpCommand):
  async def send_pages(self):


    menu = menus.MenuPages(SendHelp(self.paginator.pages, per_page=1), delete_message_after=True)

    await menu.start(self.context)

class SendHelp(menus.ListPageSource):
  async def format_page(self, menu, item):
    
    item = discord.utils.escape_markdown(item)

    emby = discord.Embed(description= item , as_needed = True)
    return emby

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._original_help_command = bot.help_command
    self.bot.help_command = MyHelp()
    self.bot.help_command.cog = self

def cog_unload(self):
  self.help_command = self._original_help_command

def setup(client):
  client.add_cog(Help(client))
