import aioimgur
import discord
import random
import sr_api
import os

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

def warn_permission(ctx):
  if isinstance(ctx.channel, discord.TextChannel):
    return ctx.author.guild_permissions.manage_messages

  if isinstance(ctx.channel,discord.DMChannel):
    return True

async def invert_converter(url,ctx):
  sr_client=sr_api.Client(key=os.environ["sr_key"])
  source_image=sr_client.filter("invert",url=str(url))
  image = await source_image.read()
  await sr_client.close()

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

