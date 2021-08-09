from discord.ext import commands
import discord, random, typing
import utils
from discord.ext.commands.cooldowns import BucketType

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.cooldown(1,90,BucketType.user)
  @commands.command(brief="a command to warn people, but if you aren't admin it doesn't penalize.")
  async def warn(self, ctx, Member: utils.BetterMemberConverter = None):
    Member = Member or ctx.author
    if utils.warn_permission(ctx, Member):

      if Member:
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

    if utils.warn_permission(ctx, Member) is False:
      await ctx.send("You don't have permission to use that. You need to have manage_messages, have a higher hieracy in a guild, and have higher permissions than the target to use that.")

  @warn.error
  async def warn_errror(self, ctx, error):
    await ctx.send(error)

    import traceback
    traceback.print_exc()

  @commands.cooldown(1,90,BucketType.user)
  @commands.command(help="a command to scan for malicious bots, specificially ones that only give you random invites and are fake(WIP)")
  async def scan_guild(self, ctx):
    if isinstance(ctx.channel, discord.TextChannel):
      cur = await self.bot.sus_users.cursor()
      cursor = await cur.execute("SELECT * FROM SUS_USERS;")
      sus_users = dict(await cursor.fetchall())
      await cur.close()
      count = 0
      for x in sus_users:
        user=ctx.guild.get_member(x)
        if user:
          count += 1
          await ctx.send(f"Found {x}. \nUsername:{user.name} \nReason: {sus_users[x]}")
      if count < 1:
        await ctx.send("No Bad users found.")
    if isinstance(ctx.channel,discord.DMChannel):
      await ctx.send("please use the global version")

  @commands.cooldown(1,90,BucketType.user)
  @commands.command(brief= "scan globally per guild")
  async def scan_global(self, ctx):
    cur = await self.bot.sus_users.cursor()
    cursor = await cur.execute("SELECT * FROM SUS_USERS;")
    sus_users = dict(await cursor.fetchall())
    await cur.close()

    
    ss_users = [u for u in sus_users if await self.bot.getch_user(u)]

    if not(ss_users):
      await ctx.send("no sus users found")

    else:
      await ctx.send("There are in fact sus_users in the program but it's currently handling how to send to you.")


  async def cog_command_error(self, ctx, error):
    if not ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
    #I need to fix all cog_command_error


  @commands.command(brief = "gives stats about the sus users", aliases = ["sususers_stats"])
  async def sus_users_stats(self, ctx):
    cur = await self.bot.sus_users.cursor()
    cursor = await cur.execute("SELECT * FROM SUS_USERS;")
    sus_users = dict(await cursor.fetchall())
    await cur.close()

    await ctx.send(content = f"Total sus user count: {len(sus_users)}")


  @commands.command(brief = "gives you info if someone is a sus user or etc")
  async def is_sus(self, ctx, *, user : typing.Optional[discord.User] = None):
    user = user or ctx.author

    cur = await self.bot.sus_users.cursor()
    cursor = await cur.execute("SELECT * FROM SUS_USERS;")
    sus_users = dict(await cursor.fetchall())
    await cur.close()

    truth=sus_users.get(user.id)

    if not truth:
      await ctx.send(f"{user} is not in the sus list.")

    else:
      await ctx.send(f"{user} for {truth}")


  @commands.command(help="a way to report a user, who might appear in the sus list. also please provide ids and reasons. (WIP)")
  async def report(self, ctx, *, args = None):
    if args:
      jdjg = await self.bot.getch_user(168422909482762240) 
      if (jdjg.dm_channel is None):
        await jdjg.create_dm()
      embed = discord.Embed(color=random.randint(0, 16777215))
      embed.set_author(name=f"Report by {ctx.author}",icon_url=(ctx.author.avatar.url))
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
      await ctx.channel.purge(limit = amount)
    except Exception as e:
      await ctx.send(f"An Error occured with {e}")
  

def setup(bot):
  bot.add_cog(Moderation(bot))