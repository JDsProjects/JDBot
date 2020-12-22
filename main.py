import discord
from discord.ext import commands
import math
import B
import ClientConfig
import os
import random
import logging
import json
import aiohttp
import typing
import re
import asyncio
#import typing
import random

logging.basicConfig(level=logging.WARNING)
ratelimit_detection=logging.Filter(name='WARNING:discord.http:We are being rate limited.')

client = ClientConfig.client

class BetterUserconverter(commands.Converter):
  async def convert(self, ctx, argument):
    try:
      user=await commands.UserConverter().convert(ctx,argument)
    except commands.UserNotFound:
      user = None
    if not user and ctx.guild:
      user=ctx.guild.get_member_named(argument)
    if user == None:
      match = re.compile(r'([0-9]{15,21})$').match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
      if match:
        argument = match.group(1)

      #if not match:
        #match2 = re.match(r'<@&([0-9]+)>$',argument)
        #if match2:
          #argument2=match2.group(1)
          #role=ctx.guild.get_role(int(argument2))
          #going to be around when 1.16 comes around lol
      if argument.isdigit():
        user=client.get_user(int(argument))
        if user == None:
          try:
            user=await client.fetch_user(int(argument))
          except:
            user = None
    if user == None:
      tag = re.match(r"#?(\d{4})",argument)
      if tag:
        test=discord.utils.get(client.users, discriminator = tag.group(1))
        if test:
          user = test
        if not test:
          user=ctx.author
    return user

@client.command()
async def ping(ctx):
  await ctx.send("Pong")
  await ctx.send(f"Response time: {client.latency*1000}")

@client.command()
async def pi(ctx):
  await ctx.send(math.pi)

@client.event
async def on_ready():
  print("Bot is Ready")
  print(f"Logged in as {client.user}")
  print(f"Id: {client.user.id}")

@client.command(help="repeats what you say",brief="a command that repeats what you say the orginal message is deleted")
async def say(ctx,*,args=None):
  if args:
    await ctx.send(args)

@client.command(help="a command that gives information on users",brief="this can work with mentions, ids, usernames, and even full names.")
async def userinfo(ctx,*,user: BetterUserconverter = None):
  if not user:
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
      for guild in client.guilds:
        member=guild.get_member(user.id)
        if member:
          status=str(member.status).upper()
          break
      highest_role = "None Found"
  if not ctx.guild:
      nickname = "None"
      joined_guild = "N/A"
      status = "Unknown"
      for guild in client.guilds:
        member=guild.get_member(user.id)
        if member:
          status=str(member.status).upper()
          break
      highest_role = "None Found"
  
  guilds_list=[guild for guild in client.guilds if guild.get_member(user.id)]
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

@client.event
async def on_message(message):
  if isinstance(message.channel, discord.DMChannel):
    time_used=(message.created_at).strftime('%m/%d/%Y %H:%M:%S')
    embed_message = discord.Embed(title=message.content, description=time_used, color=random.randint(0, 16777215))
    embed_message.set_author(name=f"Direct Message From {message.author}:",icon_url=(message.author.avatar_url))
    embed_message.set_footer(text = f"{message.author.id}")
    embed_message.set_thumbnail(url = "https://media.discordapp.net/attachments/556242984241201167/763866804359135292/inbox.png?width=677&height=677")
    channel_usage=client.get_channel(738912143679946783)
    embed_message.add_field(name="Sent To:",value=str(channel_usage))
    await channel_usage.send(embed=embed_message)
  
  test=await client.get_context(message)
  if (test.valid) == False:
    if test.prefix != None:
      if test.command == None:
        time_used=(message.created_at).strftime('%m/%d/%Y %H:%M:%S')
        embed_message = discord.Embed(title=f" {message.content}", description=time_used,color=random.randint(0, 16777215))
        embed_message.set_author(name=f"{message.author} tried to excute invalid command:",icon_url=(message.author.avatar_url))
        embed_message.set_footer(text = f"{message.author.id}")
        embed_message.set_thumbnail(url="https://media.discordapp.net/attachments/738912143679946783/763873708908478474/Warning.png")
        await client.get_channel(738912143679946783).send(embed=embed_message)
  
  await client.process_commands(message) 

B.b()

client.run(os.environ["classic_token"])
