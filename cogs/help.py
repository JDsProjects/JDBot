from discord.ext import commands
import discord

class MyHelp(commands.MinimalHelpCommand):
  async def send_command_help(self, command):
    embed = discord.Embed(title=self.get_command_signature(command))
    embed.add_field(name="Help", value=command.help)
    alias = command.aliases
    if alias:
      embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

    channel = self.get_destination()
    await channel.send(embed=embed)

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    #self._original_help_command = bot.help_command
    #self.bot.help_command = MyHelp()
    #self.bot.help_command.cog = self

def cog_unload(self):
  self.t.help_command = self._original_help_command

def setup(client):
  client.add_cog(Help(client))
