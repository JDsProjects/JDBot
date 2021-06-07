from discord.ext import commands
import discord, asyncpraw , os, random, tweepy, functools

class Reddit(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    bot.loop.create_task(self.__ainit__())

  async def __ainit__(self):
    await self.bot.wait_until_ready()
    self.reddit = asyncpraw.Reddit(client_id=os.getenv("reddit_client_id"), client_secret=os.getenv("reddit_client_secret"), user_agent="JDBot 1.0", username= os.getenv("reddit_username"), password = os.getenv("reddit_password"),requestor_kwargs={"session": self.bot.session})

  async def asyncpraw_handler(self, sub_name):
    subreddit = await self.reddit.subreddit(sub_name)

    meme_list = [result async for result in subreddit.new()]

    data = random.choice(meme_list)
    embed = discord.Embed(title=f"{data.subreddit_name_prefixed}",description=f"[{data.title}](https://reddit.com{data.permalink})", color=0x00FF00)
    embed.set_image(url=data.url)
    embed.set_footer(text=f"Upvote ratio : {data.upvote_ratio}")
    return embed

  @commands.command(brief="Random Meme from Dank Memes with asyncpraw")
  async def dankmeme(self,ctx):
    embed=await self.asyncpraw_handler("dankmeme")
    await ctx.send(embed=embed)

  @commands.command()
  async def programmerhumor(self,ctx):
    embed=await self.asyncpraw_handler("programmerhumor")
    await ctx.send(embed=embed)

  @commands.command()
  async def codingmemes(self,ctx):
    embed = await self.asyncpraw_handler("codingmemes")
    await ctx.send(embed=embed)

  @commands.command(brief="Random meme from Dank Memes with aiohttp",help="Content returned may not be suitable to younger audiences")
  async def dankmeme2(self,ctx):
    e = await self.bot.session.get("https://www.reddit.com/r/dankmemes/.json")
    data = random.choice((await e.json())["data"]["children"])["data"]
    embed = discord.Embed(title="r/dankmemes",description=f'[{data["title"]}](https://reddit.com{data["permalink"]})', color=0x00FF00)
    embed.set_image(url=data["url"])
    embed.set_footer(text=f"Upvote ratio : {data['upvote_ratio']}")
    await ctx.send(embed=embed)

class Twitter(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  
  


def setup(bot):
  bot.add_cog(Reddit(bot))
  bot.add_cog(Twitter(bot))