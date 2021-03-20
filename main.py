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
import gtts
import chardet
import mystbin
from difflib import SequenceMatcher
import time
from utils import BetterMemberConverter, BetterUserconverter

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

@client.command(brief="sends pong and the time it took to do so.")
async def ping(ctx):
  start = time.perf_counter()
  message=await ctx.send("Pong")
  end = time.perf_counter()
  await message.edit(content=f"Pong\nBot Latency: {((end - start)*1000)} MS\nWebsocket Response time: {client.latency*1000} MS")

@client.command(brief="gives you the digits of pi that Python knows")
async def pi(ctx):
  await ctx.send(math.pi)

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
  await ctx.send("WIP")

@client.command(brief="Work in Progress")
async def status(ctx,*,args=None):
  if await client.is_owner(ctx.author):
    if args:
      pass
    if args is None:
      await client.change_presence(status=discord.Status.do_not_disturb)
  if await client.is_owner(ctx.author) is False:
    await ctx.send("That's an owner only command")

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
  await ctx.send("WIP")
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

def warn_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.administrator

  if isinstance(ctx.channel,discord.DMChannel):
    return True

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
  

@client.command(brief="a command to get the avatar of a user",help="using the userinfo technology it now powers avatar grabbing.",aliases=["pfp","av"])
async def avatar(ctx,*,user: BetterUserconverter = None): 
  if user is None:
    user = ctx.author
  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"{user.name}'s avatar:",icon_url=(user.avatar_url))
  embed.set_image(url=(user.avatar_url))
  embed.set_footer(text=f"Requested by {ctx.author}")
  await ctx.send(embed=embed)

B.b()
client.loop.create_task(startup())
client.run(os.environ["classic_token"])
