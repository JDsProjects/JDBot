from discord.ext import commands
from utils import BetterMemberConverter, BetterUserconverter
import random
import discord
import aiohttp
import os

class Owner(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command(brief="a command to send mail")
  async def mail(self,ctx,*,user: BetterUserconverter=None):
    if user is None:
      await ctx.reply("User not found, returning Letter")
      user = ctx.author
    if user:
      def check(m):
        return m.author.id == ctx.author.id
      await ctx.reply("Please give me a message to use.")
      message = await self.client.wait_for("message",check=check)
      embed_message = discord.Embed(title=message.content, timestamp=(message.created_at), color=random.randint(0, 16777215))
      embed_message.set_author(name=f"Mail from: {ctx.author}",icon_url=(ctx.author.avatar_url))
      embed_message.set_footer(text = f"{ctx.author.id}")
      embed_message.set_thumbnail(url = "https://i.imgur.com/1XvDnqC.png")
      if (user.dm_channel is None):
        await user.create_dm()
      try:
        await user.send(embed=embed_message)
      except:
        user = ctx.author
        await user.send(content="Message failed. sending",embed=embed_message)
        embed_message.add_field(name="Sent To:",value=str(user))
      await self.client.get_channel(738912143679946783).send(embed=embed_message)

  @commands.command()
  async def load(self,ctx,*,cog=None):
    if cog:
      await ctx.send("WIP")
    if cog is None:
      await ctx.send("you can't ask to load no cogs.")
  
  @commands.command()
  async def reload(self,ctx,*,cog=None):
    if cog:
      pass
    if cog is None:
      await ctx.send("you can't ask to reload no cogs")
  
  @commands.command()
  async def unload(self,ctx,*,cog=None):
    if cog:
      pass
    
    if cog is None:
      await ctx.send("you can't ask to reload no cogs")

  async def cog_check(self, ctx):
    return await self.client.is_owner(ctx.author)

  @commands.command(brief="Changes Bot Status(Owner Only)")
  async def status(self , ctx , * , args=None):
    if await self.client.is_owner(ctx.author):
      if args:
        await self.client.change_presence(status=discord.Status.do_not_disturb, activity= discord.Activity(type=discord.ActivityType.watching,name=args))
      if args is None:
        await self.client.change_presence(status=discord.Status.do_not_disturb)
    if await self.client.is_owner(ctx.author) is False:
      await ctx.send("That's an owner only command")
  
  @commands.command(brief="Only owner command to change bot's nickname")
  async def change_nick(self, ctx ,*, name=None):
    if await self.client.is_owner(ctx.author):
      if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send("Changing Nickname")
        try:
          await ctx.guild.me.edit(nick=name)
        except discord.Forbidden:
          await ctx.send("Appears not to have valid perms")
      if isinstance(ctx.channel,discord.DMChannel):
        await ctx.send("You can't use that in Dms.")
      
    if await self.client.is_owner(ctx.author) is False:
      await ctx.send("You can't use that command")

  
  @commands.command(brief="a command to give a list of servers(owner only)",help="Gives a list of guilds(Bot Owners only)")
  async def servers(self,ctx):
    if await self.client.is_owner(ctx.author):
      send_list = [""]
      guild_list = ["%d %s %d %s" % (len(g.members), g.name, g.id, (g.system_channel or g.text_channels[0]).mention) for g in self.client.guilds]
      for i in guild_list:
        if len(send_list[-1] + i) < 1000:
          send_list[-1] += i + "\n"
        else:
          send_list += [i + "\n"]
      if (ctx.author.dm_channel is None):
        await ctx.author.create_dm()
      await ctx.author.dm_channel.send("\n Servers:")
      for i in send_list:
        await ctx.author.dm_channel.send(i) 
    if await self.client.is_owner(ctx.author) is False:
      await ctx.send("You can't use that it's owner only")

  @commands.command(brief="only works with JDJG, but this command is meant to send updates to my webhook")
  async def webhook_update(self,ctx,*,args=None):
    if await self.client.is_owner(ctx.author):
      if args:
        if isinstance(ctx.channel, discord.TextChannel):
          await ctx.message.delete()

        async with aiohttp.ClientSession() as session:
          webhook=discord.Webhook.from_url(os.environ["webhook1"], adapter=discord.AsyncWebhookAdapter(session))
          embed=discord.Embed(title="Update",color=(35056),timestamp=(ctx.message.created_at))
          embed.add_field(name="Update Info:",value=args)
          embed.set_author(name="JDJG's Update",icon_url='https://i.imgur.com/pdQkCBv.png')
          embed.set_footer(text="JDJG's Updates")
          await webhook.execute(embed=embed)
        
        async with aiohttp.ClientSession() as session:
          webhook=discord.Webhook.from_url(os.environ["webhook99"], adapter=discord.AsyncWebhookAdapter(session))
          embed=discord.Embed(title="Update",color=(35056),timestamp=(ctx.message.created_at))
          embed.add_field(name="Update Info:",value=args)
          embed.set_author(name="JDJG's Update",icon_url='https://i.imgur.com/pdQkCBv.png')
          embed.set_footer(text="JDJG's Updates")
          await webhook.execute(embed=embed)
      if args is None:
        await ctx.send("You sadly can't use it like that.")
    if await self.client.is_owner(ctx.author) is False:
      await ctx.send("You can't use that")

  @commands.command(brief="Commands to see what guilds a person is in.")
  async def mutualguilds(self,ctx,*,user:BetterUserconverter=None):
    if user is None:
      user = ctx.author.id
    user_guildlist=[guild for guild in self.client.guilds if guild.get_member(user)]
    send_list = [""]
    for i in user_guildlist:
      if len(send_list[-1] + i) < 1000:
        send_list[-1] += i + "\n"
      else:
        send_list += [i + "\n"]
    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()
      await ctx.author.dm_channel.send("\n Servers:")
      for i in send_list:
        await ctx.author.dm_channel.send(i) 
      if len(send_list) < 1:
       await ctx.author.dm_channel("No shared servers")

def setup(client):
  client.add_cog(Owner(client))
