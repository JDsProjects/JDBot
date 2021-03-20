import discord
from discord.ext import commands
from utils import BetterMemberConverter, BetterUserconverter
import asuna_api
import random
import sr_api
from utils import triggered_converter, headpat_converter

class Image(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(brief="a command to slap someone",help="this sends a slap gif to the target user")
  async def slap(self,ctx,*, Member: BetterMemberConverter = None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
    
    asuna = asuna_api.Client()
    url = await asuna.get_gif("slap")
    await asuna.close()

    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} slapped you! Ow...",icon_url=(person.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="powered using the asuna.ga api")

    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed DM'ing them...")

  @commands.command(brief="a command to look up foxes",help="this known as wholesome fox to the asuna api")
  async def fox2(self,ctx):
    asuna = asuna_api.Client()
    url = await asuna.get_gif("wholesome_foxes")
    await asuna.close()
    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{ctx.author} requested a wholesome fox picture",icon_url=(ctx.author.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="powered using the asuna.ga api")
    await ctx.send(embed=embed)

  
  @commands.command(brief="another command to give you pat gifs",help="powered using the asuna api")
  async def pat2(self,ctx,*, Member: BetterMemberConverter= None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
    
    asuna = asuna_api.Client()
    url = await asuna.get_gif("pat")
    await asuna.close()

    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} patted you! *pat pat pat*",icon_url=(person.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="powered using the asuna.ga api")
    
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed DM'ing them...")

  @commands.command(brief="a command to give you pat gifs",help="using the sra api it gives you pat gifs")
  async def pat(self,ctx,*, Member: BetterMemberConverter=None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
      
    sr_client=sr_api.Client()
    image=await sr_client.get_gif("pat")
    await sr_client.close()
    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} patted you",icon_url=(person.avatar_url))
    embed.set_image(url=image.url)
    embed.set_footer(text="powered by some random api")
      
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed Dming them...")
  

  @commands.command(brief="a hug command to hug people",help="this the first command to hug.")
  async def hug(self,ctx,*, Member: BetterMemberConverter=None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member

    sr_client=sr_api.Client()
    image=await sr_client.get_gif("hug")
    await sr_client.close()

    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} hugged you! Awwww...",icon_url=(person.avatar_url))
    embed.set_image(url=image.url)
    embed.set_footer(text="powered by some random api")
    
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed DM'ing them...")
  
  @commands.command(help="takes a .png attachment or your avatar and makes a triggered version.")
  async def triggered(self,ctx):
    y = 0
    if len(ctx.message.attachments) > 0:
      for x in ctx.message.attachments:
        if x.filename.endswith(".png"):
          url = x.url
          await triggered_converter(url,ctx)
          y = y + 1
        if not x.filename.endswith(".png"):
          pass

    if len(ctx.message.attachments) == 0 or y == 0:
      url = ctx.author.avatar_url_as(format="png")
      await triggered_converter(url,ctx)

  @commands.command(brief="uses our headpat program to pat you",help="a command that uses sra_api to make a headpat of you.")
  async def headpat2(self,ctx):
    y = 0
    if len(ctx.message.attachments) > 0:
      for x in ctx.message.attachments:
        if x.filename.endswith(".png"):
          url = x.url
          await headpat_converter(url,ctx)
          y = y + 1
        if not x.filename.endswith(".png"):
          pass

    if len(ctx.message.attachments) == 0 or y == 0:
      url = ctx.author.avatar_url_as(format="png")
      await headpat_converter(url,ctx)

  @commands.command(brief="a hug command to hug people",help="this actually the second hug command and is quite powerful.")
  async def hug2(self,ctx,*, Member: BetterMemberConverter=None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
    
    asuna = asuna_api.Client()
    url = await asuna.get_gif("hug")
    await asuna.close()

    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} super hugged you!",icon_url=(person.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="powered using the asuna.ga api")
    
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed DM'ing them...")

  @commands.command(brief="a kiss command",help="a command where you can target a user or pick yourself to get a kiss gif( I don't know why I have this)")
  async def kiss(self,ctx,*, Member: BetterMemberConverter=None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
    
    asuna = asuna_api.Client()
    url = await asuna.get_gif("kiss")
    await asuna.close()
          
    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} kissed you",icon_url=(person.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="Why did I make this command? powered using the asuna.ga api")
    
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed Dming them...")

  @commands.command(brief="a command to get a neko",help="using the asuna.ga api you will get these images")
  async def neko(self,ctx):
    asuna = asuna_api.Client()
    url = await asuna.get_gif("neko")
    await asuna.close()
    
    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{ctx.author} requested a neko picture",icon_url=(ctx.author.avatar_url))
    embed.set_image(url=url.url)
    embed.set_footer(text="powered using the asuna.ga api")
    await ctx.send(embed=embed)

  @commands.command(brief="a command to send wink gifs",wink="you select a user to send it to and it will send it to you lol")
  async def wink(self,ctx,*, Member: BetterMemberConverter=None):
    if Member is None:
      Member = ctx.author
      
    if Member.id == ctx.author.id:
      person = self.client.user
      target = ctx.author
    
    if Member.id != ctx.author.id:
      person = ctx.author
      target = Member
    
    sr_client=sr_api.Client()
    image=await sr_client.get_gif("wink")
    await sr_client.close()

    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} winked at you",icon_url=(person.avatar_url))
    embed.set_image(url=image.url)
    embed.set_footer(text="powered by some random api")

    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send(content=target.mention,embed=embed) 

    if isinstance(ctx.channel,discord.DMChannel):
      if target.dm_channel is None:
        await target.create_dm()
      
      try:
        await target.send(content=target.mention,embed=embed)
      except discord.Forbidden:
        await ctx.author.send("Failed Dming them...")

def setup(client):
  client.add_cog(Image(client))