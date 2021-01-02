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
import datetime
from io import BytesIO
import DatabaseConfig
import DatabaseControl
import money_system
import gtts
import sr_api
import asuna_api

async def status_task():
  while True:
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="JDBot has returned"))
    await asyncio.sleep(40)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="New updates coming soon.."))
    await asyncio.sleep(40)

async def startup():
  await client.wait_until_ready()
  #client.lavalink=await asyncio.create_subprocess_shell('java -jar Lavalink.jar')
  await status_task()

logging.basicConfig(level=logging.WARNING)
ratelimit_detection=logging.Filter(name='WARNING:discord.http:We are being rate limited.')

client = ClientConfig.client

class BetterMemberConverter(commands.Converter):
  async def convert(self,ctx,argument):
    try:
      user = await commands.MemberConverter().convert(ctx,argument)
    except commands.MemberNotFound:
      user = None

    if user == None:
      tag = re.match(r"#?(\d{4})",argument)
      if tag:
        if ctx.guild:
          test=discord.utils.get(ctx.guild.members, discriminator = tag.group(1))
          if test:
            user = test
          if not test:
            user=ctx.author
        if ctx.guild is None:
          user = await BetterUserconverter().convert(ctx,argument)
          if user:
            user = client.get_user(user.id)
          if user is None:
            user = ctx.author
            
          
    return user

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

async def triggered_converter(url,ctx):
  sr_client=sr_api.Client()
  source_image=sr_client.filter(option="triggered",url=str(url))
  image = BytesIO(await source_image.read())
  await sr_client.close()

  file=discord.File(image, "triggered.gif")
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url="attachment://triggered.gif")
  embed.set_footer(text="powered by some random api")
  await ctx.send(file=file,embed=embed)

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

@client.command(help="a command meant to flips coins",brief="commands to flip coins, etc.")
async def coin(ctx, *, args = None):
  if args:
    value = random.choice([True,False]) 
    if args.lower().startswith("h") and value:
      win = True
    elif args.lower().startswith("t") and not value:
      win = True
    elif args.lower().startswith("h") and not value:
      win = False
    elif args.lower().startswith("t") and value:
      win = False    
    else:
      await ctx.send("Please use heads or Tails as a value.")
      return
    
    if(value):
      pic_name = "heads"
    else:
      pic_name ="Tails"

    url_dic = {"heads":"https://i.imgur.com/MzdU5Z7.png","Tails":"https://i.imgur.com/qTf1owU.png"}

    embed = discord.Embed(title="coin flip",color=random.randint(0, 16777215))
    embed.set_author(name=f"{ctx.author}",icon_url=(ctx.author.avatar_url))
    embed.add_field(name="The Coin Flipped: "+("heads" if value else "tails"),value=f"You guessed: {args}")
    embed.set_image(url=url_dic[pic_name])

    if win:
      embed.add_field(name="Result: ",value="Won")
    else:
      embed.add_field(name="Result: ",value="Lost")
    
    await ctx.send(embed=embed)


  if args is None:
    await ctx.send("example: ```\ntest*coin heads \nnot test*coin```")

@client.command(help="a command to talk to Google TTS",brief="using the power of the GTTS module you can now do tts")
async def tts(ctx,*,args=None):
  if args:
    mp3_fp = BytesIO()
    tts=gtts.gTTS(text=args,lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    file = discord.File(mp3_fp,"tts.mp3")
    await ctx.send(file=file)
  
  if args is None:
    await ctx.send("You didn't specify any value.")

@client.command(help="repeats what you say",brief="a command that repeats what you say the orginal message is deleted")
async def say(ctx,*,args=None):
  if args:
    await ctx.send(args)

@client.command()
async def triggered(ctx):
  y = 0
  if len(ctx.message.attachments) > 0:
    for x in ctx.message.attachments:
      if x.filename.endswith(".png"):
        url = x.url
        await triggered_converter(url,ctx)
        y = y + 1
      if not x.filename.endswith(".png"):
        pass

  if len(ctx.message.attachments) == 0 or y == 0:
    url = ctx.author.avatar_url_as(format="png")
    await triggered_converter(url,ctx)

@client.command(help= "a command to slap someone",brief="this sends slap gifs to the target user")
async def slap(ctx,*, Member: BetterMemberConverter = None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  asuna = asuna_api.Client()
  url = await asuna.get_gif("slap")
  await asuna.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} slapped you",icon_url=(person.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")

  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")


