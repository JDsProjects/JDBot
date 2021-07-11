import discord, re, collections, random, emoji, contextlib, typing
from discord.ext import commands
from discord.http import Route

class BetterMemberConverter(commands.Converter):
  async def convert(self, ctx, argument):
    try:
      user = await commands.MemberConverter().convert(ctx, argument)
    except commands.MemberNotFound:
      user = None

    if user == None:
      tag = re.match(r"#?(\d{4})",argument)
      if tag:
        if ctx.guild:
          test=discord.utils.get(ctx.guild.members, discriminator = tag.group(1))
          user = test or ctx.author

        if ctx.guild is None:
          user = await BetterUserconverter().convert(ctx,argument)
          user = user or ctx.author
               
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
      role = None

      with contextlib.suppress(commands.RoleNotFound, commands.NoPrivateMessage):
        role = await commands.RoleConverter().convert(ctx, argument)
      
      if role:
        if role.is_bot_managed():
          user=role.tags.bot_id
          user = ctx.bot.get_user(user) or await ctx.bot.fetch_user(user)

    if user == None:
      tag = re.match(r"#?(\d{4})",argument)
      if tag:
        test=discord.utils.get(ctx.bot.users, discriminator = tag.group(1))
        user = test or ctx.author
    return user

  
class EmojiBasic:
  def __init__(self, id: int, url: str):
    self.id = id
    self.url = url

  @classmethod
  async def convert(cls, ctx, argument):
    match=re.match(r'(?P<id>[0-9]{15,21})',argument)
    if match:
      emoji_id=(match.group(0))
      extentions = ["gif","png"]

      for x in extentions:
        response=await ctx.bot.session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}.{x}")
        if response.ok:
          return cls(emoji_id,response.real_url)

    else:
      return None

async def guildinfo(ctx, guild):
    base_user=collections.Counter([u.bot for u in guild.members])
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
    embed.add_field(name="Server Name:",value=guild.name)
    embed.add_field(name="Server ID:",value=guild.id)
    embed.add_field(name="Server Region:" ,value=guild.region)
    embed.add_field(name="Server Creation:",value=f"{guild.created_at} UTC")

    embed.add_field(name="Server Owner Info:", value = f"Owner : {guild.owner} \nOwner ID : {guild.owner_id}")

    embed.add_field(name = "Member info", value = f"Member Count : {guild.member_count}\nUsers : {users} \nBots : {bots} ")

    embed.add_field(name="Channel Count:",value = len(guild.channels))
    embed.add_field(name="Role Count:", value = len(guild.roles))
    embed.set_thumbnail(url = (guild.icon_url))

    embed.add_field(name="Emojis Info:", value = f"Limit : {guild.emoji_limit}\nStatic : {static_emojis} \nAnimated : {animated_emojis} \nTotal : {len(guild.emojis)}/{guild.emoji_limit*2} \nUsable : {usable_emojis}")

    embed.add_field(name="Max File Size:",value=f"{guild.filesize_limit/1000000} MB")
    embed.add_field(name="Shard ID:",value=guild.shard_id)
    embed.add_field(name="Animated Icon",value=guild.is_icon_animated())
    
    embed.add_field(name="User Presences Info:", value = f"Online Users: {online_users} \nDND Users: {dnd_users} \nIdle Users : {idle_users} \nOffline Users : {offline_users}")

    await ctx.send(embed=embed)



class EmojiConverter(commands.Converter):
  async def convert(self, ctx: commands.Context, arg: str): 
    emojis = emoji.unicode_codes.EMOJI_UNICODE["en"].values()
    try:
      return await commands.PartialEmojiConverter().convert(ctx,arg)
    except commands.PartialEmojiConversionFailure: pass
    if arg.rstrip("\N{variation selector-16}") in emojis or arg in emojis:
      return discord.PartialEmoji(name=arg)
    else:
      raise commands.BadArgument(f"{arg} is not an emoji")

def check(ctx):
  def inner(m):
    return m.author == ctx.author
  return inner

def Membercheck(ctx):
  def inner(m):
    return m.author == ctx.guild.me
  return inner

def reaction_check(ctx, reactions : list):
  def inner(reaction, user):
    return str(reaction.emoji) in reactions and user == ctx.author

async def roleinfo(ctx, role):
  role_members=collections.Counter([u.bot for u in role.members])
  role_bots = role_members[True]
  role_users = role_members[False]
  
  if role.tags: 
    role_bot_id = role.tags.bot_id

  if not role.tags:
    role_bot_id = None

  role_time = role.created_at.strftime('%m/%d/%Y %H:%M:%S')
  embed = discord.Embed(title = f"{role} Info:" ,color = random.randint(0, 16777215) )
  embed.add_field(name = "Mention:", value = f"{role.mention}")
  embed.add_field(name = "ID:", value = f"{role.id}")
  embed.add_field(name = "Created at:", value = f"{role_time}")

  embed.add_field(name="Member Count:", value = f"Bot Count : {role_bots} \nUser Count : {role_users}" )

  embed.add_field(name = "Position Info:", value = f"Position : {role.position} \nHoisted : {role.hoist}")

  embed.add_field(name = "Managed Info:", value = f"Managed : {role.managed} \nBot : {role.is_bot_managed()} \nBot ID : {role_bot_id} \nDefault : {role.is_default()} \nBooster Role : {role.is_premium_subscriber()} \nIntegrated : {role.is_integration()} \nMentionable : {role.mentionable} ")

  embed.add_field(name = "Permissions:", value = f"{role.permissions.value}")
  embed.add_field(name="Color:", value = f"{role.colour}")

  embed.set_thumbnail(url = "https://i.imgur.com/liABFL4.png")

  embed.set_footer(text = f"Guild: {role.guild}")

  await ctx.send(embed=embed)


class ColorConverter(commands.Converter):
  async def convert(self, ctx, argument):

    try:
      color = await commands.ColourConverter().convert(ctx, argument)

    except commands.BadColourArgument:
      color = None

    if not color and not argument.isdigit():
      
      argument = tuple(s for s in argument.split(" ") if s)
        
    if color and argument.isdigit():
      argument = int(argument)

    if isinstance(argument, int):
      if argument > 16777215: 
        await ctx.send(f"{argument} is too, so it's going to 16777215 which is can use.")
        argument = 16777215

      color = discord.Colour(argument)

    if isinstance(argument, tuple):

      argument = tuple(sorted(filter(lambda x: x.isdigit(), argument)))
    
      print(argument)
      
    return color