from discord.ext import commands
import discord, random, json
from utils import BetterMemberConverter, warn_permission
from discord.ext.commands.cooldowns import BucketType

class Moderation(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.cooldown(1,90,BucketType.user)
  @commands.command(brief="a command to warn people, but if you aren't admin it doesn't penalize.")
  async def warn(self,ctx,Member: BetterMemberConverter = None):
    if warn_permission(ctx):

      if Member is None:
        Member = ctx.author

      if Member:
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"You have been warned by {ctx.author}",icon_url=("https://i.imgur.com/vkleJ9a.png"))
        embed.set_image(url="https://i.imgur.com/jDLcaYc.gif")
        embed.set_footer(text = f"ID: {ctx.author.id}")

        if Member.dm_channel is None:
          await Member.create_dm()
        
        try:
          await Member.send(embed=embed)

        except discord.Forbidden:
          await ctx.send("they don't seem like a valid user.")
      
      embed.set_footer(text = f"ID: {ctx.author.id}\nWarned by {ctx.author}\nWarned ID: {Member.id} \nWarned: {Member}")
      await self.client.get_channel(738912143679946783).send(embed=embed) 

      if (ctx.author.dm_channel is None):
        await ctx.author.create_dm()

      try:
        await ctx.author.send(content=f"Why did you warn {Member}?")
      except discord.Forbidden:
        await ctx.send("we can't DM them :(")

    if warn_permission(ctx) is False:
      await ctx.send("You don't have permission to use that.")

  @warn.error
  async def warn_errror(self,ctx,error):
    await ctx.send(error)

  @commands.command(help="a command to scan for malicious bots, specificially ones that only give you random invites and are fake(work in progress)")
  async def scan_guild(self,ctx):
    with open('sus_users.json', 'r') as f:
      sus_users=json.load(f)
    if isinstance(ctx.channel, discord.TextChannel):
      count = 0
      for x in sus_users:
        user=ctx.guild.get_member(int(x))
        if user:
          count = count + 1
          await ctx.send(f"Found {x}. \nReason: {sus_users[x]}")
      if count < 1:
        await ctx.send("No Bad users found.")
    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("please use the global version")

  @commands.command(help="a way to report a user, who might appear in the sus list. also please provide ids and reasons. (work in progress")
  async def report(self,ctx,*,args=None):
    if args:
      jdjg = self.client.get_user(168422909482762240)
      if (jdjg.dm_channel is None):
        await jdjg.create_dm()
      embed = discord.Embed(color=random.randint(0, 16777215))
      embed.set_author(name=f"Report by {ctx.author}",icon_url=(ctx.author.avatar_url))
      embed.add_field(name="Details:",value=args)
      embed.set_footer(text=f"Reporter's ID is {ctx.author.id}")
      await jdjg.dm_channel.send(embed=embed)
      await ctx.send(content="report sent to JDJG",embed=embed)
    
    if args is None:
      await ctx.send("You didn't give enough information to use.")
  

def setup(client):
  client.add_cog(Moderation(client))