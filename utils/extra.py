import aioimgur, discord, random, sr_api, asyncdagpi, aiogtts
import os, io

async def triggered_converter(self,url,ctx):
  sr_client=sr_api.Client(session=self.client.session)
  source_image=sr_client.filter(option="triggered",url=str(url))

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url= await imgur_client.upload_from_url(source_image.url)

  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter(self,url,ctx):
  try:
    sr_client=sr_api.Client(key=os.environ["sr_key"],session=self.client.session)
    source_image=sr_client.petpet(avatar=str(url))
    image = await source_image.read()
  except Exception as e:
    print(e)
    return await ctx.send("the api failed on us. Please contact the Bot owner if this is a perstient issue.")

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

def warn_permission(ctx, Member):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages and ctx.author.top_role.position > Member.top_role.position and ctx.author.top_role.permissions > Member.top_role.permissions

  if isinstance(ctx.channel,discord.DMChannel):
    return True

async def invert_converter(self,url,ctx):
  try:
    sr_client=sr_api.Client(key=os.environ["sr_key"],session=self.client.session)
    source_image=sr_client.filter("invert",url=str(url))
    image = await source_image.read()
  except:
    return await ctx.send("the api failed on us. Please contact the Bot owner if this is a perstient issue.")

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter2(self,url,ctx):
  dagpi_client=asyncdagpi.Client(os.environ["dagpi_key"],session=self.client.session)
  image=await dagpi_client.image_process(asyncdagpi.ImageFeatures.petpet(),str(url))
  file = discord.File(fp=image.image,filename=f"headpat.{image.format}")
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=f"attachment://headpat.{image.format}")
  embed.set_footer(text="powered by dagpi")
  await ctx.send(file=file,embed=embed)

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