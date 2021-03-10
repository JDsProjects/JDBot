from discord.ext import commands
from utils import BetterMemberConverter, BetterUserconverter
import random
import discord

class Owner(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(brief="a command to send mail")
  async def mail(self,ctx,*,user: BetterUserconverter=None):
    if user is None:
      await ctx.reply("User not found, returning Letter")
      user = ctx.author
    if user:
      def check(m):
        return m.author.id == ctx.author.id
      await ctx.reply("Please give me a message to use.")
      message = await self.client.wait_for("message",check=check)
      embed_message = discord.Embed(title=message.content, timestamp=(message.created_at), color=random.randint(0, 16777215))
      embed_message.set_author(name=f"Mail from: {ctx.author}",icon_url=(ctx.author.avatar_url))
      embed_message.set_footer(text = f"{ctx.author.id}")
      embed_message.set_thumbnail(url = "https://i.imgur.com/1XvDnqC.png")
      if (user.dm_channel is None):
        await user.create_dm()
      try:
        await user.send(embed=embed_message)
      except:
        user = ctx.author
        await user.send(content="Message failed. sending",embed=embed_message)
        embed_message.add_field(name="Sent To:",value=str(user))
      await self.client.get_channel(738912143679946783).send(embed=embed_message)

  async def cog_check(self, ctx):
    return await self.client.is_owner(ctx.author)

def setup(client):
  client.add_cog(Owner(client))
