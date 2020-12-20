import discord
from discord.ext import commands
import math
import B
import ClientConfig
import os
import random
import userinfo
import aiohttp

discordprefix = "test*"
client = ClientConfig.client

@client.command()
async def ping(ctx):
  await ctx.send("Pong")
  await ctx.send(f"Response time: {client.latency*1000}")

@client.command()
async def pi(ctx):
  await ctx.send(math.pi)

@client.command()
async def hug(ctx):
  message = ctx.message
  hug = message.content.replace(discordprefix+"hug","")
  if hug == (""):
    person = client.user
    target = message.author
  
  if len(message.mentions) > 0:
    target = message.mentions[0]
    person = message.author
  
  if len(message.mentions) == 0:
    person = message.author
    target=await userinfo.user_grab(message)

  if target.id == person.id:
    person = client.user
    target = message.author
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://some-random-api.ml/animu/hug') as anime:
      res = await anime.json()
  for x in res:
    embed=discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"{person} hugged you",icon_url=(person.avatar_url))
    embed.set_image(url=res[x])
    await message.channel.send(content=target.mention,embed=embed)


@client.event
async def on_ready():
  print("Bot is online")
  print(f"Logged in as {client.user}")
  print(f"Id: {client.user.id}")

@client.event
async def on_message(message):
  if isinstance(message.channel, discord.DMChannel):
    print("DM channel")
  
  test=await client.get_context(message)
  if (test.valid) == False:
    pass
  #print(test.prefix)
  
  await client.process_commands(message)




  

B.b()

client.run(os.environ["classic_token"])
