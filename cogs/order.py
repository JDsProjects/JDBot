import os
from discord.ext import commands
import discord
import time
import async_cse
import random
from difflib import SequenceMatcher
import TenGiphPy

#someday get https://github.com/NinjaSnail1080/akinator.py

tenor_client = TenGiphPy.Tenor(token=os.environ["tenor_key"])
giphy_client = TenGiphPy.Giphy(token=os.environ["giphy_token"])

class Order(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.group(name="order",invoke_without_command=True)
  async def order(self,ctx,*,args=None):
    if args is None:
      await ctx.send("You can't order nothing.")
    if args:
      time_before=time.process_time() 
      image_client=async_cse.Search(os.environ["image_api_key"],engine_id=os.environ["google_image_key"])
      try:
        results = await image_client.search(args, safesearch=True, image_search=True)
        emoji_image = sorted(results, key=lambda x: SequenceMatcher(None, x.image_url,args).ratio())[-1]
      except async_cse.search.NoResults:
        await ctx.send("No results found :(")
        await image_client.close()
        return

      await image_client.close()
      time_after=time.process_time()
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass
    
      embed = discord.Embed(title=f"Item: {args}", description=f"{ctx.author} ordered a {args}",color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:",icon_url=(ctx.author.avatar_url))
      embed.add_field(name="Time Spent:",value=f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:",value="Google Images Api")
      embed.set_image(url=emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)",embed=embed)
      await self.client.get_channel(738912143679946783).send(embed=embed)

  @order.command(brief="a command to shuffle images from google images")
  async def shuffle(self,ctx,*,args=None):
    if args is None:
        await self.order(ctx,args="shuffle")
    if args:
      time_before=time.process_time() 
      image_client=async_cse.Search(os.environ["image_api_key"],engine_id=os.environ["google_image_key"])
      try:
        results = await image_client.search(args, safesearch=True, image_search=True)
      except async_cse.search.NoResults:
        await ctx.send("No results found :(")
        await image_client.close()
        return

      emoji_image = random.choice(results)
      await image_client.close()
      time_after=time.process_time()
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass

      embed = discord.Embed(title=f"Item: {args}", description=f"{ctx.author} ordered a {args}",color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:",icon_url=(ctx.author.avatar_url))
      embed.add_field(name="Time Spent:",value=f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:",value="Google Images Api")
      embed.set_image(url=emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)",embed=embed)
      await self.client.get_channel(738912143679946783).send(embed=embed)

  @commands.command(brief="a command to shuffle images from google images",aliases=["order-shuffle"])
  async def order_shuffle(self,ctx,*,args):
    if args is None:
      await ctx.send("You can't order nothing")
    if args:
      time_before=time.process_time() 
      image_client=async_cse.Search(os.environ["image_api_key"],engine_id=os.environ["google_image_key"])
      try:
        results = await image_client.search(args, safesearch=True, image_search=True)
      except async_cse.search.NoResults:
        await ctx.send("No results found :(")
        await image_client.close()
        return

      emoji_image = random.choice(results)
      await image_client.close()
      time_after=time.process_time()
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass

      embed = discord.Embed(title=f"Item: {args}", description=f"{ctx.author} ordered a {args}",color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:",icon_url=(ctx.author.avatar_url))
      embed.add_field(name="Time Spent:",value=f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:",value="Google Images Api")
      embed.set_image(url=emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)",embed=embed)
      await self.client.get_channel(738912143679946783).send(embed=embed)
    
  @commands.group(name="tenor",invoke_without_command=True)
  async def tenor(self,ctx,*,args=None):
    #if args:
      #tenor_client.
    if args is None:
      await ctx.send("That doesn't have any value.")
      await ctx.send("tenor")

  @tenor.command(help="work in progress",name="shuffle")
  async def tenor_random(self,ctx,*,args=None):
    if args is None:
      await ctx.send("That doesn't have any value.")
      await ctx.send("tenor shuffle")

  @commands.command(help="work in progress",aliases=["tenor-shuffle"])
  async def tenor_shuffle(self,ctx,*,args):
    if args is None:
      await ctx.send("That doesn't have any value.")
      await ctx.send("tenor shuffle")
  
  @commands.group(name="giphy",invoke_without_command=True)
  async def giphy(self,ctx,*,args=None):
    if args is None:
      await ctx.send("That doesn't have any value.")
      await ctx.send("tenor")

  @giphy.command(help="work in progress",name="shuffle")
  async def giphy_random(self,ctx,*,args=None):
    if args is None:
      await ctx.send("That doesn't have any value.")
      await ctx.send("giphy shuffle")
  
  @commands.command(help="work in progress",aliases=["giphy-shuffle"])
  async def giphy_shuffle(self,ctx,*,args):
    if args is None:
        await ctx.send("That doesn't have any value.")
        await ctx.send("giphy shuffle")

def setup(client):
  client.add_cog(Order(client))