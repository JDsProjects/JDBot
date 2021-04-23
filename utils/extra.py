import aioimgur
import discord
import random
import sr_api
import os
import asyncdagpi

async def triggered_converter(self,url,ctx):
  sr_client=sr_api.Client(session=self.client.aiohttp_session)
  source_image=sr_client.filter(option="triggered",url=str(url))

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url= await imgur_client.upload_from_url(source_image.url)

  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter(self,url,ctx):
  sr_client=sr_api.Client(key=os.environ["sr_key"],session=self.client.aiohttp_session)
  source_image=sr_client.petpet(avatar=str(url))
  image = await source_image.read()

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

def warn_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages

  if isinstance(ctx.channel,discord.DMChannel):
    return True

async def invert_converter(self,url,ctx):
  sr_client=sr_api.Client(key=os.environ["sr_key"],session=self.client.aiohttp_session)
  source_image=sr_client.filter("invert",url=str(url))
  image = await source_image.read()

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter2(self,url,ctx):
  dagpi_client=asyncdagpi.Client(os.environ["dagpi_key"],session=self.client.aiohttp_session)
  image=await dagpi_client.image_process(asyncdagpi.ImageFeatures.petpet(),str(url))
  file = discord.File(fp=image.image,filename=f"headpat.{image.format}")
  await ctx.send(file=file)