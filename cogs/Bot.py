from discord.ext import commands, tasks, menus
import discord, random, time, asyncio, difflib, contextlib

import utils
from discord.ext.commands.cooldowns import BucketType
from discord.ext.menus.views import ViewMenuPages

class Bot(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.status_task.start()

  @tasks.loop(seconds = 40)
  async def status_task(self):
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"the return of {self.bot.user.name}"))
    await asyncio.sleep(40)
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} servers | {len(self.bot.users)} users"))
    await asyncio.sleep(40)
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the new updates coming soon..."))
    await asyncio.sleep(40)

  @status_task.before_loop
  async def before_status_task(self):
    await self.bot.wait_until_ready()

  def cog_unload(self):
    self.status_task.stop()

  @commands.command(brief="sends pong and the time it took to do so.")
  async def ping(self,ctx):
    start = time.perf_counter()
    message=await ctx.send("Pong")
    end = time.perf_counter()
    await message.edit(content=f"Pong\nBot Latency: {((end - start)*1000)} MS\nWebsocket Response time: {self.bot.latency*1000} MS")
  
  @commands.command(brief="gives you an invite to invite the bot.", aliases = ["inv"])
  async def invite(self, ctx):
    normal_inv = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 8))
    minimial_invite = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 70635073))

    embed = discord.Embed(title="Invite link:", color = random.randint(0, 16777215))
    embed.add_field(name=f"{self.bot.user.name} invite:", value=f"[{self.bot.user.name} invite url]({normal_inv}) \nNon Markdowned invite : {normal_inv}")
    embed.add_field(name = "Minimial permisions", value = f"{ minimial_invite}")
    embed.set_thumbnail(url = self.bot.user.avatar.url)
    embed.set_footer(text = f"not all features may work if you invite with minimal perms, if you invite with 0 make sure these permissions are in a Bots/Bot role.")
    await ctx.send(embed = embed)

  @commands.command(brief="gives you who the owner is.")
  async def owner(self, ctx):

    info = await self.bot.application_info()
    owner_id = info.team.owner_id if info.team else info.owner.id

    support_guild =  self.bot.get_guild(736422329399246990)

    if not support_guild.get_member(owner_id):
      await ctx.send("attempting to cache with query_members in discord.py the owner id in the support guild, if they don't exist this will not work")

      try:
        await support_guild.query_members(cache = True, limit = 5, user_ids = [owner_id]) 

      except:
        await ctx.send("failed caching members with query_members in discord.py")

    owner = await self.bot.getch_member(support_guild, owner_id) or await self.bot.getch_user(owner_id)

    user_type = ("Bot" if owner.bot else "User")

    guilds_list=[guild for guild in self.bot.guilds if guild.get_member(owner.id) and guild.get_member(ctx.author.id)]

    if not guilds_list:
      guild_list = "None"


    if guilds_list:
      guild_list= ", ".join(map(str, guilds_list))
    
    if owner:
      nickname = str(owner.nick)
      joined_guild = f"{discord.utils.format_dt(owner.joined_at, style = 'd')}\n{discord.utils.format_dt(owner.joined_at, style = 'T')}"
      status = str(owner.status).upper()
      highest_role = owner.roles[-1]
    
    if owner is None:
      nickname = "None"
      joined_guild = "N/A"
      status = "Unknown"

      for guild in owner.mutual_guilds:
        member=guild.get_member(owner.id)
        if member:
          status=str(member.status).upper()
          break
      highest_role = "None Found"
    
    embed=discord.Embed(title=f"Bot Owner: {owner}",description=f"Type: {user_type}", color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
    embed.add_field(name="Username:", value = owner.name)
    embed.add_field(name = "Discriminator:",value=owner.discriminator)
    embed.add_field(name = "Nickname: ", value = nickname)
    embed.add_field(name = "Joined Discord: ", value = (f"{discord.utils.format_dt(owner.created_at, style = 'd')}\n{discord.utils.format_dt(owner.created_at, style = 'T')}"))
    embed.add_field(name = "Joined Guild: ", value = joined_guild)
    embed.add_field(name = "Mutual Guilds:", value=guild_list)
    embed.add_field(name = "ID:", value = owner.id)
    embed.add_field(name = "Status:", value=status)
    embed.add_field(name = "Highest Role:", value=highest_role)
    embed.set_image(url = owner.avatar.url)
    embed.set_footer(text = f"Support Guild : {support_guild}")
    await ctx.send(embed = embed)

  @commands.command(help="a command to give information about the team",brief="this command works if you are in team otherwise it will just give the owner.")
  async def team(self,ctx):
    information=await self.bot.application_info()
    if information.team == None:
      true_owner=information.owner
      team_members = []
      
    if information.team != None:
      true_owner = information.team.owner
      team_members = information.team.members
    embed=discord.Embed(title=information.name,color=random.randint(0, 16777215))
    embed.add_field(name="Owner",value=true_owner)
    embed.set_footer(text=f"ID: {true_owner.id}")

    embed.set_image(url = information.icon.url if information.icon else self.bot.avatar.url)
    #I don't gunatree this works, but I hope it does.

    for x in team_members:
      embed.add_field(name=x,value=x.id)
    await ctx.send(embed=embed)

  @commands.command(help="get the stats of users and members in the bot",brief="this is an alternative that just looking at the custom status time to time.")
  async def stats(self,ctx):
    embed = discord.Embed(title="Bot stats",color=random.randint(0, 16777215))
    embed.add_field(name="Guild count",value=len(self.bot.guilds))
    embed.add_field(name="User Count:",value=len(self.bot.users))
    embed.add_field(name="True Command Count:",value=f"{len(list(self.bot.walk_commands()))}")
    embed.add_field(name="Command Count:",value=f"{len(self.bot.commands)}")
    embed.add_field(name = "Approximate Member Count:", value = f"{sum(g.member_count for g in self.bot.guilds)}")
    await ctx.send(embed=embed)

  @commands.command(brief="a way to view open source",help="you can see the open source with the link it provides")
  async def open_source(self, ctx):
    embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot. Please don't just copy the source code, cause this may cause issues with you or the user instead ask if you want to use my code or learn from my code and look to see if that's a valid command a.ka ask me first, then discord.py about the bot! Thanks :D",color=random.randint(0, 16777215))
    embed.set_author(name=f"{self.bot.user}'s source code:", icon_url = self.bot.user.avatar.url)
    await ctx.send(embed=embed)

  @commands.group(name="open", invoke_without_command=True)
  async def open(self, ctx):
    embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot. Please don't just copy the source code, cause this may cause issues with you or the user instead ask if you want to use my code or learn from my code and look to see if that's a valid command a.ka ask me first, then discord.py about the bot! Thanks :D",color=random.randint(0, 16777215))
    embed.set_author(name=f"{self.bot.user}'s source code:", icon_url = self.bot.user.avatar.url)
    await ctx.send(embed = embed)
  
  @open.command(brief="a way to view open source",help="you can see the open source with the link it provides")
  async def source(self, ctx):
    await self.open(ctx)
  
  @commands.command(brief="a set of rules we will follow")
  async def promise(self,ctx):
    embed=discord.Embed(title="Promises we will follow:",color=random.randint(0, 16777215))
    embed.add_field(name="Rule 1:",value="if you are worried about what the bot may collect, please send a DM to the bot, and we will try to compile the data the bot may have on you.")
    embed.add_field(name="Rule 2:",value="in order to make sure our bot is safe, we will be making sure the token is secure and making sure anyone who works on the project is very trustworthy.")
    embed.add_field(name="Rule 3:",value="we will not nuke your servers, as this happened to us before and we absolutely hated it.")
    embed.add_field(name="Rule 4:",value="We will also give you a list of suspicious people")
    embed.add_field(name="Rule 5:",value="we also made sure our code is open source so you can see what it does.")
    embed.add_field(name="Rule 6:",value="We will also let you ask us questions directly, just DM me directly(the owner is listed in the owner command(and anyone should be able to friend me)")
    embed.add_field(name="Rule 7:",value="Using our bot to attempt to break TOS, will cause us to ban you from using the bot, then upgrade our security")
    embed.add_field(name="Rule 8:",value="Attempting to break discord TOS like having a giveaway but having people require to join an external guild(will eventually be reportable to us, if they owner counties, then the reporter should report to discord.(essentially breaking TOS near the functionalties with our bot)")
    embed.add_field(name="Rule 9:",value="If our bot doesn't do the giveaway requirements we're actually safe, as we don't require it, however please report this to us, so we can contact them to get them to stop, Thanks. if they don't listen we'll tell you, then you can report them.")
    await ctx.send(embed=embed)

  @commands.command(brief="Privacy Policy",aliases=["privacy"])
  async def promises(self, ctx):
    embed = discord.Embed(title="Privacy Policies",color=random.randint(0, 16777215))
    embed.add_field(name="1:",value="We have a channel that logs when the bot joins or leaves a guild")
    embed.add_field(name="2:",value="We will store any errors(which may go back to you, but this is console only.) This is in memory anyway, thus it doesn't store in any of our DBs.")
    embed.add_field(name="3:",value="we will only store user ids(in the future for balance commands and economy commands(opt in only)")
    embed.add_field(name="4:",value="We will store user id, and channel id(our channel), and last active, for ticket support if you need support. (is opt in)")
    embed.add_field(name="5:",value="we Finally store invalid commands")
    embed.add_field(name="6:",value="We may temporarily look at your mutual guilds with our bot or the list of servers our bot is in, with some information, just to test some things(like if a command is going hayware) or prevent abuse. If you want to look at the embeds with this, just ask, We will show you.")
    embed.add_field(name="6.1:",value="This is a temp command, which is stored no where else, and we also delete the embed when done :D. If you have a problem with this contact me.")
    embed.add_field(name="Final:",value="There should be no more except the sus list(list of ids I put together by hand of people who probaly shouldn't hang out with). We also now use the built in discord.py guild.members list with cache_member to only use memory to store you, we only use this to limit api calls(it's only opt in anyway)")
    embed.add_field(name="Who Gets this info:",value="Only us, and our DB provider MongoDB(but they are unlikely to use our data. Sus users do show up if they exist in the same guild though and the reason why.")
    embed.add_field(name="More Info:",value="Contact me at JDJG Inc. Official#3493")
    await ctx.send(embed=embed)

  @commands.command(brief="Sends you an invite to the official Bot support guild",aliases=["guild_invite"])
  async def support_invite(self, ctx):
    
    view = utils.BasicButtons(ctx.author)
    msg = await ctx.send("You must agree with **\N{WHITE HEAVY CHECK MARK}** to have an invite link to our support server sent here before we can invite you", view = view)  

    await view.wait()

    if view.value is None:
      await ctx.reply("You let me time out :(")
      return await msg.delete()

    if view.value:
      await ctx.send(content = f"The Invite to the support guild is https://discord.gg/sHUQCch?")
      return await msg.delete()

    if not view.value:
      await ctx.send(content=f" looks like you didn't agree to be invited. So We will not invite you! ")
      return await msg.delete()


  @commands.command(brief="This command gives you an alt bot to use",aliases=["alt_invite"])
  async def verify_issue(self, ctx):
    await ctx.send("You can invite the bot 831162894447804426(this will be an alt bot with almost the same code though some report functionalies will have their guild swapped :D")

  @commands.command()
  async def whyprefixtest(self,ctx):
    await ctx.send("Because I don't have any alternative suggestions, and I don't feel like changing it to jd! or something. I can confirm this isn't a test bot :D")

  @commands.command()
  async def closest_command(self, ctx, *, command = None):
    if command is None:
      await ctx.send("Please provide an arg.")

    if command:

      all_commands = list(self.bot.walk_commands())
    
      command_names = [f"{x}" for x in await self.bot.filter_commands(ctx, all_commands)]

      #only reason why it's like this is uh, it's a bit in variable.

      matches = difflib.get_close_matches(command, command_names)
    
      if matches:
        await ctx.send(f"Did you mean... `{matches[0]}`?")

      else:
        await ctx.send("got nothing sorry.")

 
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "a command to automatically summon by creating an invite and having jdjg look at something if it's there something wrong")
  async def jdjgsummon(self, ctx):

    view = utils.BasicButtons(ctx.author)
    msg = await ctx.send("React with \N{WHITE HEAVY CHECK MARK} if you want me to be summoned if not use \N{CROSS MARK}. \nPlease don't use jdjgsummon to suggest something use suggest to suggest something, alright? If you want to contact me directly, you can find my tag using owner(please don't use jdjgsummon for suggest stuff thanks)", view = view)

    await view.wait()

    if view.value is None:
      return await ctx.reply("You let me time out :(")

    if view.value is True:
      message = await ctx.send(content=f'Summoning JDJG now a.k.a the Bot Owner to the guild make sure invite permissions are open!')
      await msg.delete()

      if isinstance(ctx.channel, discord.threads.Thread):
        
        channel = self.bot.get_channel(ctx.channel.parent_id)
        
        ctx.channel = channel if channel else ctx.channel

      if isinstance(ctx.channel, discord.TextChannel):
        await asyncio.sleep(1)
        await message.edit(content = "This is attempting to make an invite")

        invite = None
        with contextlib.suppress(discord.NotFound, discord.HTTPException):
          invite = await ctx.channel.create_invite(max_uses = 0)
        
        if not invite:
          await asyncio.sleep(1)
          return await message.edit(content = "Failed making an invite. You likely didn't give it proper permissions(a.k.a create invite permissions) or it errored for not being found.")

        else:
          await asyncio.sleep(1)
          await message.edit(content = "Contacting JDJG...")

          jdjg = await self.bot.getch_user(168422909482762240)

          embed = discord.Embed(title = f"{ctx.author} wants your help", description = f"Invite: {invite.url} \nChannel : {ctx.channel.mention} \nName : {ctx.channel}", color = random.randint(0, 16777215))

          embed.set_footer(text = f"Guild: {ctx.guild} \nGuild ID: {ctx.guild.id}")
        
          await jdjg.send(embed = embed)

      if isinstance(ctx.channel, discord.DMChannel):
        await asyncio.sleep(1)
  async def report_issue(self, ctx):
    await ctx.send("if you have an issue please join the support server, create a ticket,  or Dm the owner at JDJG Inc. Official#3493. Thanks :D!")

  @commands.command(brief = "apply for tester")
  async def apply_tester(self, ctx, *, reason = None):
    if not reason:
      return await ctx.send("Give us a reason why please.")

    embed = discord.Embed(title = f"{ctx.author} requested to be a tester.", description = f"For the reason of {reason}", color = random.randint(0, 16777215))
    embed.set_footer(text=f"User ID: {ctx.author.id}")

    shadi = await self.bot.getch_user(717822288375971900) 
    jdjg = await self.bot.getch_user(168422909482762240) 
    
    await jdjg.send(embed = embed)
    await shadi.send(embed = embed)

    await ctx.send("the application went through to JDJG, please make your DMs open to JDJG so we can talk to you. Don't send it again.")

  class PrefixesEmbed(menus.ListPageSource):
    async def format_page(self, menu, item):
      embed = discord.Embed(title="Usable Prefixes:",description=item, color = random.randint(0, 16777215))
      return embed

  @commands.command(brief="Lists the current prefixes that could be used.")
  async def prefixes(self, ctx):
    prefixes=await self.bot.get_prefix(ctx.message)
    pag = commands.Paginator()
    for p in prefixes:
      pag.add_line(f"{p}")

    pages = [page.strip("`") for page in pag.pages]

    menu = ViewMenuPages(self.PrefixesEmbed(pages, per_page=1),delete_message_after=True)
    await menu.start(ctx)
    
  @commands.command(brief="Lists the current used prefix",aliases=["prefix"])
  async def currentprefix(self, ctx):
    embed = discord.Embed(title = "Current Prefix:", description = f"{ctx.prefix}", color=random.randint(0, 16777215))
    await ctx.send(content = f"Current Prefix: {ctx.prefix}", embed = embed, allowed_mentions = discord.AllowedMentions.none())
  
  @commands.command(brief = "Gives the bot's uptime")
  async def uptime(self, ctx):
    delta_uptime = discord.utils.utcnow() - self.bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    embed = discord.Embed(title = f"Up Since:\n{discord.utils.format_dt(self.bot.launch_time, style = 'd')}\n{discord.utils.format_dt(self.bot.launch_time, style = 'T')}" ,description = f"Days: {days}d, \nHours: {hours}h, \nMinutes: {minutes}m, \nSeconds: {seconds}s",  color = random.randint(0, 16777215))
    
    embed.set_author(name = f"{self.bot.user}'s Uptime:", icon_url = self.bot.user.avatar.url)

    await ctx.send(embed = embed)

  @commands.command(brief = "make a suggestion to the bot owner of a command to add", aliases = ["suggestion"])
  async def suggest(self, ctx, *, args = None):
    if not args:
      return await ctx.send("You didn't give me a command to add to the suggestion.")

    embed = discord.Embed(title = f"New Suggestion requested by {ctx.author}", description = f"Suggestion: {args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_footer(text = f"User ID: {ctx.author.id}")
    embed.set_image(url = ctx.author.avatar.url)

    jdjg = await self.bot.getch_user(168422909482762240)
    await jdjg.send(f"New suggestion from {ctx.author}", embed = embed)

    await ctx.send("Sent suggestion to JDJG! You agree to being Dmed about this suggestion or somehow contacted(it makes some things easier lol)")

  @commands.group(name = "support", invoke_without_command=True)
  async def support(self, ctx):

    page = "\n".join(f"{c.name}" for c in ctx.command.commands)

    await ctx.send(f"Please run the subcommands with the prefix {ctx.prefix}: \n{page}")

  @support.command(brief = "a command that Dms support help to JDJG", name = "dm")
  async def support_dm(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("You need a reason why you want support.")
    
    await ctx.send("sending support to JDJG, the message will be deleted when support is done")
    
    embed = discord.Embed(title = f"{args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_author(name=f"Help Needed from {ctx.author}:", icon_url = ctx.author.avatar.url)
    embed.set_footer(text = f"{ctx.author.id} \nSupport Mode: DM")
    embed.set_thumbnail(url="https://i.imgur.com/lcND9Z2.png")

    jdjg = await self.bot.getch_user(168422909482762240) 

    await jdjg.send(content = "someone needs help! Remeber to delete when done with support.", embed = embed)

    await ctx.send(f"successfully sent to {jdjg}")

  @support.command(brief = "a command that sends support help to our log channel", name = "channel")
  async def support_channel(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("You didn't give a reason that you need support")

    embed = discord.Embed(title = f"{args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_author(name = f"Help Needed from {ctx.author}:", icon_url = ctx.author.avatar.url)

    embed.set_footer(text = f"{ctx.author.id} \nSupport Mode: Channel")
    embed.set_thumbnail(url="https://i.imgur.com/lcND9Z2.png")

    await self.bot.get_channel(855217084710912050).send(content = "someone needs help! Remeber to delete when done with support.", embed = embed)

    await ctx.send("successfully sent to the support channel!")

def setup(bot):
  bot.add_cog(Bot(bot))