import collections, random, discord, aioimgur, sr_api, asyncdagpi
import os

async def guildinfo(ctx, guild):
  base_user = collections.Counter([u.bot for u in guild.members])
  bots = base_user[True]
  users = base_user[False]

  base_animated = collections.Counter([e.animated for e in guild.emojis])
  static_emojis = base_animated[False]
  animated_emojis = base_animated[True]

  base_available = collections.Counter([e.available for e in guild.emojis])
  usable_emojis = base_available[True]

  base_status = collections.Counter([x.status for x in guild.members])

  online_users = base_status[discord.Status.online]
  dnd_users = base_status[discord.Status.dnd]
  idle_users = base_status[discord.Status.idle]
  offline_users = base_status[discord.Status.offline]

  embed = discord.Embed(title="Guild Info:", color = random.randint(0, 16777215))
  embed.add_field(name="Server Name:", value=guild.name)
  embed.add_field(name="Server ID:", value=guild.id)
  embed.add_field(name="Server Region:", value=guild.region)
  embed.add_field(name = "Server Creation:", value = f"{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}")

  embed.add_field(name="Server Owner Info:", value = f"Owner : {guild.owner} \nOwner ID : {guild.owner_id}")

  embed.add_field(name = "Member info", value = f"Member Count : {guild.member_count}\nUsers : {users} \nBots : {bots} ")

  embed.add_field(name="Channel Count:", value = len(guild.channels))
  embed.add_field(name="Role Count:", value = len(guild.roles))

  embed.set_thumbnail(url = guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

  embed.add_field(name="Emojis Info:", value = f"Limit : {guild.emoji_limit}\nStatic : {static_emojis} \nAnimated : {animated_emojis} \nTotal : {len(guild.emojis)}/{guild.emoji_limit*2} \nUsable : {usable_emojis}")

  animated_value = guild.icon.is_animated() if guild.icon else False

  embed.add_field(name="Max File Size:",value=f"{guild.filesize_limit/1000000} MB")
  embed.add_field(name="Shard ID:",value=guild.shard_id)
  embed.add_field(name="Animated Icon", value = f"{animated_value}")
  
  embed.add_field(name="User Presences Info:", value = f"Online Users: {online_users} \nDND Users: {dnd_users} \nIdle Users : {idle_users} \nOffline Users : {offline_users}")

  await ctx.send(embed=embed)

async def roleinfo(ctx, role):
  role_members = collections.Counter([u.bot for u in role.members])
  role_bots = role_members[True]
  role_users = role_members[False]
  
  if role.tags: 
    role_bot_id = role.tags.bot_id

  if not role.tags:
    role_bot_id = None

  role_time = f"{discord.utils.format_dt(role.created_at, style = 'd')}{discord.utils.format_dt(role.created_at, style = 'T')}"

  embed = discord.Embed(title = f"{role} Info:" ,color = random.randint(0, 16777215) )
  embed.add_field(name = "Mention:", value = f"{role.mention}")
  embed.add_field(name = "ID:", value = f"{role.id}")
  embed.add_field(name = "Created at:", value = f"{role_time}")

  embed.add_field(name="Member Count:", value = f"Bot Count : {role_bots} \nUser Count : {role_users}" )

  embed.add_field(name = "Position Info:", value = f"Position : {role.position} \nHoisted : {role.hoist}")

  embed.add_field(name = "Managed Info:", value = f"Managed : {role.managed} \nBot : {role.is_bot_managed()} \nBot ID : {role_bot_id} \nDefault : {role.is_default()} \nBooster Role : {role.is_premium_subscriber()} \nIntegrated : {role.is_integration()} \nMentionable : {role.mentionable} ")

  embed.add_field(name = "Permissions:", value = f"{role.permissions.value}")
  embed.add_field(name = "Color:", value = f"{role.colour}")

  embed.set_thumbnail(url = "https://i.imgur.com/liABFL4.png")

  embed.set_footer(text = f"Guild: {role.guild}")

  await ctx.send(embed = embed)


async def triggered_converter(url, ctx):
  sr_client = sr_api.Client(session = ctx.bot.session)
  source_image=sr_client.filter(option="triggered", url = str(url))

  imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url= await imgur_client.upload_from_url(source_image.url)

  embed = discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Triggered gif requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
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

  imgur_client = aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"])
  imgur_url = await imgur_client.upload(image)
  embed=discord.Embed(color=random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

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
  embed=discord.Embed(color = random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
  embed.set_image(url=imgur_url["link"])
  embed.set_footer(text="powered by some random api")
  await ctx.send(embed=embed)

async def headpat_converter2(url, ctx):
  dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session = ctx.bot.session)
  image=await dagpi_client.image_process(asyncdagpi.ImageFeatures.petpet(),str(url))
  file = discord.File(fp=image.image,filename=f"headpat.{image.format}")
  embed=discord.Embed(color = random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
  embed.set_image(url=f"attachment://headpat.{image.format}")
  embed.set_footer(text="powered by dagpi")
  await ctx.send(file=file, embed=embed)

async def jail_converter(url, ctx):
  dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session = ctx.bot.session)
  image=await dagpi_client.image_process(asyncdagpi.ImageFeatures.jail(),str(url))
  file = discord.File(fp=image.image,filename=f"headpat.{image.format}")
  embed=discord.Embed(color = random.randint(0, 16777215))
  embed.set_author(name=f"Headpat gif requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
  embed.set_image(url=f"attachment://headpat.{image.format}")
  embed.set_footer(text="powered by dagpi")
  await ctx.send(file=file, embed = embed)