@client.command(help="a command to look up foxes",brief="this known as wholesome fox to the asuna api")
async def fox2(ctx):
  asuna = asuna_api.Client()
  url = await asuna.get_gif("wholesome_foxes")
  await asuna.close()
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{ctx.author} requested a wholesome fox picture",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  await ctx.send(embed=embed)

@client.command(help="another command to give you pat gifs",brief="powered using the asuna api")
async def pat2(ctx,*, Member: BetterMemberConverter= None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  asuna = asuna_api.Client()
  url = await asuna.get_gif("pat")
  await asuna.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} patted you",icon_url=(person.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")


@client.command(help="a command to give you pat gifs",brief="using the sra api it gives you pat gifs")
async def pat(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
    
  sr_client=sr_api.Client()
  image=await sr_client.get_gif("pat")
  await sr_client.close()
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} patted you",icon_url=(person.avatar_url))
  embed.set_image(url=image.url)
  embed.set_footer(text="powered by some random api")
    
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")
  

@client.command(help="a hug command to hug people",brief="this the first command to hug.")
async def hug(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member

  sr_client=sr_api.Client()
  image=await sr_client.get_gif("hug")
  await sr_client.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} hugged you",icon_url=(person.avatar_url))
  embed.set_image(url=image.url)
  embed.set_footer(text="powered by some random api")
  
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")


@client.command(help="a hug command to hug people",brief="this actually the second hug command and is quite powerful.")
async def hug2(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  asuna = asuna_api.Client()
  url = await asuna.get_gif("hug")
  await asuna.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} hugged you",icon_url=(person.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")

def warn_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.administrator

  if isinstance(ctx.channel,discord.DMChannel):
    return True

@client.command()
async def spam(ctx):
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_image(url="https://i.imgur.com/1LckTTu.gif")
  await ctx.send(content="I hate spam",embed=embed)

@client.command()
async def warn(ctx,Member: BetterMemberConverter = None):
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
    await client.get_channel(738912143679946783).send(embed=embed) 

    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()

    try:
      await ctx.author.send(content=f"Why did you warn {Member}?")
    except discord.Forbidden:
      await ctx.send("we can't DM them :(")

  if warn_permission(ctx) is False:
    await ctx.send("You don't have permission to use that.")


@client.command(help="a kiss command",brief="a command where you can target a user or pick yourself to get a kiss gif( I don't know why I have this)")
async def kiss(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  asuna = asuna_api.Client()
  url = await asuna.get_gif("kiss")
  await asuna.close()
        
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} kissed you",icon_url=(person.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="Why did I make this command? powered using the asuna.ga api")
  
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")

@client.command(help="a command to get a neko",brief="using the asuna.ga api you will get these images")
async def neko(ctx):
  asuna = asuna_api.Client()
  url = await asuna.get_gif("neko")
  await asuna.close()
  
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{ctx.author} requested a neko picture",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  await ctx.send(embed=embed)

@client.command()
async def work(ctx,*,args=None):
  Member = ctx.author.id
  if args is None:
    money_system.add_money(Member,10,0)

