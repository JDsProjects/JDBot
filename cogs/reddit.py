from discord.ext import commands
import discord, apraw, os, random, aiohttp

class Reddit(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    self.reddit =  apraw.Reddit(client_id=os.getenv("reddit_client_id"), client_secret=os.getenv("reddit_client_secret"),password= os.getenv("reddit_password"), user_agent="JDBot 1.0", username= os.getenv("reddit_username"),requestor_kwargs={"session": self.bot.session})

  async def apraw_handler(self,sub_name):
    subreddit = await self.reddit.subreddit(sub_name)
    meme_list = []
    async for submission in subreddit.new():
      meme_list.append(submission)

    meme_list= [submission async for submission in subreddit.new()]

    data = random.choice(meme_list)
    embed = discord.Embed(title=f"{data.subreddit_name_prefixed}",description=f"[{data.title}](https://reddit.com{data.permalink})", color=0x00FF00)
    embed.set_image(url=data.url)
    embed.set_footer(text=f"Upvote ratio : {data.upvote_ratio}")
    return embed

  @commands.command(brief="Random Meme from Dank Memes with Apraw")
  async def dankmeme(self,ctx):
    embed=await self.apraw_handler("dankmeme")
    await ctx.send(embed=embed)

  @commands.command()
  async def programmerhumor(self,ctx):
    embed=await self.apraw_handler("programmerhumor")
    await ctx.send(embed=embed)

  @commands.command()
  async def codingmemes(self,ctx):
    embed = await self.apraw_handler("codingmemes")
    await ctx.send(embed=embed)

  @commands.command(brief="Random meme from Dank Memes with aiohttp",help="Content returned may not be suitable to younger audiences")
  async def dankmeme2(self,ctx):
    e = await self.bot.session.get("https://www.reddit.com/r/dankmemes/.json")
    data = random.choice((await e.json())["data"]["children"])["data"]
    embed = discord.Embed(title="r/dankmemes",description=f'[{data["title"]}](https://reddit.com{data["permalink"]})', color=0x00FF00)
    embed.set_image(url=data["url"])
    embed.set_footer(text=f"Upvote ratio : {data['upvote_ratio']}")
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Reddit(bot))