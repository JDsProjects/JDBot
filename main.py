import discord
from discord.ext import commands, tasks
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
import io
import DatabaseConfig
import DatabaseControl
import money_system
import gtts
import sr_api
import asuna_api
import aioimgur
import chardet
import mystbin
from difflib import SequenceMatcher
import time

async def status_task():
  while True:
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="the return of JDBot"))
    await asyncio.sleep(40)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers | {len(client.users)} users"))
    await asyncio.sleep(40)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the new updates coming soon..."))
    await asyncio.sleep(40)

async def startup():
  await client.wait_until_ready()
  await status_task()

logging.basicConfig(level=logging.INFO)

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

      match2 = re.match(r'<@&([0-9]+)>$',argument)
      if match2:
        argument2=match2.group(1)
        role=ctx.guild.get_role(int(argument2))
        if role.is_bot_managed:
            user=role.tags.bot_id
            user = client.get_user(user)
            if user is None:
              user = await client.fetch_user(user)

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
  await sr_client.close()

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url= await imgur_client.upload_from_url(source_image.url)

  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

@client.command(brief="sends pong and the time it took to do so.")
async def ping(ctx):
  await ctx.send("Pong")
  await ctx.send(f"Response time: {client.latency*1000}")

@client.command(brief="gives you the digits of pi that Python knows")
async def pi(ctx):
  await ctx.send(math.pi)

@client.event
async def on_ready():
  print("Bot is Ready")
  print(f"Logged in as {client.user}")
  print(f"Id: {client.user.id}")

@client.command(brief="a command meant to flip coins",help="commands to flip coins, etc.")
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
      embed.add_field(name="Result: ",value="You won")
    else:
      embed.add_field(name="Result: ",value="You lost")
    
    await ctx.send(embed=embed)

  if args is None:
    await ctx.send("example: \n```test*coin heads``` \nnot ```test*coin```")

@client.command(brief="gives info about a file")
async def file(ctx):
  if len(ctx.message.attachments) < 1:
    await ctx.send(ctx.message.attachments)
    await ctx.send("no file submitted")
  if len(ctx.message.attachments) > 0:
    embed = discord.Embed(title="Attachment info",color=random.randint(0, 16777215))
    for x in ctx.message.attachments:
      embed.add_field(name=f"ID: {x.id}",value=f"[{x.filename}]({x.url})")
      embed.set_footer(text="Check on the url/urls to get a direct download to the url.")
    await ctx.send(embed=embed,content="\nThat's good")

@client.command(brief="reverses text")
async def reverse(ctx,*,args=None):
  if args:
    await ctx.send(args[::-1])
  if args is None:
    await ctx.send("Try sending actual to reverse")

@client.command(brief="gives you an invite to invite the bot.")
async def invite(ctx):
  embed = discord.Embed(title="Invite link:",color=random.randint(0, 16777215))
  embed.add_field(name="JDBot invite:",value=f"[JDBot invite url](https://discord.com/oauth2/authorize?client_id={client.user.id}&scope=bot&permissions=8)")
  embed.add_field(name="Non Markdowned invite",value=f"https://discord.com/oauth2/authorize?client_id={client.user.id}&scope=bot&permissions=8")
  embed.set_thumbnail(url=client.user.avatar_url)
  await ctx.send(embed=embed)

