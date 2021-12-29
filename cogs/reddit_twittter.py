from discord.ext import commands
import discord, os, tweepy, functools

class Twitter(commands.Cog):
  "Commands related to Twitter"
  def __init__(self, bot):
    self.bot = bot
  


def setup(bot):
  bot.add_cog(Twitter(bot))