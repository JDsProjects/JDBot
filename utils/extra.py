import aioimgur, discord, random, sr_api, asyncdagpi, aiogtts
import os, io, typing, datetime

async def triggered_converter(url, ctx):
  sr_client = sr_api.Client(session = ctx.bot.session)
  source_image=sr_client.filter(option="triggered", url = str(url))

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url= await imgur_client.upload_from_url(source_image.url)

  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.avatar.url))
  embed.set_image(url = imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter(url, ctx):
  try:
    sr_client = sr_api.Client(key=os.environ["sr_key"],session=ctx.bot.session)
    source_image=sr_client.petpet(avatar=str(url))
    image = await source_image.read()
  except Exception as e:
    print(e)
    return await ctx.send("the api failed on us. Please contact the Bot owner if this is a perstient issue.")

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar.url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

def warn_permission(ctx, Member):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages and ctx.author.top_role.position > Member.top_role.position and ctx.author.top_role.permissions > Member.top_role.permissions

  if isinstance(ctx.channel,discord.DMChannel):
    return True

def create_channel_permission(ctx):
  return ctx.author.guild_permissions.manage_channels

def clear_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages

  if isinstance(ctx.channel,discord.DMChannel):
    return False


async def invert_converter(url, ctx):
  try:
    sr_client = sr_api.Client(key=os.environ["sr_key"],session=ctx.bot.session)
    source_image = sr_client.filter("invert",url=str(url))
    image = await source_image.read()
  except:
    return await ctx.send("the api failed on us. Please contact the Bot owner if this is a perstient issue.")

  imgur_client = aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar.url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter2(url, ctx):
  dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session = ctx.bot.session)
  image=await dagpi_client.image_process(asyncdagpi.ImageFeatures.petpet(),str(url))
  file = discord.File(fp=image.image,filename=f"headpat.{image.format}")
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar.url))
  embed.set_image(url=f"attachment://headpat.{image.format}")
  embed.set_footer(text="powered by dagpi")
  await ctx.send(file=file, embed=embed)

async def google_tts(text):
  mp3_fp = io.BytesIO()
  tts=aiogtts.aiogTTS()
  await tts.write_to_fp(text,mp3_fp,lang='en')
  mp3_fp.seek(0)
  file = discord.File(mp3_fp,"tts.mp3")
  return file

async def latin_google_tts(text):
  mp3_fp = io.BytesIO()
  tts=aiogtts.aiogTTS()
  await tts.write_to_fp(text,mp3_fp,lang='la')
  mp3_fp.seek(0)
  file = discord.File(mp3_fp,"latin_tts.mp3")
  return file

def reference(message):

  reference = message.reference
  if reference and isinstance(reference.resolved, discord.Message):
    return reference.resolved.to_reference()

  return None


def cleanup_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages

  if isinstance(ctx.channel, discord.DMChannel):
    return True

def profile_converter(name):
  
  names_to_emojis = {
    "staff" : "<:staff:314068430787706880>",
    "partner" : "<:partnernew:754032603081998336>",
    "hypesquad" : "<:hypesquad:314068430854684672>",
    "bug_hunter" : "<:bughunter:585765206769139723>",
    "hypesquad_bravery" : "<:bravery:585763004218343426>",
    "hypesquad_brilliance" : "<:brilliance:585763004495298575>",
    "hypesquad_balance" : "<:balance:585763004574859273>",
    "early_supporter" : "<:supporter:585763690868113455> ",
    "system" : "<:system:863129934611349555><:system2:863129934633631774>",
    "bug_hunter_level_2" : "<:goldbughunter:853274684337946648>",
    "verified_bot" : "<:verified_bot:863128487610548304>",
    "verified_bot_developer" : "<:verifiedbotdev:853277205264859156>",
    "early_verified_bot_developer" : "<:verifiedbotdev:853277205264859156>",
    "discord_certified_moderator" : "<:certifiedmod:853274382339670046>",
    "bot" : "<:bot:863128982136684614>"
  }
  
  return names_to_emojis.get(name)