@client.command(help="a command to send how much money you have",brief="using the JDBot database you can see how much money you have")
async def balance(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
  money_system.display_account(Member.id)

@client.command(help="a command to send wink gifs",brief="you select a user to send it to and it will send it to you lol")
async def wink(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  sr_client=sr_api.Client()
  image=await sr_client.get_gif("wink")
  await sr_client.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{person} winked at you",icon_url=(person.avatar_url))
  embed.set_image(url=image.url)
  embed.set_footer(text="powered by some random api")

  if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")

@client.command(help="a command to send facepalm gifs",brief="using some random api it sends you a facepalm gif lol")
async def facepalm(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
    
  if Member.id == ctx.author.id:
    person = client.user
    target = ctx.author
  
  if Member.id != ctx.author.id:
    person = ctx.author
    target = Member
  
  sr_client=sr_api.Client()
  image=await sr_client.get_gif("face-palm")
  await sr_client.close()

  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{target} you made {person} facepalm",icon_url=(person.avatar_url))
  embed.set_image(url=image.url)
  embed.set_footer(text="powered by some random api")
  
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=target.mention,embed=embed) 

  if isinstance(ctx.channel,discord.DMChannel):
    if target.dm_channel is None:
      await target.create_dm()
    
    try:
      await target.send(content=target.mention,embed=embed)
    except discord.Forbidden:
      await ctx.author.send("Failed Dming them...")

@client.command()
async def webhook_update(ctx,*,args=None):
  if await client.is_owner(ctx.author):
    if args:

      if isinstance(ctx.channel, discord.TextChannel):
        await ctx.message.delete()

      async with aiohttp.ClientSession() as session:
        webhook=discord.Webhook.from_url(os.environ["webhook1"], adapter=discord.AsyncWebhookAdapter(session))
        embed=discord.Embed(title="Update",color=(35056),timestamp=(ctx.message.created_at))
        embed.add_field(name="Update Info:",value=args)
        embed.set_author(name="JDJG's Update",icon_url='https://i.imgur.com/pdQkCBv.png')
        embed.set_footer(text="JDJG's Updates")
        await webhook.execute(embed=embed)
      
      async with aiohttp.ClientSession() as session:
        webhook=discord.Webhook.from_url(os.environ["webhook99"], adapter=discord.AsyncWebhookAdapter(session))
        embed=discord.Embed(title="Update",color=(35056),timestamp=(ctx.message.created_at))
        embed.add_field(name="Update Info:",value=args)
        embed.set_author(name="JDJG's Update",icon_url='https://i.imgur.com/pdQkCBv.png')
        embed.set_footer(text="JDJG's Updates")
        await webhook.execute(embed=embed)
    if args is None:
      await ctx.send("You sadly can't use it like that.")
  if await client.is_owner(ctx.author) is False:
    await ctx.send("You can't use that")

@client.command()
async def webhook_create(ctx,arg=None,*,args=None):
  if isinstance(ctx.channel, discord.TextChannel):
    if ctx.author.guild_permissions.manage_webhooks:
      if arg:
        if args is None:
          webhook=await ctx.channel.create_webhook(name=arg)
          embed = discord.Embed(title=f"{ctx.author}'s message:",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
          embed.add_field(name="Content:",value="Test")
        if args:
          webhook=await ctx.channel.create_webhook(name=arg,reason=args)
          embed = discord.Embed(title=f"{ctx.author}'s message:",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
          embed.add_field(name="Content:",value=args)

        if len(ctx.message.attachments) > 0:
          image=await ctx.message.attachments[0].read()
          pass_test = True
          try:
            discord.utils._get_mime_type_for_image(image)
          except discord.errors.InvalidArgument:
            pass_test = False
          
          if pass_test:
            await webhook.edit(avatar=image)
          if pass_test is False:
            await ctx.send("not a valid image")
        
        await webhook.execute(embed=embed)
        
        if (ctx.author.dm_channel is None):
          await ctx.author.create_dm()

        try:
          await ctx.author.send("Webhook url coming up")
          await ctx.author.send(webhook.url)
        except discord.Forbidden:
          await ctx.send(f"We couldn't DM you {ctx.author.mention}")
          
      if arg is None:
        await ctx.send("You need to use values for it to work")
    if ctx.author.guild_permissions.manage_webhooks is False:
      await ctx.send("you can't use that.")
      

  if isinstance(ctx.channel, discord.DMChannel):
    await ctx.send("You can't use that silly")

@client.command()
async def webhook(ctx,*,args=None):
  if args is None:
    await ctx.send("You didn't send anything")

  if args:
    check=re.match(r"https://discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,21})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})",args)
    if check:
      args = args.replace(f"{check.group()} ","")
      if args == check.group():
        args = "No Content"

      async with aiohttp.ClientSession() as session:
        async with session.get(check.group()) as response:
          if response.status == 200:
            webhook=discord.Webhook.from_url(check.group(), adapter=discord.AsyncWebhookAdapter(session))
            
            embed = discord.Embed(title=f"Webhook {webhook.name}'s Message",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value=args)
            await webhook.execute(embed=embed)

          if response.status != 200:
            await ctx.send("Not a valid link or an error occured")

      if isinstance(ctx.channel, discord.TextChannel):
        await ctx.message.delete()

  

@client.command(help="a way to look up minecraft usernames",brief="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)")
async def mchistory(ctx,*,args=None):
  if not args:
    await ctx.send("Please pick a minecraft user.")
  if args:
    async with aiohttp.ClientSession() as cs:
      async with cs.get(f'https://api.mojang.com/users/profiles/minecraft/{args}') as r:
        if r.status == 200:
          user_dict=await r.json()
          minecraft_uuid=user_dict["id"]
          async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.mojang.com/user/profiles/{minecraft_uuid}/names") as r:
              if r.status == 200:
                user_history=await r.json()

                y = 0
                for x in user_history:
                  if y == 0:
                    minecraft_username = x["name"]
                    embed=discord.Embed(title=f"Minecraft Username: {args}",color=random.randint(0, 16777215))
                    embed.set_footer(text=f"Minecraft UUID: {minecraft_uuid}")
                    embed.add_field(name="Orginal Name:",value=minecraft_username)

                  if y > 0:
                    username = (x["name"])
                    date_changed=datetime.datetime.utcfromtimestamp(int(x["changedToAt"])/1000).strftime("%m/%d/%Y")
                    time_changed=datetime.datetime.utcfromtimestamp(int(x["changedToAt"])/1000).strftime("%H:%M:%S")
                    embed.add_field(name=f"Username:\n{username}",value=f"Date Changed:\n{date_changed}\n  \nTime Changed: \n {time_changed}")

                  y = y + 1
                
                embed.set_author(name=f"Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
                await ctx.send(embed=embed)

              if r.status == 500:
                await ctx.send("Internal server error occured at Mojang. We're sorry :( ")
                     
        if not r.status == 200:
          await ctx.send("It doesn't like it didn't find the user.")

@client.command(help="a command to get the avatar of a user",brief="using the userinfo technology it now powers avatar grabbing.")
async def avatar(ctx,*,user: BetterUserconverter = None): 
  if user is None:
    user = ctx.author
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{user.name}'s avatar:",icon_url=(user.avatar_url))
  embed.set_image(url=(user.avatar_url))
  embed.set_footer(text=f"Requested by {ctx.author}")
  await ctx.send(embed=embed)

@client.command(help="gives you the milkman gif",brief="you summoned the milkman oh no")
async def milk(ctx):
  embed = discord.Embed(title="You have summoned the milkman",color=random.randint(0, 16777215))
  embed.set_image(url="https://i.imgur.com/JdyaI1Y.gif")
  embed.set_footer(text="his milk is delicious")
  await ctx.send(embed=embed)

@client.command(help="a command that gives information on users",brief="this can work with mentions, ids, usernames, and even full names.")
async def userinfo(ctx,*,user: BetterUserconverter = None):
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
    embed_message.set_thumbnail(url = "https://i.imgur.com/ugKZ7lW.png")
    channel_usage=client.get_channel(738912143679946783)
    embed_message.add_field(name="Sent To:",value=str(channel_usage))
    await channel_usage.send(embed=embed_message)
  
  test=await client.get_context(message)
  if (test.valid) == False:
    if test.prefix != None and not client.user.mentioned_in(message):
      if test.command == None:
        time_used=(message.created_at).strftime('%m/%d/%Y %H:%M:%S')
        embed_message = discord.Embed(title=f" {message.content}", description=time_used,color=random.randint(0, 16777215))
        embed_message.set_author(name=f"{message.author} tried to excute invalid command:",icon_url=(message.author.avatar_url))
        embed_message.set_footer(text = f"{message.author.id}")
        embed_message.set_thumbnail(url="https://i.imgur.com/bW6ergl.png")
        await client.get_channel(738912143679946783).send(embed=embed_message)
  
  await client.process_commands(message) 

@client.event
async def on_error(event,*args,**kwargs):
  import traceback
  more_information=os.sys.exc_info()
  error_wanted=traceback.format_exc()
  traceback.print_exc()
  
  #print(more_information[0])


B.b()

client.loop.create_task(startup())
client.run(os.environ["classic_token"])
