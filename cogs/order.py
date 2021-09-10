import os, discord, time, async_cse, random, cse
from discord.ext import commands, menus
from difflib import SequenceMatcher
from discord.ext.commands.cooldowns import BucketType
from discord.ext.menus.views import ViewMenuPages

from aiogifs.tenor import TenorClient, ContentFilter
from aiogifs.giphy import GiphyClient, AgeRating

class Order(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    bot.loop.create_task(self.__ainit__())
  
  async def __ainit__(self):
    await self.bot.wait_until_ready()
    tenor_key = os.environ["tenor_key"]
    giphy_key = os.environ["giphy_token"] 

    image_api_key = os.environ["image_api_key"]  
    image_engine_key = os.environ["google_image_key"] 

    self.image_client = async_cse.Search(image_api_key, engine_id = image_engine_key, session = self.bot.session)

    self.tenor_client = TenorClient (api_key=tenor_key, session = self.bot.session)
    self.giphy_client = GiphyClient(api_key=giphy_key, session = self.bot.session)

    self.google_engine = cse.Search(image_api_key, session = self.bot.session, engine_id = image_engine_key)

  @commands.cooldown(1, 30, BucketType.user)
  @commands.group(name = "order", invoke_without_command = True, brief = "searches from google images to find the closest google image")
  async def order(self, ctx, *, args = None):
    if not args:
      await ctx.send("You can't order nothing.")

    if args:
      time_before = time.perf_counter()  
      
      try:
        results = await self.image_client.search(args, safesearch = True, image_search = True)
        emoji_image = sorted(results, key = lambda x: SequenceMatcher(None, x.image_url, args).ratio())[-1]

        
      except async_cse.search.NoResults:
        return await ctx.send("No results found :(")

      time_after = time.perf_counter() 
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass
    
      embed = discord.Embed(title = f"Item: {args}", description=f"{ctx.author} ordered a {args}", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:", icon_url = (ctx.author.avatar.url))
      embed.add_field(name="Time Spent:", value = f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:", value="Google Images Api")

      embed.add_field(name = "Image link:", value = f"[Image Link]({emoji_image.image_url})")

      embed.set_image(url = emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)", embed = embed)

      await self.bot.get_channel(855217084710912050).send(embed = embed)

  @commands.cooldown(1, 30, BucketType.user)
  @order.command(brief = "a command to shuffle images from google images")
  async def shuffle(self, ctx, *, args = None):
    if not args:
      await self.order(ctx, args="shuffle")

    if args:
      time_before=time.perf_counter()
      try:
        results = await self.image_client.search(args, safesearch = True, image_search=True)
      except async_cse.search.NoResults:
        return await ctx.send("No results found :(")


      emoji_image = random.choice(results)
      time_after=time.perf_counter() 
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass

      embed = discord.Embed(title=f"Item: {args}", description=f"{ctx.author} ordered a {args}",color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:",icon_url=(ctx.author.avatar.url))
      embed.add_field(name="Time Spent:",value=f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:",value="Google Images Api")

      embed.add_field(name = "Image link:", value = f"[Image Link]({emoji_image.image_url})")

      embed.set_image(url=emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)",embed=embed)
      await self.bot.get_channel(855217084710912050).send(embed=embed)

  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief="a command to shuffle images from google images", aliases=["order-shuffle"])
  async def order_shuffle(self, ctx, *, args = None):
    if not args:
      await ctx.send("You can't order nothing")

    if args:
      time_before=time.perf_counter()  
      try:
        results = await self.image_client.search(args, safesearch = True, image_search=True)
      except async_cse.search.NoResults:
        return await ctx.send("No results found :(")

      emoji_image = random.choice(results)

      time_after = time.perf_counter() 
      
      try:
        await ctx.message.delete()
      except discord.errors.Forbidden:
        pass

      embed = discord.Embed(title=f"Item: {args}", description=f"{ctx.author} ordered a {args}", color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
      embed.set_author(name=f"order for {ctx.author}:",icon_url=(ctx.author.avatar.url))
      embed.add_field(name="Time Spent:",value=f"{int((time_after - time_before)*1000)}MS")
      embed.add_field(name="Powered by:",value="Google Images Api")

      embed.add_field(name = "Image link:", value = f"[Image Link]({emoji_image.image_url})")

      embed.set_image(url=emoji_image.image_url)
      embed.set_footer(text = f"{ctx.author.id} \nCopyright: I don't know the copyright.")
      await ctx.send(content="Order has been logged for safety purposes(we want to make sure no unsafe search is sent)",embed=embed)
      await self.bot.get_channel(855217084710912050).send(embed=embed)

  @commands.cooldown(1, 30, BucketType.user)
  @commands.group(name = "tenor", invoke_without_command = True, brief = "searches from tenor to find the closest image.")
  async def tenor(self, ctx, *, args = None):

    if not args:
      return await ctx.send("You can't search for nothing")

    safesearch_type = ContentFilter.high()
    results = await self.tenor_client.search(args, content_filter = safesearch_type, limit = 10)

    if not results:
      return await ctx.send("I got no results from tenor.")

    results_media = [r for r in results.media if r]

    if not results_media:
      return await ctx.send("I got no gif results from tenor.")

    gifNearest = sorted(results_media, key=lambda x: SequenceMatcher(None, x.item_url, args).ratio())[-1]

    embed = discord.Embed(title=f"Item: {args}", description = f"{ctx.author} ordered a {args}", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_author(name = f"order for {ctx.author}:", icon_url= ctx.author.avatar.url)
    embed.add_field(name = "Powered by:", value="Tenor")

    if gifNearest.gif: embed.set_image(url= gifNearest.gif.url)
    else: embed.set_image("https://i.imgur.com/sLQzAiW.png")

    embed.set_footer(text = f"{ctx.author.id}")

    await ctx.send(content = "Tenor has been logged for safety purposes(we want to make sure no unsafe search is sent)", embed = embed)

    await self.bot.get_channel(855217084710912050).send(embed = embed)

  @commands.cooldown(1, 30, BucketType.user)
  @tenor.command(help = "shuffles the results from the tenor results", name = "shuffle")
  async def tenor_random(self, ctx, *, args = None):

    if not args:
      return await self.tenor(ctx, args="shuffle")


    safesearch_type = ContentFilter.high()
    results = await self.tenor_client.search(args, content_filter = safesearch_type, limit = 10)

    if not results:
      return await ctx.send("I got no results from tenor.")

    results_media = [r for r in results.media if r]

    if not results_media:
      return await ctx.send("I got no gif results from tenor.")


    gifNearest = random.choice(results_media)

    embed = discord.Embed(title=f"Item: {args}", description = f"{ctx.author} ordered a {args}", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_author(name = f"order for {ctx.author}:", icon_url= ctx.author.avatar.url)
    embed.add_field(name = "Powered by:", value="Tenor")

    if gifNearest.gif: embed.set_image(url= gifNearest.gif.url)
    else: embed.set_image("https://i.imgur.com/sLQzAiW.png")

    embed.set_footer(text = f"{ctx.author.id}")

    await ctx.send(content = "Tenor has been logged for safety purposes(we want to make sure no unsafe search is sent)", embed = embed)

    await self.bot.get_channel(855217084710912050).send(embed = embed)

  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(help = "shuffles the results from the tenor results", aliases = ["tenor-shuffle"])
  async def tenor_shuffle(self, ctx, *, args = None):

    if not args:
      return await self.tenor(ctx, args = "shuffle")

    await self.tenor_random(ctx, args = args)
    
  @commands.cooldown(1, 30, BucketType.user)
  @commands.group(brief = "looks up an item from giphy.",invoke_without_command = True)
  async def giphy(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("That doesn't have any value.")

    safesearch_type = AgeRating.g()
    results = await self.giphy_client.search(args, rating = safesearch_type, limit = 10)

    if not results:
      return await ctx.send("I got no results from tenor.")

    results_media = [r for r in results.media if r]

    if not results_media:
      return await ctx.send("I got no gif results from giphy.")

    gifNearest = sorted(results_media, key = lambda x: SequenceMatcher(None, x.url, args).ratio())[-1]

    embed = discord.Embed(title=f"Item: {args}", description = f"{ctx.author} ordered a {args}",  color=random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_footer(text = f"{ctx.author.id}")

    embed.set_author(name = f"order for {ctx.author}:", icon_url = ctx.author.avatar.url)

    embed.add_field(name = "Powered by:", value="GIPHY")
    embed.set_image(url = f"https://media3.giphy.com/media/{gifNearest.id}/giphy.gif")

    await ctx.send(content = "Giphy has been logged for safety purposes(we want to make sure no unsafe search is sent)", embed = embed)

    await self.bot.get_channel(855217084710912050).send(embed = embed)

  @commands.cooldown(1, 30, BucketType.user)
  @giphy.command(help = "looks up an item from giphy but shuffled.", name = "shuffle")
  async def giphy_random(self, ctx, *, args = None):

    if not args:
      return await self.giphy(ctx, args = "shuffle")

    safesearch_type = AgeRating.g()
    results = await self.giphy_client.search(args, rating = safesearch_type, limit = 10)

    if not results:
      return await ctx.send("I got no results from tenor.")

    results_media = [r for r in results.media if r]

    if not results_media:
      return await ctx.send("I got no gif results from giphy.")

    gifNearest = random.choice(results_media)

    embed = discord.Embed(title=f"Item: {args}", description = f"{ctx.author} ordered a {args}",  color=random.randint(0, 16777215), timestamp = ctx.message.created_at)

    embed.set_footer(text = f"{ctx.author.id}")

    embed.set_author(name = f"order for {ctx.author}:", icon_url = ctx.author.avatar.url)

    embed.add_field(name = "Powered by:", value="GIPHY")
    embed.set_image(url = f"https://media3.giphy.com/media/{gifNearest.id}/giphy.gif")

    await ctx.send(content = "Giphy has been logged for safety purposes(we want to make sure no unsafe search is sent)", embed = embed)

    await self.bot.get_channel(855217084710912050).send(embed = embed)

    
    
  @commands.cooldown(1, 30, BucketType.user)
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(help = "looks up an item from giphy but shuffled", aliases=["giphy-shuffle"])
  async def giphy_shuffle(self, ctx, *, args = None):

    if not args:
      return await self.giphy(ctx, args = "shuffle")

    await self.giphy_random(ctx, args = args)

  async def cog_command_error(self, ctx, error):
    if ctx.command and not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()
      
    #I need to fix all cog_command_error

  class GoogleEmbed(menus.ListPageSource):
    async def format_page(self, menu, item):
      
      embed = discord.Embed(title = "Gooogle Search", description = f"[{item.title}]({item.link}) \n{item.snippet}", color = random.randint(0, 16777215))

      if item.image: embed.set_image(url = item.image)

      embed.set_footer(text = f"Google does some sketchy ad stuff, and descriptions from google are shown here, please be careful :D, thanks :D")

      return embed

  @commands.command(brief = "can search a search result from google with safe search!")
  async def google(self, ctx, *, args = None):

    if not args:
      return await ctx.send("You can't search for nothing, as well you need a thing to lokup.")

    try:
      results = await self.google_engine.search(args, max_results = 10, safe_search = True)
    
    except Exception as e:
      return await ctx.send(f"An error occured, error: {e}. Please give this to the owner. This was an error with results")

  
    menu = ViewMenuPages(self.GoogleEmbed(results, per_page = 1), delete_message_after = True)

    await menu.start(ctx)

    #this appears to work but I don't know if it's officially supported by the custom button menus team.

  @google.error
  async def google_error(self, ctx, error):
    await ctx.send(error)

    import traceback
    traceback.print_exc()



def setup(bot):
  bot.add_cog(Order(bot))