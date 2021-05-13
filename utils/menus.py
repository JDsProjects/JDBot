import discord, re, collections, random
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
      embed=discord.Embed(title="Failed grabbing the invite code:",description=f"it returned as {item}. Discord couldn't fetch the invite.",color=random.randint(0, 16777215))
      embed.set_footer(text="If this is a consistent problem please contact JDJG Inc. Official#3493")

    return embed