@client.command(brief="gives you who the owner is.")
async def owner(ctx):
  info = await client.application_info()
  if info.team is None:
    owner = info.owner.id
  if info.team:
    owner = info.team.owner_id

  support_guild=client.get_guild(736422329399246990)
  owner=support_guild.get_member(owner)
  if owner.bot:
    user_type = "Bot"
  if not owner.bot:
    user_type = "User"

  guilds_list=[guild for guild in client.guilds if guild.get_member(owner.id)]
  if not guilds_list:
    guild_list = "None"

  x = 0
  for g in guilds_list:
    if x < 1:
      guild_list = g.name
    if x > 0:
      guild_list = guild_list + f", {g.name}"
    x = x + 1
  
  if owner:
    nickname = str(owner.nick)
    joined_guild = owner.joined_at.strftime('%m/%d/%Y %H:%M:%S')
    status = str(owner.status).upper()
    highest_role = owner.roles[-1]
  
  if owner is None:
    nickname = "None"
    joined_guild = "N/A"
    status = "Unknown"
    for guild in client.guilds:
      member=guild.get_member(owner.id)
      if member:
        status=str(member.status).upper()
        break
    highest_role = "None Found"
  
  embed=discord.Embed(title=f"Bot Owner: {owner}",description=f"Type: {user_type}", color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
  embed.add_field(name="Username:", value = owner.name)
  embed.add_field(name="Discriminator:",value=owner.discriminator)
  embed.add_field(name="Nickname: ", value = nickname)
  embed.add_field(name="Joined Discord: ",value = (owner.created_at.strftime('%m/%d/%Y %H:%M:%S')))
  embed.add_field(name="Joined Guild: ",value = joined_guild)
  embed.add_field(name="Part of Guilds:", value=guild_list)
  embed.add_field(name="ID:",value=owner.id)
  embed.add_field(name="Status:",value=status)
  embed.add_field(name="Highest Role:",value=highest_role)
  embed.set_image(url=owner.avatar_url)
  await ctx.send(embed=embed)

@client.command(brief="a command to find the nearest emoji")
async def emote(ctx,*,args=None):
  if args is None:
    await ctx.send("Please specify an emote")
  if args:
    emoji=discord.utils.get(client.emojis,name=args)
    if emoji is None:
      await ctx.send("we haven't found anything")
    if emoji:
      await ctx.send(emoji)

@client.command(help="a different method to find the nearest emoji")
async def emote2(ctx,*,args=None):
  if args is None:
    await ctx.send("Please specify an emote")
  if args:
    emoji = sorted(client.emojis, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]

    if emoji is None:
      await ctx.send("we haven't found anything")
    if emoji:
      await ctx.send(emoji)

@client.command(brief="this is a way to get the nearest channel.")
async def closest_channel(ctx,*,args=None):
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

@client.command(brief="a command to get the closest user.")
async def closest_user(ctx,*,args=None):
  if args is None:
    await ctx.send("please specify a user")
  if args:
    userNearest = discord.utils.get(client.users,name=args)
    user_nick = discord.utils.get(client.users,display_name=args)
    if userNearest is None:
      userNearest = sorted(client.users, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]
    if user_nick is None:
      user_nick = sorted(client.users, key=lambda x: SequenceMatcher(None, x.display_name,args).ratio())[-1]
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

@client.command(brief="a command to tell you the channel id")
async def this(ctx):
  await ctx.send(ctx.channel.id)

@client.group(name="open",invoke_without_command=True)
async def source(ctx):
  embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot.",color=random.randint(0, 16777215))
  embed.set_author(name=f"{client.user}'s source code:",icon_url=(client.user.avatar_url))
  await ctx.send(embed=embed)

@client.command(brief="a way to view open source",help="you can see the open source with the link it provides")
async def open_source(ctx):
  embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot.",color=random.randint(0, 16777215))
  embed.set_author(name=f"{client.user}'s source code:",icon_url=(client.user.avatar_url))
  await ctx.send(embed=embed)

@client.command(brief="a command to email you(work in progress)",help="This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary")
async def email(ctx,*args):
  print(args)

@client.command(brief="a magic 8ball command",aliases=["8ball"])
async def _8ball(ctx,*,args=None):
  if args is None:
    await ctx.send("Please give us a value to work with.")
  if args:
    responses = ["As I see it, yes.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don’t count on it.","It is certain.","It is decidedly so.","Most likely.","My reply is no.","My sources say no.","Outlook not so good.","Outlook good.","Reply hazy, try again.","Signs point to yes.","Very doubtful.","Without a doubt.","Yes.","Yes – definitely.","You may rely on it."]
    await ctx.send(random.choice(responses))

#@client.command(brief="a command to send mail")
#async def mail(ctx,*,user: discord.User=None,args=None):
  #print(user)
  #print(args)

@client.command(brief="Only owner command to change bot's nickname")
async def change_nick(ctx,*,name=None):
  if await client.is_owner(ctx.author):
    if isinstance(ctx.channel, discord.TextChannel):
      await ctx.send("Changing Nickname")
      try:
        await ctx.guild.me.edit(nick=name)
      except discord.Forbidden:
        await ctx.send("Appears not to have valid perms")
    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("You can't use that in Dms.")
    
  if await client.is_owner(ctx.author) is False:
    await ctx.send("You can't use that command")

@client.command(brief="a command to backup text",help="please don't upload any private files that aren't meant to be seen")
async def text_backup(ctx):
  if ctx.message.attachments:
    for x in ctx.message.attachments:
      file=await x.read()
      if len(file) > 0:
        encoding=chardet.detect(file)["encoding"]
        if encoding:
          text = file.decode(encoding)
          mystbin_client = mystbin.Client()
          paste = await mystbin_client.post(text)
          await ctx.send(content=f"Added text file to mystbin: \n{paste.url}")
          await mystbin_client.close()
        if encoding is None:
          await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439 or it wasn't a text file.")
      if len(file ) < 1:
        await ctx.send("this doesn't contain any bytes.")

@client.command(brief="Oh no Dad Jokes, AHHHHHH!")
async def dadjoke(ctx):
  async with aiohttp.ClientSession() as session:
    async with session.get("https://icanhazdadjoke.com/",headers={"Accept": "application/json"}) as response:
      joke=await response.json()
  embed = discord.Embed(title="Random Dad Joke:",color=random.randint(0, 16777215))
  embed.set_author(name=f"Dad Joke Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.add_field(name="Dad Joke:",value=joke["joke"])
  embed.set_footer(text=f"View here:\n https://icanhazdadjoke.com/j/{joke['id']}")
  await ctx.send(embed=embed)

@client.command(brief="gets a panel from the xkcd comic",aliases=["astrojoke","astro_joke"])
async def xkcd(ctx):
  async with aiohttp.ClientSession() as session:
    async with session.get("https://xkcd.com/info.0.json") as response:
      info=await response.json()

  num = random.randint(1,info["num"])
  async with aiohttp.ClientSession() as session:
    async with session.get(f"https://xkcd.com/{num}/info.0.json") as comic:
      data=await comic.json()
      title = data["title"]
      embed=discord.Embed(title=f"Title: {title}",color=random.randint(0, 16777215))
      embed.set_image(url=data["img"])
      embed.set_footer(text=f"Made on {data['month']}/{data['day']}/{data['year']}")
      await ctx.send(embed=embed)

@client.command(brief="a set of rules we will follow")
async def promise(ctx):
  embed=discord.Embed(title="Promises we will follow:",color=random.randint(0, 16777215))
  embed.add_field(name="Rule 1:",value="if you are worried about what the bot may collect, please send a DM to the bot, and we will try to compile the data the bot may have on you.")
  embed.add_field(name="Rule 2:",value="in order to make sure our bot is safe, we will be making sure the token is secure and making sure anyone who works on the project is very trustworthy.")
  embed.add_field(name="Rule 3:",value="we will not nuke your servers, as this happened to us before and we absolutely hated it.")
  embed.add_field(name="Rule 4:",value="We will also give you a list of suspicious people")
  embed.add_field(name="Rule 5:",value="we also made sure our code is open source so you can see what it does.")
  embed.add_field(name="Rule 6:",value="We will also let you ask us questions directly, just DM me directly(the owner is listed in the owner command(and anyone should be able to friend me)")
  await ctx.send(embed=embed)

@client.command(brief="a command that can scan urls(work in progress), and files",help="please don't upload anything secret or send any secret url thank you :D")
async def scan(ctx, *, args = None):
  import vt
  vt_client = vt.Client(os.environ["virustotal_key"])
  used = None
  if args:
    used = True
    urls=re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",args)
    for x in urls:
      print(x)

  if len(ctx.message.attachments) > 0:
    await ctx.send("If this takes a while, it probably means it was never on Virustotal before")
    used = True
  for x in ctx.message.attachments:
    analysis = await vt_client.scan_file_async(await x.read(),wait_for_completion=True)
    object_info = await vt_client.get_object_async("/analyses/{}", analysis.id)
  
  if used:
    await ctx.send(content="Scan completed")
  await vt_client.close_async()

@client.command(help="a command to scan for malicious bots, specificially ones that only give you random invites and are fake(work in progress)")
async def scan_guild(ctx):
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

@client.command(help="a way to report a user, who might appear in the sus list. also please provide ids and reasons. (work in progress")
async def report(ctx,*,args=None):
  if args:
    jdjg = client.get_user(168422909482762240)
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

@client.command(help="learn about a secret custom xbox controller",brief="this will give you a message of JDJG's classic wanted xbox design.")
async def secret_controller(ctx):
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name="Secret Xbox Image:")
  embed.add_field(name="Body:",value="Zest Orange")
  embed.add_field(name="Back:",value="Zest Orange")
  embed.add_field(name="Bumpers:",value="Zest Orange")
  embed.add_field(name="Triggers:",value="Zest Orange")
  embed.add_field(name="D-pad:",value="Electric Green")
  embed.add_field(name="Thumbsticks:",value="Electric Green")
  embed.add_field(name="ABXY:",value="Colors on Black")
  embed.add_field(name="View & Menu:",value="White on Black")
  embed.add_field(name="Engraving(not suggested):",value="JDJG Inc.")
  embed.add_field(name="Disclaimer:",value="I do not work at microsoft,or suggest you buy this I just wanted a place to represent a controller that I designed a while back.")
  embed.set_image(url="https://i.imgur.com/QCh4M2W.png")
  embed.set_footer(text="This is Xbox's custom controller design that I picked for myself.\nXbox is owned by Microsoft. I don't own the image")
  await ctx.send(embed=embed)

@client.command(help="Gives advice from JDJG api.",aliases=["ad"])
async def advice(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/advice') as r:
      res = await r.json()
  embed = discord.Embed(title = "Here is some advice for you!",color=random.randint(0, 16777215))
  embed.add_field(name = f"{res['text']}", value = "Hopefully this helped!")
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives a random objection",aliases=["obj","ob","object"])
async def objection(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/objection') as r:
        res = await r.json()
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{ctx.author} yelled OBJECTION!",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=res["url"])
  embed.set_footer(text="Powered By JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives random compliment")
async def compliment(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/compliment') as r:
      res = await r.json()
  embed = discord.Embed(title = "Here is a compliment:",color=random.randint(0, 16777215))
  embed.add_field(name = f"{res['text']}", value = "Hopefully this helped your day!")
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives an insult")
async def insult(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/insult') as r:
      res = await r.json()
  embed = discord.Embed(title = "Here is a insult:",color=random.randint(0, 16777215))
  embed.add_field(name = f"{res['text']}", value = "Hopefully this Helped?")
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives response to slur")
async def noslur(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/noslur') as r:
      res = await r.json()
  embed = discord.Embed(title = "Don't Swear",color=random.randint(0, 16777215))
  embed.add_field(name = f"{res['text']}", value = "WHY MUST YOU SWEAR?")
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives the truth about opinions(may offend)",aliases=["opinion"])
async def opinional(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/opinional') as r:
      res = await r.json()
  embed = discord.Embed(title = "Truth about opinions(may offend some people):",color=random.randint(0, 16777215))
  embed.set_image(url=res["url"])
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="gives random message",aliases=["rm"])
async def random_message(ctx):
  async with aiohttp.ClientSession() as cs:
    async with cs.get('https://jdjgapi.nom.mu/api/randomMessage') as r:
      res = await r.json()
  embed = discord.Embed(title = "Random Message:",color=random.randint(0, 16777215))
  embed.add_field(name="Here:",value=res["text"])
  embed.set_footer(text="Powered by JDJG Api!")
  await ctx.send(embed=embed)

@client.command(help="emojis command(work in progress)")
async def emoji(ctx,*emojis: typing.Union[discord.PartialEmoji, str]):
  for x in emojis:
    if isinstance(x,discord.PartialEmoji):
      embed = discord.Embed(title=f"Emoji: **{x.name}**",color=random.randint(0, 16777215))
      embed.set_image(url=x.url)
      embed.set_footer(text=f"Emoji ID:{x.id}")
      await ctx.send(embed=embed)
    else:
      pass
  if len(emojis) < 1:
    await ctx.send("Looks like there was no emojis.")

@client.command(help="fetch invite details")
async def fetch_invite(ctx,*invites:typing.Union[discord.Invite, str]):
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

async def headpat_converter(url,ctx):
  sr_client=sr_api.Client(key=os.environ["sr_key"])
  source_image=sr_client.petpet(avatar=str(url))
  image = await source_image.read()
  await sr_client.close()

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

@client.command(brief="uses our headpat program to pat you",help="a command that uses sra_api to make a headpat of you.")
async def headpat2(ctx):
  y = 0
  if len(ctx.message.attachments) > 0:
    for x in ctx.message.attachments:
      if x.filename.endswith(".png"):
        url = x.url
        await headpat_converter(url,ctx)
        y = y + 1
      if not x.filename.endswith(".png"):
        pass

  if len(ctx.message.attachments) == 0 or y == 0:
    url = ctx.author.avatar_url_as(format="png")
    await headpat_converter(url,ctx)

@client.command(brief="uploads your emojis into a mystbin link")
async def look_at(ctx):
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

@client.command(brief="a command to give a list of servers(owner only)",help="Gives a list of guilds(Bot Owners only)")
async def servers(ctx):
  if await client.is_owner(ctx.author):
    send_list = [""]
    guild_list = ["%d %s %d %s" % (len(g.members), g.name, g.id, (g.system_channel or g.text_channels[0]).mention) for g in client.guilds]
    for i in guild_list:
      if len(send_list[-1] + i) < 1000:
        send_list[-1] += i + "\n"
      else:
        send_list += [i + "\n"]
    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()
    await ctx.author.dm_channel.send("\n Servers:")
    for i in send_list:
      await ctx.author.dm_channel.send(i) 
  if await client.is_owner(ctx.author) is False:
    await ctx.send("You can't use that it's owner only")

@client.group(name="apply",invoke_without_command=True)
async def apply(ctx):
  await ctx.send("this command is meant to apply")

@apply.command(brief="a command to apply for our Bloopers.",help="a command to apply for our bloopers.")
async def bloopers(ctx,*,args=None):
  if args is None:
    await ctx.send("You didn't give us any info.")
  if args:
    if isinstance(ctx.message.channel, discord.TextChannel):
      await ctx.message.delete()

    for x in [708167737381486614,168422909482762240]:
      apply_user = client.get_user(x)
    
    if (apply_user.dm_channel is None):
      await apply_user.create_dm()
    
    embed_message = discord.Embed(title=args,color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
    embed_message.set_author(name=f"Application from {ctx.author}",icon_url=(ctx.author.avatar_url))
    embed_message.set_footer(text = f"{ctx.author.id}")
    embed_message.set_thumbnail(url="https://i.imgur.com/PfWlEd5.png")
    await apply_user.send(embed=embed_message)  

@client.command(help="gives the id of the current guild or DM if you are in one.")
async def guild_get(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    await ctx.send(content=ctx.guild.id) 

  if isinstance(ctx.channel,discord.DMChannel):
    await ctx.send(ctx.channel.id)

@client.command(help="a command to give information about the team",brief="this command works if you are in team otherwise it will just give the owner.")
async def team(ctx):
  information=await client.application_info()
  if information.team == None:
    true_owner=information.owner
    team_members = []
  if information.team != None:
    true_owner = information.team.owner
    team_members = information.team.members
  embed=discord.Embed(title=information.name,color=random.randint(0, 16777215))
  embed.add_field(name="Owner",value=true_owner)
  embed.set_footer(text=f"ID: {true_owner.id}")
  embed.set_image(url=(information.icon_url))
  for x in team_members:
    embed.add_field(name=x,value=x.id)
  await ctx.send(embed=embed)

@client.command(help="get the stats of users and members in the bot",brief="this is an alternative that just looking at the custom status time to time.")
async def stats(ctx):
  embed = discord.Embed(title="Bot stats",color=random.randint(0, 16777215))
  embed.add_field(name="Guild count",value=len(client.guilds))
  embed.add_field(name="User Count:",value=len(client.users))
  await ctx.send(embed=embed)

@client.command(help="This gives random history using Sp46's api.",brief="a command that uses SP46's api's random history command to give you random history responses")
async def random_history(ctx,*,args=None):
  if args is None:
    args = 1
  asuna = asuna_api.Client()
  response = await asuna.random_history(args)
  await asuna.close()
  for x in response:
    await ctx.send(f":earth_africa: {x}")

async def google_tts(ctx,text):
  await ctx.send("if you have a lot of text it may take a bit")
  mp3_fp = io.BytesIO()
  tts=gtts.gTTS(text=text,lang='en')
  tts.write_to_fp(mp3_fp)
  mp3_fp.seek(0)
  file = discord.File(mp3_fp,"tts.mp3")
  await ctx.send(file=file)

@client.command(help="a command to talk to Google TTS",brief="using the power of the GTTS module you can now do tts")
async def tts(ctx,*,args=None):
  if args:
    await google_tts(ctx,args)
  
  if ctx.message.attachments:
    for x in ctx.message.attachments:
      file=await x.read()
      if len(file) > 0:
        encoding=chardet.detect(file)["encoding"]
        if encoding:
          text = file.decode(encoding)
          await google_tts(ctx,text)
        if encoding is None:
          await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439")
      if len(file ) < 1:
        await ctx.send("this doesn't contain any bytes.")
        

  if args is None and len(ctx.message.attachments) < 1:
    await ctx.send("You didn't specify any value.")

@client.command(brief="repeats what you say",help="a command that repeats what you say the orginal message is deleted")
async def say(ctx,*,args=None):
  if args:
    args = discord.utils.escape_mentions(args)
    args=discord.utils.escape_markdown(args,as_needed=False,ignore_links=False)
    try:
      await ctx.message.delete()

    except discord.errors.Forbidden:
      pass

    await ctx.send(args)
  
  if args is None:
    await ctx.send("You didn't give us any text to use.")

@client.command(help="takes a .png attachment or your avatar and makes a triggered version.")
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

@client.command(brief="a command to slap someone",help="this sends a slap gif to the target user")
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
  embed.set_author(name=f"{person} slapped you! Ow...",icon_url=(person.avatar_url))
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
      await ctx.author.send("Failed DM'ing them...")


@client.command(brief="a command to look up foxes",help="this known as wholesome fox to the asuna api")
async def fox2(ctx):
  asuna = asuna_api.Client()
  url = await asuna.get_gif("wholesome_foxes")
  await asuna.close()
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{ctx.author} requested a wholesome fox picture",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  await ctx.send(embed=embed)

@client.command(brief="another command to give you pat gifs",help="powered using the asuna api")
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
  embed.set_author(name=f"{person} patted you! *pat pat pat*",icon_url=(person.avatar_url))
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
      await ctx.author.send("Failed DM'ing them...")


@client.command(brief="a command to give you pat gifs",help="using the sra api it gives you pat gifs")
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
  

@client.command(brief="a hug command to hug people",help="this the first command to hug.")
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
  embed.set_author(name=f"{person} hugged you! Awwww...",icon_url=(person.avatar_url))
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
      await ctx.author.send("Failed DM'ing them...")


@client.command(brief="a hug command to hug people",help="this actually the second hug command and is quite powerful.")
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
  embed.set_author(name=f"{person} super hugged you!",icon_url=(person.avatar_url))
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
      await ctx.author.send("Failed DM'ing them...")

def warn_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.administrator

  if isinstance(ctx.channel,discord.DMChannel):
    return True

@client.command(brief="a command to send I hate spam.")
async def spam(ctx):
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_image(url="https://i.imgur.com/1LckTTu.gif")
  await ctx.send(content="I hate spam.",embed=embed)

@client.command(brief="work in progress")
async def headpat(ctx):
  await ctx.send("Currently working in progress")

@client.command(brief="a command to warn people, but if you aren't admin it doesn't penalize.")
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


@client.command(brief="a kiss command",help="a command where you can target a user or pick yourself to get a kiss gif( I don't know why I have this)")
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

@client.command(brief="a command to get a neko",help="using the asuna.ga api you will get these images")
async def neko(ctx):
  asuna = asuna_api.Client()
  url = await asuna.get_gif("neko")
  await asuna.close()
  
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{ctx.author} requested a neko picture",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=url.url)
  embed.set_footer(text="powered using the asuna.ga api")
  await ctx.send(embed=embed)

@client.command(brief="Currently work in progress")
async def work(ctx,*,args=None):
  Member = ctx.author.id
  if args is None:
    money_system.add_money(Member,10,0)

@client.command(brief="a command to send how much money you have(work in progress)",help="using the JDBot database you can see how much money you have")
async def balance(ctx,*, Member: BetterMemberConverter=None):
  if Member is None:
    Member = ctx.author
  money_system.display_account(Member.id)

@client.command(brief="a command to send wink gifs",wink="you select a user to send it to and it will send it to you lol")
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

@client.command(brief="a command to send facepalm gifs",help="using some random api it sends you a facepalm gif lol")
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

@client.command(brief="only works with JDJG, but this command is meant to send updates to my webhook")
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

@client.command(brief="a way to create webhooks",help="make commands with this.")
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

@client.command(brief="a way to send stuff to webhooks.",help="this uses webhook urls, and sends stuff to them")
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
  

@client.command(brief="a way to look up minecraft usernames",help="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)")
async def mchistory(ctx,*,args=None):
  asuna = asuna_api.Client()
  minecraft_info=await asuna.mc_user(args)
  await asuna.close()
  
  if not args:
    await ctx.send("Please pick a minecraft user.")

  if args:
    embed=discord.Embed(title=f"Minecraft Username: {args}",color=random.randint(0, 16777215))
    embed.set_footer(text=f"Minecraft UUID: {minecraft_info.uuid}")
    embed.add_field(name="Orginal Name:",value=minecraft_info.name)
    y = 0
    for x in minecraft_info.history:
      if y > 0:
        embed.add_field(name=f"Username:\n{x['name']}",value=f"Date Changed:\n{x['changedToAt']}\n \nTime Changed: \n {x['timeChangedAt']}")

      y = y + 1
    embed.set_author(name=f"Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
    await ctx.send(embed=embed)

@client.command(brief="a command to get the avatar of a user",help="using the userinfo technology it now powers avatar grabbing.",aliases=["pfp",])
async def avatar(ctx,*,user: BetterUserconverter = None): 
  if user is None:
    user = ctx.author
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{user.name}'s avatar:",icon_url=(user.avatar_url))
  embed.set_image(url=(user.avatar_url))
  embed.set_footer(text=f"Requested by {ctx.author}")
  await ctx.send(embed=embed)

@client.command(brief="gives you the milkman gif",help="you summoned the milkman oh no")
async def milk(ctx):
  embed = discord.Embed(title="You have summoned the milkman",color=random.randint(0, 16777215))
  embed.set_image(url="https://i.imgur.com/JdyaI1Y.gif")
  embed.set_footer(text="his milk is delicious")
  await ctx.send(embed=embed)

async def guildinfo(ctx,guild):
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

@client.command(help="gives you info about a guild",aliases=["server_info","guild_fetch","guild_info","fetch_guild",])
async def serverinfo(ctx,*,args=None):
  if args:
    match=re.match(r'(\d{16,21})',args)
    guild=client.get_guild(int(match.group(0)))
    if guild is None:
      guild = ctx.guild

  if args is None:
    guild = ctx.guild
  
  await guildinfo(ctx,guild)

@client.command(aliases=["user info", "user_info","user-info"],brief="a command that gives information on users",help="this can work with mentions, ids, usernames, and even full names.")
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
  test=await client.get_context(message)

  if isinstance(message.channel, discord.DMChannel):
    if message.author.id != client.user.id and test.valid == False:
      time_used=(message.created_at).strftime('%m/%d/%Y %H:%M:%S')
      embed_message = discord.Embed(title=message.content, description=time_used, color=random.randint(0, 16777215))
      embed_message.set_author(name=f"Direct Message From {message.author}:",icon_url=(message.author.avatar_url))
      embed_message.set_footer(text = f"{message.author.id}")
      embed_message.set_thumbnail(url = "https://i.imgur.com/ugKZ7lW.png")
      channel_usage=client.get_channel(738912143679946783)
      embed_message.add_field(name="Sent To:",value=str(channel_usage))
      jdjg = client.get_user(168422909482762240)
      await channel_usage.send(content=jdjg.mention,embed=embed_message)

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
