from discord.ext import commands
import discord, random, typing
import utils
from discord.ext.commands.cooldowns import BucketType
from discord.ext.menus.views import ViewMenuPages

class Moderation(commands.Cog):
  "Commands For Moderators to use"
  def __init__(self, bot):
    self.bot = bot

  @commands.cooldown(1, 90, BucketType.user)
  @commands.command(brief="a command to warn people, but if you aren't admin it doesn't penalize.")
  async def warn(self, ctx, Member: utils.BetterMemberConverter = None):
    Member = Member or ctx.author
    
    warn_useable = utils.warn_permission(ctx, Member)

    if warn_useable:

      embed = discord.Embed(color=random.randint(0, 16777215))
      embed.set_author(name=f"You have been warned by {ctx.author}",icon_url=("https://i.imgur.com/vkleJ9a.png"))
      embed.set_image(url="https://i.imgur.com/jDLcaYc.gif")
      embed.set_footer(text = f"ID: {ctx.author.id}")

      if Member.dm_channel is None:
        await Member.create_dm()
      
      try:
        await Member.send(embed=embed)

      except discord.Forbidden:
        await ctx.send("they don't seem like a valid user or they weren't DMable.")
      
      embed.set_footer(text = f"ID: {ctx.author.id}\nWarned by {ctx.author}\nWarned ID: {Member.id} \nWarned: {Member}")
      await self.bot.get_channel(855217084710912050).send(embed=embed) 

      if (ctx.author.dm_channel is None):
        await ctx.author.create_dm()

      try:
        await ctx.author.send(content=f"Why did you warn {Member}?")

      except discord.Forbidden:
        await ctx.send("we can't DM them :(")

    elif warn_useable is False:
      await ctx.send(f"{ctx.author.mention}, you don't have permission to use that. You need to have manage_messages, have a higher hieracy in a guild, and have higher permissions than the target to use that.", allowed_mentions = discord.AllowedMentions.none())

  @warn.error
  async def warn_errror(self, ctx, error):
    await ctx.send(error)

    import traceback
    traceback.print_exc()

  @commands.cooldown(1, 90, BucketType.user)
  @commands.command(help = "a command to scan for malicious bots, specificially ones that only give you random invites and are fake")
  async def scan_guild(self, ctx):
    if isinstance(ctx.channel, discord.TextChannel):

      sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))
      count = 0

      #some code here to do a list compreshion to see if they are cached using get_user, those who return as None will be passed to query_members

      ids = [u for u in list(sus_users.keys()) if not ctx.guild.get_member(u)]

      await ctx.guild.query_members(limit = 100, cache = True, user_ids = ids)

      for x in sus_users:
        user = ctx.guild.get_member(x)
        if user:
          count += 1
          await ctx.send(f"Found {x}. \nUsername: {user.name} \nReason: {sus_users[x]}")
          
      if count < 1:
        await ctx.send("No Bad users found.")

    if isinstance(ctx.channel, discord.DMChannel):
      await ctx.send("please use the global version")

  @commands.cooldown(1, 90, BucketType.user)
  @commands.command(brief = "scan globally per guild")
  async def scan_global(self, ctx):
    
    sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))
    
    ss_users = [await self.bot.try_user(u) for u in sus_users if not None]

    if not(ss_users):
      await ctx.send("no sus users found")

    else:
      mutual_guild_users = [u for u in ss_users if u.mutual_guilds]

      valid_users = [u for u in mutual_guild_users if utils.mutual_guild_check(ctx, u)]

      menu = ViewMenuPages(utils.ScanGlobalEmbed(valid_users, per_page = 1), delete_message_after = True)
      
      await menu.start(ctx)

  async def cog_command_error(self, ctx, error):
    if not ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
    #I need to fix all cog_command_error


  @commands.command(brief = "gives stats about the sus users", aliases = ["sususers_stats"])
  async def sus_users_stats(self, ctx):
    
    sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))
    await ctx.send(content = f"Total sus user count: {len(sus_users)}")


  @commands.command(brief = "gives you info if someone is a sus user or etc")
  async def is_sus(self, ctx, *, user : typing.Optional[discord.User] = None):
    user = user or ctx.author

    result = await self.bot.db.fetchrow("SELECT * FROM SUS_USERS WHERE user_id = ($1);", user.id)

    if not result:
      await ctx.send(f"{user} is not in the sus list.")

    else:
      reason = tuple(result)[1]
      await ctx.send(f"{user} for {reason}")

  @commands.command(help ="a way to report a user, who might appear in the sus list. also please provide ids and reasons. (WIP)")
  async def report(self, ctx, *, args = None):
    if args:
      jdjg = await self.bot.try_user(168422909482762240) 
      if (jdjg.dm_channel is None):
        await jdjg.create_dm()
        
      embed = discord.Embed(color=random.randint(0, 16777215))
      embed.set_author(name=f"Report by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
      embed.add_field(name="Details:",value=args)
      embed.set_footer(text=f"Reporter's ID is {ctx.author.id}")
      await jdjg.send(embed=embed)
      await ctx.send(content="report sent to JDJG",embed=embed)
    
    if args is None:
      await ctx.send("You didn't give enough information to use.")

  @commands.command(brief = "cleat amount/purge messages above to 100 msgs each", aliases = ["purge"])
  async def clear(self, ctx, *, amount: typing.Optional[int] = None):
    
    if not amount:
      return await ctx.send("you didn't give an amount to use to clear.") 

    if not utils.clear_permission(ctx):
      return await ctx.send("you can't use that(you don't have manage messages).")

    
    if not ctx.guild.me.guild_permissions.manage_messages:
      return await ctx.send("Bot can't use that it doesn't have manage messages :(")

    amount += 1

    if amount > 100:
      await ctx.send('too high setting to 100')
      amount = 101

    try:
      messages = await ctx.channel.purge(limit = amount)
      await ctx.send(f"I deleted {len(messages)} messages, plus the {amount} messages you wanted me to delete.")
    except Exception as e:
      await ctx.send(f"An Error occured with {e}")

  @commands.command(brief = "Unarchives thread channel")
  async def unarchive_thread(self, ctx, channel : typing.Optional[discord.Thread] = None):

    channel = channel or ctx.channel
  
    if isinstance(channel, discord.Thread):
      if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
        await ctx.send("Now unarchiving thread")

        thread = await channel.edit(archived = False)
        await ctx.send(f"Succesfully made {thread} unarchived again")

      if not ctx.me.guild_permissions.manage_threads:
        await ctx.send("can't unarchive channel because the bot doesn't have permissions to do so.")

      if not ctx.author.guild_permissions.manage_threads:
        await ctx.send("you don't have permission to edit to the thread channel.")

    else:
      await ctx.send("You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread.")

  @commands.command(brief = "Unarchives thread channel")
  async def archive_thread(self, ctx, channel : typing.Optional[discord.Thread] = None):

    channel = channel or ctx.channel
  
    if isinstance(channel, discord.Thread):
      if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
        await ctx.send("Now archiving thread")

        thread = await channel.edit(archived = True)
        await ctx.send(f"Succesfully made {thread} archived again")

      if not ctx.me.guild_permissions.manage_threads:
        await ctx.send("can't archive channel because the  bot doesn't have permissions to do so.")

      if not ctx.author.guild_permissions.manage_threads:
        await ctx.send("you don't have permission to edit to the thread channel.")

    else:
      await ctx.send("You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread.")

  @commands.command(brief = "locks the thread channel")
  async def lock_thread(self, ctx, channel : typing.Optional[discord.Thread] = None):

    channel = channel or ctx.channel
  
    if isinstance(channel, discord.Thread):
      if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
        await ctx.send("Now locking thread")

        thread = await channel.edit(locked = True)
        await ctx.send(f"Succesfully made {thread} locked.")

      if not ctx.me.guild_permissions.manage_threads:
        await ctx.send("can't lock channel because the bot doesn't have permissions to do so.")

      if not ctx.author.guild_permissions.manage_threads:
        await ctx.send("you don't have permission to edit to the thread channel.")

    else:
      await ctx.send("You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread.")

  @commands.command(brief = "unlocks the thread channel")
  async def unlock_thread(self, ctx, channel : typing.Optional[discord.Thread] = None):

    channel = channel or ctx.channel
  
    if isinstance(channel, discord.Thread):
      if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
        await ctx.send("Now unlocking thread")

        thread = await channel.edit(locked = False)
        await ctx.send(f"Succesfully made {thread} unlocked.")

      if not ctx.me.guild_permissions.manage_threads:
        await ctx.send("can't unlock channel because the bot doesn't have permissions to do so.")

      if not ctx.author.guild_permissions.manage_threads:
        await ctx.send("you don't have permission to edit to the thread channel.")

    else:
      await ctx.send("You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread.")
  

def setup(bot):
  bot.add_cog(Moderation(bot))