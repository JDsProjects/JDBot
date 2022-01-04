import discord, re, emoji, contextlib, typing, datetime
from discord.ext import commands
from discord.http import Route

class BetterMemberConverter(commands.Converter):
  async def convert(self, ctx, argument):
    try:
      user = await commands.MemberConverter().convert(ctx, argument)
    except commands.MemberNotFound:
      user = None

    if user is None:
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
     user = await commands.UserConverter().convert(ctx,argument)
    except commands.UserNotFound:
      user = None
    if not user and ctx.guild:
      try:
        user = await commands.MemberConverter().convert(ctx, argument)
      except commands.MemberNotFound:
        user = None

    if user is None:
      role = None

      with contextlib.suppress(commands.RoleNotFound, commands.NoPrivateMessage):
        role = await commands.RoleConverter().convert(ctx, argument)
      
      if role:
        if role.is_bot_managed():
          user=role.tags.bot_id
          user = await ctx.bot.try_user(user)

    if user is None:
      tag = re.match(r"#?(\d{4})", argument)
      if tag and not ctx.bot.users:
        test = discord.utils.get(ctx.bot.users, discriminator = tag.group(1))
        user = test or ctx.author
    return user

  
class EmojiBasic:
  def __init__(self, id: int, url: str):
    self.id = id
    self.url = url

  @classmethod
  async def convert(cls, ctx, argument):
    match = re.match(r'(?P<id>[0-9]{15,21})', argument)
    if match:
      emoji_id=(match.group(0))
      extentions = ["gif", "png"]

      for x in extentions:
        response=await ctx.bot.session.get(f"https://cdn.discordapp.com/emojis/{emoji_id}.{x}")
        if response.ok:
          return cls(emoji_id, response.real_url)

    else:
      return None

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


class ColorConverter(commands.Converter):
  async def convert(self, ctx, argument):

    try:
      color = await commands.ColourConverter().convert(ctx, argument)

    except commands.BadColourArgument:
      color = None

    if not color and not argument.isdigit():
      
      argument = list(s for s in argument.split(" ") if s)
        
    if color and argument.isdigit():
      argument = int(argument)

    if isinstance(argument, int):
      if argument > 16777215: 
        await ctx.send(f"{argument} is not valid color, 16777215 will be used instead.")
        argument = 16777215

      color = discord.Colour(argument)

    if isinstance(argument, list):

      argument = sorted(filter(lambda x: x.isdigit(), argument))

      argument = [int(n) for n in argument][:3]

      try:
        color = discord.Colour.from_rgb(*argument)
      
      except TypeError:
        color = None
    
    if color:
      if color.value > 16777215: 
        color = discord.Colour(16777215)
      
    return color

def generate_snowflake(dt: typing.Optional[datetime.datetime] = None) -> int:
    """Returns a numeric snowflake pretending to be created at the given date but more accurate and random than time_snowflake.
    If No dt is not passed, it makes one from the current time using utcnow.

    Parameters
    -----------
    dt: :class:`datetime.datetime`
        A datetime object to convert to a snowflake.
        If naive, the timezone is assumed to be local time.

    Returns
    --------
    :class:`int`
        The snowflake representing the time given.
    """

    dt = dt or discord.utils.utcnow()
    return int(dt.timestamp() * 1000 - 1420070400000) << 22 | 0x3fffff


class ObjectPlus(discord.Object):    
  
  @property
  def worker_id(self) -> int:
    """:class:`int`: Returns the worker id that made the snowflake."""
    return (self.id & 0x3E0000) >> 17

  @property
  def process_id(self) -> int:
        """:class:`int`: Returns the process id that made the snowflake."""
        return (self.id & 0x1F000) >> 12

  @property
  def increment_id(self) -> int:
    """:class:`int`: Returns the increment id that made the snowflake."""
    return (self.id & 0xFFF)


class ObjectPlusConverter(commands.converter.IDConverter[commands.Converter]):
  async def convert(self, ctx: commands.Context, argument: str) -> ObjectPlus:
        match = self._get_id_match(argument) or re.match(r'<(?:@(?:!|&)?|#)([0-9]{15,20})>$', argument)

        if match is None:
            raise discord.errors.ObjectNotFound(argument)

        result = int(match.group(1))

        return ObjectPlus(id=result)

#remove if edpy adds my pull request into the master.