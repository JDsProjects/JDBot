from discord.ext import commands
import discord
from discord.ext import menus

#class MyHelp(commands.MinimalHelpCommand):
#async def send_bot_help(self,mapping):
#channel = self.get_destination()
  

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._original_help_command = bot.help_command
    #self.bot.help_command = MyHelp()
    self.bot.help_command.cog = self

def cog_unload(self):
  self.t.help_command = self._original_help_command

def setup(client):
  client.add_cog(Help(client))
