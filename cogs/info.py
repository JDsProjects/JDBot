from discord.ext import commands
import re
import discord
import random
from utils import BetterMemberConverter, BetterUserconverter
import mystbin
import typing
from difflib import SequenceMatcher
import typing

class Info(commands.Cog):
  def __init__(self,client):
    self.client = client

  async def guildinfo(self,ctx,guild):
    bots = 0
    users = 0
    for x in guild.members:
      if x.bot is True:
        bots = bots + 1
      if x.bot is False:
        users = users + 1
    static_emojis = 0
    animated_emojis = 0
    usable_emojis = 0
    for x in guild.emojis:
      if x.animated is True:
        animated_emojis = animated_emojis + 1
      if x.animated is False:
        static_emojis = static_emojis + 1
      if x.available is True:
        usable_emojis = usable_emojis + 1
    
    embed = discord.Embed(title="Guild Info:",color=random.randint(0, 16777215))
    embed.add_field(name="Server Name:",value=guild.name)
    embed.add_field(name="Server ID:",value=guild.id)
    embed.add_field(name="Server region",value=guild.region)
    embed.add_field(name="Server created at:",value=f"{guild.created_at} UTC")
    embed.add_field(name="Server Owner:",value=guild.owner)
    embed.add_field(name="Member Count:",value=guild.member_count)
    embed.add_field(name="Users:",value=users)
    embed.add_field(name="Bots:",value=bots)
    embed.add_field(name="Channel Count:",value=len(guild.channels))
    embed.add_field(name="Role Count:",value=len(guild.roles))
    embed.set_thumbnail(url=(guild.icon_url))
    embed.add_field(name="Emoji Limit:",value=guild.emoji_limit)
    embed.add_field(name="Max File Size:",value=f"{guild.filesize_limit/1000000} MB")
    embed.add_field(name="Shard ID:",value=guild.shard_id)
    embed.add_field(name="Animated Icon",value=guild.is_icon_animated())
    embed.add_field(name="Static Emojis",value=static_emojis)
    embed.add_field(name="Animated Emojis",value=animated_emojis)
    embed.add_field(name="Total Emojis:",value=f"{len(guild.emojis)}/{guild.emoji_limit*2}")
    embed.add_field(name="Usable Emojis",value=usable_emojis)

    await ctx.send(embed=embed)

  @commands.command(help="gives you info about a guild",aliases=["server_info","guild_fetch","guild_info","fetch_guild",])
  async def serverinfo(self,ctx,*,args=None):
    if args:
      match=re.match(r'(\d{16,21})',args)
      guild=self.client.get_guild(int(match.group(0)))
      if guild is None:
        guild = ctx.guild

    if args is None:
      guild = ctx.guild
    
    await self.guildinfo(ctx,guild)

  @commands.command(aliases=["user info", "user_info","user-info"],brief="a command that gives information on users",help="this can work with mentions, ids, usernames, and even full names.")
  async def userinfo(self,ctx,*,user: BetterUserconverter = None):
    if user is None:
      user = ctx.author

    if user.bot:
      user_type = "Bot"
    if not user.bot:
      user_type = "User"
    
    if ctx.guild:
      member_version=ctx.guild.get_member(user.id)
      if member_version:
        nickname = str(member_version.nick)
        joined_guild = member_version.joined_at.strftime('%m/%d/%Y %H:%M:%S')
        status = str(member_version.status).upper()
        highest_role = member_version.roles[-1]
      if not member_version:
        nickname = str(member_version)
        joined_guild = "N/A"
        status = "Unknown"
        for guild in self.client.guilds:
          member=guild.get_member(user.id)
          if member:
            status=str(member.status).upper()
            break
        highest_role = "None Found"
    if not ctx.guild:
        nickname = "None"
        joined_guild = "N/A"
        status = "Unknown"
        for guild in self.client.guilds:
          member=guild.get_member(user.id)
          if member:
            status=str(member.status).upper()
            break
        highest_role = "None Found"
    
    guilds_list=[guild for guild in self.client.guilds if guild.get_member(user.id)]
    if not guilds_list:
      guild_list = "None"

    x = 0
    for g in guilds_list:
      if x < 1:
        guild_list = g.name
      if x > 0:
        guild_list = guild_list + f", {g.name}"
      x = x + 1

    embed=discord.Embed(title=f"{user}",description=f"Type: {user_type}", color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
    embed.add_field(name="Username: ", value = user.name)
    embed.add_field(name="Discriminator:",value=user.discriminator)
    embed.add_field(name="Nickname: ", value = nickname)
    embed.add_field(name="Joined Discord: ",value = (user.created_at.strftime('%m/%d/%Y %H:%M:%S')))
    embed.add_field(name="Joined Guild: ",value = joined_guild)
    embed.add_field(name="Part of Guilds:", value=guild_list)
    embed.add_field(name="ID:",value=user.id)
    embed.add_field(name="Status:",value=status)
    embed.add_field(name="Highest Role:",value=highest_role)
    embed.set_image(url=user.avatar_url)
    await ctx.send(embed=embed)

  @commands.command(brief="uploads your emojis into a mystbin link")
  async def look_at(self,ctx):
    if isinstance(ctx.message.channel, discord.TextChannel):
      message_emojis = ""
      for x in ctx.guild.emojis:
        message_emojis = message_emojis+" "+str(x)+"\n"
      mystbin_client = mystbin.Client()
      paste = await mystbin_client.post(message_emojis)
      await mystbin_client.close()
      await ctx.send(paste.url)
      
    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("We can't use that in DMS")

  @commands.command(help="gives the id of the current guild or DM if you are in one.")
  async def guild_get(self,ctx):
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=ctx.guild.id) 

    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send(ctx.channel.id)

  @commands.command(brief="a command to tell you the channel id")
  async def this(self,ctx):
    await ctx.send(ctx.channel.id)

  @commands.command(help="fetch invite details")
  async def fetch_invite(self,ctx,*invites:typing.Union[discord.Invite, str]):
    for x in invites:
      if isinstance(x,discord.Invite):
        if x.guild:
          image = x.guild.icon_url
          guild = x.guild
          guild_id = x.guild.id
        if x.guild is None:
          guild = "Group Chat"
          image = "https://i.imgur.com/pQS3jkI.png"
          guild_id = "Unknown"
        embed=discord.Embed(title=f"Invite for {guild}:",color=random.randint(0, 16777215))
        embed.set_author(name="Discord Invite Details:",icon_url=(image))
        embed.add_field(name="Inviter:",value=f"{x.inviter}")
        embed.add_field(name="User Count:",value=f"{x.approximate_member_count}")
        embed.add_field(name="Active User Count:",value=f"{x.approximate_presence_count}")
        embed.add_field(name="Invite Channel",value=f"{x.channel}")
        embed.set_footer(text=f"ID: {guild_id}\nInvite Code: {x.code}\nInvite Url: {x.url}")
        await ctx.send(embed=embed)
        
      if isinstance(x,str):
        await ctx.send(content=f"it returned as {x}. It couldn't fetch it :(")

  @commands.command(brief="gives info about a file")
  async def file(self,ctx):
    if len(ctx.message.attachments) < 1:
      await ctx.send(ctx.message.attachments)
      await ctx.send("no file submitted")
    if len(ctx.message.attachments) > 0:
      embed = discord.Embed(title="Attachment info",color=random.randint(0, 16777215))
      for x in ctx.message.attachments:
        embed.add_field(name=f"ID: {x.id}",value=f"[{x.filename}]({x.url})")
        embed.set_footer(text="Check on the url/urls to get a direct download to the url.")
      await ctx.send(embed=embed,content="\nThat's good")

  @commands.command(brief="a command to get the avatar of a user",help="using the userinfo technology it now powers avatar grabbing.",aliases=["pfp","av"])
  async def avatar(self,ctx,*,user: BetterUserconverter = None): 
    if user is None:
      user = ctx.author
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{user.name}'s avatar:",icon_url=(user.avatar_url))
    embed.set_image(url=(user.avatar_url))
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

  @commands.command(brief="this is a way to get the nearest channel.")
  async def closest_channel(self,ctx,*,args=None):
    if args is None:
      await ctx.send("Please specify a channel")
    
    if args:
      if isinstance(ctx.channel, discord.TextChannel):
        channel=discord.utils.get(ctx.guild.channels,name=args)
        if channel:
          await ctx.send(channel.mention)
        if channel is None:
          await ctx.send("Unforantely we haven't found anything")

      if isinstance(ctx.channel,discord.DMChannel):
        await ctx.send("You can't use it in a DM.")


  @commands.command(brief="a command to get the closest user.")
  async def closest_user(self,ctx,*,args=None):
    if args is None:
      await ctx.send("please specify a user")
    if args:
      userNearest = discord.utils.get(self.client.users,name=args)
      user_nick = discord.utils.get(self.client.users,display_name=args)
      if userNearest is None:
        userNearest = sorted(self.client.users, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]
      if user_nick is None:
        user_nick = sorted(self.client.users, key=lambda x: SequenceMatcher(None, x.display_name,args).ratio())[-1]
      await ctx.send(f"Username: {userNearest}")
      await ctx.send(f"Display name: {user_nick}")
    
    if isinstance(ctx.channel, discord.TextChannel):
      member_list = []
      for x in ctx.guild.members:
        if x.nick is None:
          pass
        if x.nick:
          member_list.append(x)
      
      nearest_server_nick = sorted(member_list, key=lambda x: SequenceMatcher(None, x.nick,args).ratio())[-1] 
      await ctx.send(f"Nickname: {nearest_server_nick}")

    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("You unforantely don't get the last value.")
  
  @commands.command(help="emojis command(work in progress)")
  async def emoji(self,ctx,*emojis: typing.Union[discord.PartialEmoji, str]):
    for x in emojis:
      if isinstance(x,discord.PartialEmoji):
        embed = discord.Embed(title=f"Emoji: **{x.name}**",color=random.randint(0, 16777215))
        embed.set_image(url=x.url)
        embed.set_footer(text=f"Emoji ID:{x.id}")
        await ctx.send(embed=embed)
      else:
        await ctx.send(content=f"We can't fetch {x} yet")
    if len(emojis) < 1:
      await ctx.send("Looks like there was no emojis.")

def setup(client):
  client.add_cog(Info(client))