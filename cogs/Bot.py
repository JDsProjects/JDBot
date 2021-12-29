from discord.ext import commands, tasks
import discord, random, time, asyncio, difflib, contextlib, platform, psutil, os, typing, inspect

import utils
from discord.ext.commands.cooldowns import BucketType

class Bot(commands.Cog):
  "Basic info about the bot and quick commands to get you access to support"
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
  async def ping(self, ctx):
    start = time.perf_counter()
    message = await ctx.send("Ping")
    end = time.perf_counter()

    embed = discord.Embed(title = "Bot Ping Data", color = 15428885, timestamp = ctx.message.created_at)

    embed.add_field(name = "Bot Latency:", value = f"{round((end - start)*1000)} MS", inline = False)

    embed.add_field(name = "Websocket Response time:", value = f"{round(self.bot.latency*1000)} MS", inline = False)

    await message.edit(content = f"Pong", embed = embed)
  
  @commands.command(brief="gives you an invite to invite the bot.", aliases = ["inv"])
  async def invite(self, ctx):
    normal_inv = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 8))
    minimial_invite = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 70635073))

    embed = discord.Embed(title="Invite link:", color = random.randint(0, 16777215))
    embed.add_field(name=f"{self.bot.user.name} invite:", value=f"[{self.bot.user.name} invite url]({normal_inv}) \nNon Markdowned invite : {normal_inv}")
    embed.add_field(name = "Minimial permisions", value = f"{ minimial_invite}")

    embed.set_thumbnail(url = self.bot.user.display_avatar.url)
    embed.set_footer(text = f"not all features may work if you invite with minimal perms, if you invite with 0 make sure these permissions are in a Bots/Bot role.")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = f"{self.bot.user.name}'s Normal invite", url = normal_inv, style = discord.ButtonStyle.link))
    view.add_item(discord.ui.Button(label = f"{self.bot.user.name}'s Minimial Permisions Invite", url = minimial_invite, style = discord.ButtonStyle.link))

    await ctx.send(embed = embed, view = view)

  @commands.command(brief="gives you an invite to invite the bot.", aliases = ["inv_slash", "slash_invite"])
  async def invite_slash(self, ctx):
    
    embed = discord.Embed(title="Invite link:", color = random.randint(0, 16777215))

    normal_inv_slash = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 8), scopes = ("bot", "applications.commands"))

    minimial_invite_slash = discord.utils.oauth_url(self.bot.user.id, permissions = discord.Permissions(permissions = 70635073),  scopes = ("bot", "applications.commands"))

    embed.add_field(name=f"{self.bot.user.name} invite with slash:", value=f"[{self.bot.user.name} invite url]({normal_inv_slash}) \nNon Markdowned invite : {normal_inv_slash}")
    embed.add_field(name = "Minimial permisions with slash", value = f"{minimial_invite_slash}")

    embed.set_thumbnail(url = self.bot.user.display_avatar.url)
    embed.set_footer(text = f"not all features may work if you invite with minimal perms, if you invite with 0 make sure these permissions are in a Bots/Bot role.(this is with slash commands added as well)")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = f"{self.bot.user.name}'s Normal Invite with Slash", url = normal_inv_slash, style = discord.ButtonStyle.link, row = 1))
    view.add_item(discord.ui.Button(label = f"{self.bot.user.name}'s Minimial Permisions Invite with Slash", url = minimial_invite_slash, style = discord.ButtonStyle.link, row = 1))

    await ctx.send(embed = embed, view = view)

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

    owner = await support_guild.try_member(owner_id) or await self.bot.try_user(owner_id)

    user_type = ("Bot" if owner.bot else "User")
    
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


    flags = owner.public_flags.all()
    
    badges="\u0020".join(utils.profile_converter(f.name) for f in flags)

    if owner.bot: badges = f"{badges} {utils.profile_converter('bot')}"
    
    embed=discord.Embed(title=f"Bot Owner: {owner}",color = random.randint(0, 16777215), timestamp = ctx.message.created_at)
    
    embed.add_field(name = "User Info: ", value = f"**Username**: {owner.name} \n**Discriminator**: {owner.discriminator} \n**ID**: {owner.id}")

    embed.add_field(name = "User Info 2:", value = f"Type: {user_type} \nBadges: {badges} \n**Joined Discord**: {discord.utils.format_dt(owner.created_at, style = 'd')}\n{discord.utils.format_dt(owner.created_at, style = 'T')}\n**Status**: {status}")
    
    embed.add_field(name = "Guild Info:", value = f"**Nickname**: {nickname} \n**Joined Guild**: {joined_guild} \n**Highest Role**: {highest_role}")

    embed.set_footer(text = f"Support Guild's Name: \n{support_guild}")    

    embed.set_image(url = owner.display_avatar.url)

    guilds_list = utils.grab_mutualguilds(ctx, owner)

    pag = commands.Paginator()

    for g in guilds_list:
      pag.add_line(f"{g}")

    pages = [page.strip("`") for page in pag.pages]
    pages = pages or ["None"]

    if (ctx.author.dm_channel is None):
        await ctx.author.create_dm()
    
    menu = utils.MutualGuildsEmbed(pages, ctx = ctx, disable_after = True)
    view = utils.dm_or_ephemeral(ctx, menu, ctx.author.dm_channel)
    
    view.message = await ctx.send("Pick a way for Mutual Guilds to be sent to you or not if you really don't the mutualguilds", embed = embed, view = view)

  @commands.command(help = "a command to give information about the team", brief = "this command works if you are in team otherwise it will just give the owner.")
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

    embed.set_image(url = information.icon.url if information.icon else self.bot.display_avatar.url)
    #I don't gunatree this works, but I hope it does.

    for x in team_members:
      embed.add_field(name=x,value=x.id)
    await ctx.send(embed=embed)

  @commands.command(help="get the stats of users and members in the bot",brief="this is an alternative that just looking at the custom status time to time.")
  async def stats(self, ctx):
    embed = discord.Embed(title="Bot stats", color=random.randint(0, 16777215))
    embed.add_field(name="Guild count",value=len(self.bot.guilds))
    embed.add_field(name="User Count:",value=len(self.bot.users))
    embed.add_field(name="True Command Count:",value=f"{len(list(self.bot.walk_commands()))}")
    embed.add_field(name="Command Count:",value=f"{len(self.bot.commands)}")
    embed.add_field(name = "Usable Command Count:", value=f"{len(await utils.filter_commands(ctx, self.bot.commands))}")
    embed.add_field(name = "Approximate Member Count:", value = f"{sum(g.member_count for g in self.bot.guilds)}")
    embed.set_footer(text = f"if you at all don't get what this means, you can ask our support team, if you do understand you can ask for clarification")
    await ctx.send(embed = embed)
  
  @commands.command(brief = "finds out where the location of the command on my github repo(so people can learn from my commands)")
  async def source(self, ctx, *, command = None):
    github_url = "https://github.com/JDJGInc/JDBot"
    branch = "master"

    embed = discord.Embed(title = "Github link", description = f"{github_url}", color = 15428885, timestamp = ctx.message.created_at)

    embed.set_footer(text = "This Bot's License is MIT, you must credit if you use my code, but please just make your own, if you don't know something works ask me, or try to learn how mine works.")
    
    if command is None:
      return await ctx.send("Here's the github link:", embed = embed)

    command_wanted = self.bot.get_command(command)
    if not command_wanted:
      return await ctx.send(f"Couldn't find {command}. Here's source anyway:", embed = embed)

    src = command_wanted.callback.__code__
    filename = src.co_filename

    module = command_wanted.callback.__module__

    if command == "help":
      src = type(self.bot.help_command)
      module = src.__module__
      filename = inspect.getsourcefile(src)

    
    lines, firstline = inspect.getsourcelines(src)

    check_path = filename.startswith(os.getcwd())
    filename = module.replace('.', '/') + '.py'

    if not check_path:

      if module.startswith("jishaku"):
        github_url = "https://github.com/Gorialis/jishaku"

      elif module.startswith("discord"):
        github_url = "https://github.com/iDevision/enhanced-discord.py"
        branch = "2.0.0"

      else:
        module = module.split(".")[0]
        return await ctx.send(f"We don't support getting the source of {module}. Here's my bot's source:", embed = embed)

    embed.title = f"Source for {command_wanted}:"
    embed.description = f"[**Click Here**]({github_url}/blob/{branch}/{filename}#L{firstline}-L{firstline + len(lines)-1})"

    await ctx.send(embed = embed)
  
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

  @commands.command(brief="Privacy Policy", aliases = ["privacy"])
  async def promises(self, ctx):
    embed = discord.Embed(title = "Privacy Policy", color = random.randint(0, 16777215))
    embed.add_field(name = "1:", value = "We have a logging channel that notifies us when the bot joins or leaves a guild")

    embed.add_field(name = "2:", value = "We log errors that occured in the bot(although it might contain private information). This is only visible temporarily in console, and is not stored in any of our DBs.")
    embed.add_field(name = "3:", value = "We store user ids for economy commands (Opt In)")
    embed.add_field(name = "4:", value = "We store user id , and support channel id, as well as last time it was used(for archive reasons), for allowing ticket based support. (Opt In)")
    embed.add_field(name = "5:", value = "We store inputted invalid commands")
    embed.add_field(name = "6:", value = "We may temporarily look at your mutual guilds with our bot or the list of servers our bot is in, with some information, just to check if any problems occured(like if a command is going hayware) or to prevent abuse. If you want to look at what is sent in embeds, just ask, We will show you.")
    embed.add_field(name = "6.1:", value = "This is a temp command, which is stored no where else, and we also delete the embed when done :D. If you have a problem with this contact me.")
    embed.add_field(name = "7:", value = "Any message content in global chat is logged to a private channel on discord with included channel ids, and guild ids, but otherwise, message content is not stored, except in moderation channels, and user ids are used to blacklist users per guild or globaly, or tell who is mod or staff or just a normal user.")
    embed.add_field(name = "8:", value = "In the future we will store the guild id and channel id for member joining/leaving messages, and member changes")
    embed.add_field(name = "Final:", value = "There should be no more except the sus list(list of ids I put together by hand of people who probaly shouldn't hang out with). We also now use the built in discord.py guild.members list with cache_member to only use memory to store you, we only use this to limit api calls(it's only opt in anyway)")
    embed.add_field(name = "Who Gets this info:", value = "Only us, and our DB provider MongoDB(but they are unlikely to use our data. Sus users do show up if they exist in the same guild though and the reason why.")
    embed.add_field(name = "More Info:", value="Contact me at JDJG Inc. Official#3493")
    await ctx.send(embed = embed)

  @commands.command(brief="Sends you an invite to the official Bot support guild",aliases=["guild_invite"])
  async def support_invite(self, ctx):
    
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label = f"Support Guild Invite", url = "https://discord.gg/sHUQCch", style = discord.ButtonStyle.link, row = 1))
    await ctx.send("If you press the button you will be invited to our guild :D, you can also manually use discord.gg/sHUQCch", view = view)

  @commands.command(brief="This command gives you an alt bot to use",aliases=["alt_invite", "alt_bot"])
  async def verify_issue(self, ctx):
    await ctx.send("You can invite the bot 831162894447804426(this will be an alt bot with almost the same code but with javascript though some report functionalies will have their guild swapped :D")

  @commands.command()
  async def whyprefixtest(self,ctx):
    await ctx.send("Because I don't have any alternative suggestions, and I don't feel like changing it to jd! or something. I can confirm this isn't a test bot :D")

  @commands.command()
  async def closest_command(self, ctx, *, command = None):
    if command is None:
      await ctx.send("Please provide an arg.")

    if command:

      all_commands = list(self.bot.walk_commands())
    
      command_names = [f"{x}" for x in await utils.filter_commands(ctx, all_commands)]

      #only reason why it's like this is uh, it's a bit in variable.

      matches = difflib.get_close_matches(command, command_names)
    
      if matches:
        await ctx.send(f"Did you mean... `{matches[0]}`?")

      else:
        await ctx.send("got nothing sorry.")

 
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "a command to automatically summon by creating an invite and having jdjg look at something if it's there something wrong")
  async def jdjgsummon(self, ctx):

    view = utils.BasicButtons(ctx)
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

          jdjg = await self.bot.try_user(168422909482762240)

          embed = discord.Embed(title = f"{ctx.author} wants your help", description = f"Invite: {invite.url} \nChannel : {ctx.channel.mention} \nName : {ctx.channel}", color = random.randint(0, 16777215))

          embed.set_footer(text = f"Guild: {ctx.guild} \nGuild ID: {ctx.guild.id}")
        
          await jdjg.send(embed = embed)

      if isinstance(ctx.channel, discord.DMChannel):
        await asyncio.sleep(1)
        return await message.edit(content = "This is meant for guilds not Dm channel if you want support in DM channel contact the owner, By DMS at JDJG Inc. Official#3493.")

    if view.value is False:
      await ctx.send(content = f" You didn't agree to summoning me. So I will not be invited.")
      await msg.delete()

  @commands.command(brief = "this command tells you to how to report ex issues to owner")
  async def report_issue(self, ctx):
    await ctx.send("if you have an issue please join the support server, create a ticket,  or Dm the owner at JDJG Inc. Official#3493. Thanks :D!")

  @commands.command(brief = "apply for tester")
  async def apply_tester(self, ctx, *, reason = None):
    if not reason:
      return await ctx.send("Give us a reason why please.")

    embed = discord.Embed(title = f"{ctx.author} requested to be a tester.", description = f"For the reason of {reason}", color = random.randint(0, 16777215))
    embed.set_footer(text=f"User ID: {ctx.author.id}")

    shadi = await self.bot.try_user(717822288375971900) 
    jdjg = await self.bot.try_user(168422909482762240) 
    
    await jdjg.send(embed = embed)
    await shadi.send(embed = embed)

    await ctx.send("the application went through to JDJG, please make your DMs open to JDJG so we can talk to you. Don't send it again.")

  @commands.command(brief="Lists the current prefixes that could be used.")
  async def prefixes(self, ctx):
    prefixes=await self.bot.get_prefix(ctx.message)
    pag = commands.Paginator()
    for p in prefixes:
      pag.add_line(f"{p}")

    pages = [page.strip("`") for page in pag.pages]

    menu = utils.PrefixesEmbed(pages, ctx = ctx, delete_message_after = True)

    await menu.send(ctx.channel)
    
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
    
    embed.set_author(name = f"{self.bot.user}'s Uptime:", icon_url = self.bot.user.display_avatar.url)

    await ctx.send(embed = embed)

  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "make a suggestion to the bot owner of a command to add", aliases = ["suggestion"])
  async def suggest(self, ctx, *, args = None):
    if not args:
      return await ctx.send("You didn't give me a command to add to the suggestion.")
      ctx.command.reset_cooldown(ctx)

    embed = discord.Embed(title = f"New Suggestion requested by {ctx.author}", description = f"Suggestion: {args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_footer(text = f"User ID: {ctx.author.id}")
    embed.set_image(url = ctx.author.display_avatar.url)

    jdjg = await self.bot.try_user(168422909482762240)
    await jdjg.send(f"New suggestion from {ctx.author}", embed = embed)

    await ctx.send("Sent suggestion to JDJG! You agree to being Dmed about this suggestion or somehow contacted(it makes some things easier lol)")

  @commands.group(name = "support", invoke_without_command = True)
  async def support(self, ctx):

    page = "\n".join(f"{c.name}" for c in ctx.command.commands)

    await ctx.send(f"Please run the subcommands with the prefix {ctx.prefix}: \n{page}")

  @support.command(brief = "a command that Dms support help to JDJG", name = "dm")
  async def support_dm(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("You need a reason why you want support.")
    
    await ctx.send("sending support to JDJG, the message will be deleted when support is done")
    
    embed = discord.Embed(title = f"{args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_author(name=f"Help Needed from {ctx.author}:", icon_url = ctx.author.display_avatar.url)
    embed.set_footer(text = f"{ctx.author.id} \nSupport Mode: DM")
    embed.set_thumbnail(url="https://i.imgur.com/lcND9Z2.png")

    jdjg = await self.bot.try_user(168422909482762240) 

    await jdjg.send(content = "someone needs help! Remeber to delete when done with support.", embed = embed)

    await ctx.send(f"successfully sent to {jdjg}")

  @support.command(brief = "a command that sends support help to our log channel", name = "channel")
  async def support_channel(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("You didn't give a reason that you need support")

    embed = discord.Embed(title = f"{args}", timestamp = ctx.message.created_at, color = random.randint(0, 16777215))

    embed.set_author(name = f"Help Needed from {ctx.author}:", icon_url = ctx.author.display_avatar.url)

    embed.set_footer(text = f"{ctx.author.id} \nSupport Mode: Channel")
    embed.set_thumbnail(url="https://i.imgur.com/lcND9Z2.png")

    await self.bot.get_channel(855217084710912050).send(content = "someone needs help! Remeber to delete when done with support.", embed = embed)

    await ctx.send("successfully sent to the support channel!")

  @commands.command(brief = "information about donating")
  async def donate(self, ctx):
    await ctx.send("JDBot is completly free, but if you would love to donate you should run owner to see the owner of the bot to contact them about suggesting an idea, or I guess donating stuff. Though this is my lobby of mine. Just please don't steal my hard work.")

  
  @commands.command(brief = "Gives Information about JDBot")
  async def about(self, ctx):

    embed = discord.Embed(title = "About Bot", description = "Here you can view bot and author information", timestamp = ctx.message.created_at, color= 0xeb6d15)


    embed.add_field(name="Author Information", value="```This Bot is made by JDJG Inc. Official#3493(you can find out more about owners from the owner command).```", inline=False)

    embed.add_field(name="Bot Version", value="```1.0.0```")

    embed.add_field(name="Python Version:", value=f"```{platform.python_version()}```")

    embed.add_field(name="Library", value = "```discord.py```")

    embed.add_field(name="Discord.Py Version", value=f"```{discord.__version__}```")


    embed.add_field(name = "RAM Usage", value=f"```{(psutil.Process(os.getpid()).memory_full_info().rss / 1024**2):.2f} MB```")

    embed.add_field(name="Servers", value=f"```{len(self.bot.guilds)}```")

    embed.add_field(name = "Contributers", value = "```Shadi#9492 \nMiddlle#0101 \nDutchy#6127```")

    embed.add_field(name = "Sponsors", value="```No current sponsors :(```")

    embed.set_author(name = f"{self.bot.user}", icon_url = self.bot.user.display_avatar.url)

    embed.set_footer(text = "Learn More from: \nStats \nOr Any Other Bot Commands \nYou can Even Sponsor the Bot \nIf you want to sponsor the bot DM me. \nI hope I am not missing any contibutors or sponsors")

    await ctx.send(embed = embed)

  @commands.cooldown(1, 90, BucketType.user)
  @commands.command(brief = "sends a emoji to me to review(a.k.a reviewed in the review channel, you will be Dmed if you failed or not)")
  async def emoji_save(self, ctx, *, emoji : typing.Optional[discord.PartialEmoji] = None):
    
    if not emoji:
      await ctx.send("That's not a valid emoji or isn't a custom emoji")
      ctx.command.reset_cooldown(ctx)

    else:
      already_exists = False
      if emoji.id in [e.id for e in self.bot.emojis]:
        await ctx.send("That emoji was already added to the bot's emojis(sent it anyway)")
        already_exists = True

      if not emoji.id in [e.id for e in self.bot.emojis]:
        await ctx.send("The emoji is now in the bot's emoji review channel")
      
      embed = discord.Embed(title = "Emoji Submission", color = 5565960)

      embed.add_field(name = "Emoji", value = f"Regex: {emoji}\nName:{emoji.name} \nAnimated: {emoji.animated} \nEmoji Exists in bot's emoji: {already_exists}")

      embed.set_author(name = f"{ctx.author}", icon_url = ctx.author.display_avatar.url)

      embed.set_image(url = f"{emoji.url}")
      embed.set_footer(text = f"ID: {emoji.id}")

      await self.bot.get_channel(855217084710912050).send(embed = embed)


  @commands.command(brief = "gives you info if someone is a tester of the bot or not")
  async def is_tester(self, ctx, *, user : typing.Optional[discord.User] = None):
    user = user or ctx.author
    truth = user.id in self.bot.testers

    if user.bot: return await ctx.send(f"A bot can't be a tester. So {user} is not a tester")

    if not truth:
      await ctx.send(f"{user} is not in a tester.")

    else:
      await ctx.send(f"{user} is a tester")

  @commands.command(brief = "bug about massive Test")
  async def test_bug(self, ctx):
    await ctx.send(f"If you are a moderator please contact JDJG Inc. Official#3493, I made a mistake when doing the checks for just doing {self.bot.user.mention}, if you get a massive error or something wrong please contact me, thanks :D")

def setup(bot):
  bot.add_cog(Bot(bot))
