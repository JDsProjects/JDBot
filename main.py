import discord
from discord.ext import commands
import math
import discord.utils
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

logging.basicConfig(level=logging.WARNING)
ratelimit_detection=logging.Filter(name='WARNING:discord.http:We are being rate limited.')

client = ClientConfig.client

class BetterUserconverter(commands.Converter):
  async def convert(self, ctx, argument):
    user=ctx.guild.get_member_named(argument)
    if user == None:
      match = re.compile(r'([0-9]{15,21})$').match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
      if match:
        argument = match.group(1)

      if not match:
        match2 = re.match(r'<@&([0-9]+)>$',argument)
        if match2:
          print(match2.group(1))

      if argument.isdigit() == True:
        user=client.get_user(int(argument))
        if user == None:
          try:
            user=await client.fetch_user(int(argument))
          except:
            user = None
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
async def userinfo(ctx,user: BetterUserconverter=None):
  if user == None:
    user = ctx.author
  await ctx.send(user)

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
