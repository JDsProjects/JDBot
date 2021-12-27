from discord.ext import commands
import discord, asyncpraw , os, random, tweepy, functools

class Reddit(commands.Cog):
  "Commands to get random memes from Reddit"
  def __init__(self, bot):
    self.bot = bot
    bot.loop.create_task(self.__ainit__())

  async def __ainit__(self):
    await self.bot.wait_until_ready()
    self.reddit = asyncpraw.Reddit(client_id = os.getenv("reddit_client_id"), client_secret = os.getenv("reddit_client_secret"), password = os.getenv("reddit_password"), requestor_kwargs = {"session" : self.bot.session}, user_agent="JDBot 2.0", username = os.getenv("reddit_username"))

  async def asyncpraw_handler(self, sub_name):
    subreddit = await self.reddit.subreddit(sub_name)
    meme_list = [result async for result in subreddit.new()]

    meme_list = list(filter(lambda m: not m.over_18, meme_list))

    data = random.choice(meme_list)
    embed = discord.Embed(title=f"{data.subreddit_name_prefixed}",description=f"[{data.title}](https://reddit.com{data.permalink})", color=0x00FF00)
    embed.set_image(url=data.url)
    embed.set_footer(text=f"Upvote ratio : {data.upvote_ratio}")
    return embed

  @commands.command(brief="Random Meme from Dank Memes with asyncpraw")
  async def dankmeme(self,ctx):
    embed = await self.asyncpraw_handler("dankmeme")
    await ctx.send(embed=embed)

  @commands.command()
  async def programmerhumor(self,ctx):
    embed=await self.asyncpraw_handler("programmerhumor")
    await ctx.send(embed=embed)

  @commands.command()
  async def codingmemes(self, ctx):
    embed = await self.asyncpraw_handler("codingmemes")
    await ctx.send(embed=embed)

  @commands.command()
  async def smg4(self, ctx):
    embed = await self.asyncpraw_handler("smg4")
    await ctx.send(embed = embed)

  @commands.command()
  async def insaneparents(self, ctx):
    embed = await self.asyncpraw_handler("insaneparents")
    await ctx.send(embed = embed)

  @commands.command()
  async def supermariogalaxy2(self, ctx):
    embed = await self.asyncpraw_handler("supermariogalaxy2")
    await ctx.send(embed = embed)

  @commands.command()
  async def supermariogalaxy(self, ctx):
    embed = await self.asyncpraw_handler("supermariogalaxy")
    await ctx.send(embed = embed)

  @commands.command()
  async def insaneparentsmemes(self, ctx):
    embed = await self.asyncpraw_handler("insaneparentsmemes")
    await ctx.send(embed = embed)

  @commands.command()
  async def entitledparents(self, ctx):
    embed = await self.asyncpraw_handler("entitledparents")
    await ctx.send(embed = embed)

  @commands.command()
  async def dankmemer(self, ctx):
    embed = await self.asyncpraw_handler("dankmemer")
    await ctx.send(embed = embed)

  @commands.command()
  async def memes(self, ctx):
    embed = await self.asyncpraw_handler("memes")
    await ctx.send(embed = embed)

  @commands.command()
  async def askreddit(self, ctx):
    embed = await self.asyncpraw_handler("askreddit")
    await ctx.send(embed = embed)

  @commands.command()
  async def memeeconomy(self, ctx):
    embed = await self.asyncpraw_handler("memeeconomy")
    await ctx.send(embed = embed)

  @commands.command()
  async def dankmemes(self, ctx):
    embed = await self.asyncpraw_handler("dankmemes")
    await ctx.send(embed = embed)

  @commands.command()
  async def funny(self, ctx):
    embed = await self.asyncpraw_handler("funny")
    await ctx.send(embed = embed)

  @commands.command()
  async def ask(self, ctx):
    embed = await self.asyncpraw_handler("ask")
    await ctx.send(embed = embed)

  @commands.command()
  async def gametheorists(self, ctx):
    embed = await self.asyncpraw_handler("gametheorists")
    await ctx.send(embed = embed)

  @commands.command()
  async def _advice(self, ctx):
    embed = await self.asyncpraw_handler("advice")
    await ctx.send(embed = embed)

  @commands.command()
  async def discordapp(self, ctx):
    embed = await self.asyncpraw_handler("discordapp")
    await ctx.send(embed = embed)

class Twitter(commands.Cog):
  "Commands related to Twitter"
  def __init__(self, bot):
    self.bot = bot
  


def setup(bot):
  bot.add_cog(Reddit(bot))
  bot.add_cog(Twitter(bot))