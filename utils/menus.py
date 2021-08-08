import discord, re, collections, random, contextlib, asyncio, emoji, aiohttp
from discord.ext import commands, menus


class InviteInfoEmbed(menus.ListPageSource):
  async def format_page(self, menu, item):
    if isinstance(item,discord.Invite):
      if item.guild:
        image = item.guild.icon_url
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


class JDJGsummon(menus.Menu):
  async def send_initial_message(self, ctx, channel):
    return await channel.send("react with \N{WHITE HEAVY CHECK MARK} if you want me to be summoned if not use \N{CROSS MARK}")

  @menus.button('\N{WHITE HEAVY CHECK MARK}')
  async def on_checkmark(self, payload):
    msg = await self.ctx.send(content=f'Summon JDJG now a.k.a the owner to the guild make sure invite permissions are open!')
    await self.message.delete()

    if isinstance(self.ctx.channel, discord.TextChannel):
      await asyncio.sleep(1)
      await msg.edit(content = "This is attempting to make an invite")

      invite = None
      with contextlib.suppress(discord.NotFound, discord.HTTPException):
        invite = await self.ctx.channel.create_invite(max_uses = 0)

      if invite:
        await asyncio.sleep(1)
        await msg.edit(content = "Contacting JDJG...")

        jdjg = await self.bot.getch_user(168422909482762240)

        embed = discord.Embed(title = f"{self.ctx.author} wants your help", description = f"Invite: {invite.url} \nChannel : {self.ctx.channel.mention} \nName : {self.ctx.channel}", color = random.randint(0, 16777215) )
        embed.set_footer(text = f"Guild: {self.ctx.guild} \nGuild ID: {self.ctx.guild.id}")
        
        await jdjg.send(embed=embed)

      else:
        await asyncio.sleep(1)
        return await msg.edit(content = "Failed making an invite. You likely didn't give it proper permissions(a.k.a create invite permissions) or it errored for not being found.")

    if isinstance(self.ctx.channel,discord.DMChannel):
      await asyncio.sleep(1)
      return await msg.edit(content = "This is meant for guilds not Dm channel if you want support in DM channel contact the owner, By DMS at JDJG Inc. Official#3493.")

  @menus.button('\N{CROSS MARK}')
  async def on_crossmark(self, payload):
    await self.ctx.send(content=f"You didn't agree to summoning me. So I will not be invited.")
    await self.message.delete()


class SupportInvite(menus.Menu):
  async def send_initial_message(self, ctx, channel):
    return await channel.send("You must agree with **\N{WHITE HEAVY CHECK MARK}** to have an invite link to our support server sent here before we can invite you")  

  @menus.button('\N{WHITE HEAVY CHECK MARK}')
  async def on_checkmark(self, payload):
    await self.ctx.send(content=f"https://discord.gg/sHUQCch")

  @menus.button('\N{CROSS MARK}')
  async def on_crossmark(self, payload):
    await self.ctx.send(content=f"looks like you didn't agree to be invited. So We will not invite you!")

class QuickMenu(menus.ListPageSource):
  async def format_page(self, menu, item):
    return item
    #returns the embed here lol.