import collections, random, discord

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