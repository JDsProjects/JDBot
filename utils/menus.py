import discord, re, collections, random, emoji, aiohttp
from discord.ext import commands, menus


class InviteInfoEmbed(menus.ListPageSource):
  async def format_page(self, menu, item):
    if isinstance(item,discord.Invite):
      if item.guild:
        image = item.guild.icon.url if item.guild.icon else "https://i.imgur.com/3ZUrjUP.png"
        guild = item.guild
        guild_id = item.guild.id
      if item.guild is None:
        guild = "Group Chat"
        image = "https://i.imgur.com/pQS3jkI.png"
        guild_id = "Unknown"
      embed=discord.Embed(title=f"Invite for {guild}:",color=random.randint(0, 16777215))
      embed.set_author(name="Discord Invite Details:",icon_url=(image))
      embed.add_field(name="Inviter:",value=f"{item.inviter}")
      embed.add_field(name="User Count:",value=f"{item.approximate_member_count}")
      embed.add_field(name="Active User Count:",value=f"{item.approximate_presence_count}")
      embed.add_field(name="Invite Channel",value=f"{item.channel}")
      embed.set_footer(text=f"ID: {guild_id}\nInvite Code: {item.code}\nInvite Url: {item.url}")
  
    if isinstance(item,str):
      embed=discord.Embed(title="Failed grabbing the invite code:",description=f"Discord couldnt fetch the invite with the code {item}.",color=random.randint(0, 16777215))
      embed.set_footer(text="If this is a consistent problem please contact JDJG Inc. Official#3493")

    return embed

async def valid_src(url: str, session: aiohttp.ClientSession):
  async with session.head(url) as resp:
    status = resp.status
  return status == 200

async def emoji_to_url(char, include_check: bool = True, session: aiohttp.ClientSession = None):
  try:
    url = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(char[0]):x}.png"
    if not include_check:
      return url
        
    _session = session or aiohttp.ClientSession()
    is_valid = await valid_src(url, _session)
    if not session:
      await _session.close()
    return (url if is_valid else char)
  except TypeError:
    return char

class EmojiInfoEmbed(menus.ListPageSource):
  async def format_page(self, menu, item):
    if isinstance(item, discord.PartialEmoji):
      if item.is_unicode_emoji():
        digit = f"{ord(str(item)):x}"
        unicode = f"\\U{digit:>08}"
        emoji_name = item.name.replace(':','')
        emoji_url = await emoji_to_url(f"{item}", session = menu.ctx.bot.session)
        embed=discord.Embed(title="Default Emote:",url=f"http://www.fileformat.info/info/unicode/char/{digit}",color=random.randint(0, 16777215))
        embed.add_field(name="Name:",value=f"{emoji_name}")
        embed.add_field(name="Unicode:",value=unicode)
        embed.add_field(name="unicode url",value=f"[site](http://www.fileformat.info/info/unicode/char/{digit})")
        embed.add_field(name="Credit:",value=f"[[Site 1]](https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L250-L264)")
        embed.set_image(url=emoji_url)
        embed.set_footer(text=f"click the title for more unicode data")
        return embed

      else:
        embed = discord.Embed(title=f"Custom Emoji: **{item.name}**",color=random.randint(0, 16777215))
        embed.set_image(url=item.url)
        embed.set_footer(text=f"Emoji ID:{item.id}")
        return embed

    else:
      embed=discord.Embed(title="Failed grabbing emoji:",description=f"Discord couldn't fetch the emoji with regex: {item}",color=random.randint(0, 16777215))
      return embed

class ErrorEmbed(menus.ListPageSource):
  async def format_page(self, menu, item):

    item = discord.utils.escape_markdown(item, as_needed=False, ignore_links=True)
    
    return discord.Embed(title="Error", description=item, color=random.randint(0, 16777215))

class charinfoMenu(menus.ListPageSource):
  async def format_page(self, menu, item):
    return discord.Embed(description = item, color = random.randint(0, 16777215))

class QuickMenu(menus.ListPageSource):
  async def format_page(self, menu, item):
    return item
    #returns the embed here lol.