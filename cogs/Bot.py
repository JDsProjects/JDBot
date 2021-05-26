from discord.ext import commands, tasks
import discord, random , time, asyncio, difflib
import utils

class Bot(commands.Cog):
  def __init__(self,client):
    self.client = client
    self.status_task.start()

  @tasks.loop(seconds=40)
  async def status_task(self):
    await self.client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=f"the return of {self.client.user.name}"))
    await asyncio.sleep(40)
    await self.client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.client.guilds)} servers | {len(self.client.users)} users"))
    await asyncio.sleep(40)
    await self.client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the new updates coming soon..."))
    await asyncio.sleep(40)

  @status_task.before_loop
  async def before_status_task(self):
    await self.client.wait_until_ready()

  @commands.command(brief="sends pong and the time it took to do so.")
  async def ping(self,ctx):
    start = time.perf_counter()
    message=await ctx.send("Pong")
    end = time.perf_counter()
    await message.edit(content=f"Pong\nBot Latency: {((end - start)*1000)} MS\nWebsocket Response time: {self.client.latency*1000} MS")
  
  @commands.command(brief="gives you an invite to invite the bot.")
  async def invite(self,ctx):
    embed = discord.Embed(title="Invite link:",color=random.randint(0, 16777215))
    embed.add_field(name=f"{self.client.user.name} invite:",value=f"[{self.client.user.name} invite url](https://discord.com/oauth2/authorize?client_id={self.client.user.id}&scope=bot&permissions=8)")
    embed.add_field(name="Non Markdowned invite",value=f"https://discord.com/oauth2/authorize?client_id={self.client.user.id}&scope=bot&permissions=8")
    embed.set_thumbnail(url=self.client.user.avatar_url)
    await ctx.send(embed=embed)

  @commands.command(brief="gives you who the owner is.")
  async def owner(self,ctx):
    info = await self.client.application_info()
    if info.team is None:
      owner_id = info.owner.id
    if info.team:
      owner_id = info.team.owner_id

    support_guild=self.client.get_guild(736422329399246990)
    owner= await self.client.getch_member(support_guild,owner_id)
    user_type = user_type = ['User', 'Bot'][owner.bot]

    guilds_list=[guild for guild in self.client.guilds if guild.get_member(owner.id) and guild.get_member(ctx.author.id)]
    if not guilds_list:
      guild_list = "None"

    x = 0
    for g in guilds_list:
      if x < 1:
        guild_list = g.name
      if x > 0:
        guild_list = guild_list + f", {g.name}"
      x = x + 1
    
    if owner:
      nickname = str(owner.nick)
      joined_guild = owner.joined_at.strftime('%m/%d/%Y %H:%M:%S')
      status = str(owner.status).upper()
      highest_role = owner.roles[-1]
    
    if owner is None:
      nickname = "None"
      joined_guild = "N/A"
      status = "Unknown"
      for guild in self.client.guilds:
        member=guild.get_member(owner.id)
        if member:
          status=str(member.status).upper()
          break
      highest_role = "None Found"
    
    embed=discord.Embed(title=f"Bot Owner: {owner}",description=f"Type: {user_type}", color=random.randint(0, 16777215),timestamp=ctx.message.created_at)
    embed.add_field(name="Username:", value = owner.name)
    embed.add_field(name="Discriminator:",value=owner.discriminator)
    embed.add_field(name="Nickname: ", value = nickname)
    embed.add_field(name="Joined Discord: ",value = (owner.created_at.strftime('%m/%d/%Y %H:%M:%S')))
    embed.add_field(name="Joined Guild: ",value = joined_guild)
    embed.add_field(name="Part of Guilds:", value=guild_list)
    embed.add_field(name="ID:",value=owner.id)
    embed.add_field(name="Status:",value=status)
    embed.add_field(name="Highest Role:",value=highest_role)
    embed.set_image(url=owner.avatar_url)
    await ctx.send(embed=embed)

  @commands.command(help="a command to give information about the team",brief="this command works if you are in team otherwise it will just give the owner.")
  async def team(self,ctx):
    information=await self.client.application_info()
    if information.team == None:
      true_owner=information.owner
      team_members = []
    if information.team != None:
      true_owner = information.team.owner
      team_members = information.team.members
    embed=discord.Embed(title=information.name,color=random.randint(0, 16777215))
    embed.add_field(name="Owner",value=true_owner)
    embed.set_footer(text=f"ID: {true_owner.id}")
    embed.set_image(url=(information.icon_url))
    for x in team_members:
      embed.add_field(name=x,value=x.id)
    await ctx.send(embed=embed)

  @commands.command(help="get the stats of users and members in the bot",brief="this is an alternative that just looking at the custom status time to time.")
  async def stats(self,ctx):
    embed = discord.Embed(title="Bot stats",color=random.randint(0, 16777215))
    embed.add_field(name="Guild count",value=len(self.client.guilds))
    embed.add_field(name="User Count:",value=len(self.client.users))
    embed.add_field(name="True Command Count:",value=f"{len(list(self.client.walk_commands()))}")
    embed.add_field(name="Command Count:",value=f"{len(self.client.commands)}")
    await ctx.send(embed=embed)

  @commands.command(brief="a way to view open source",help="you can see the open source with the link it provides")
  async def open_source(self,ctx):
    embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot.",color=random.randint(0, 16777215))
    embed.set_author(name=f"{self.client.user}'s source code:",icon_url=(self.client.user.avatar_url))
    await ctx.send(embed=embed)

  @commands.group(name="open",invoke_without_command=True)
  async def source(self,ctx):
    embed = discord.Embed(title="Project at:\nhttps://github.com/JDJGInc/JDBot !",description="you can also contact the owner if you want more info(by using the owner command) you can see who owns the bot.",color=random.randint(0, 16777215))
    embed.set_author(name=f"{self.client.user}'s source code:",icon_url=(self.client.user.avatar_url))
    await ctx.send(embed=embed)  
  
  @commands.command(brief="a set of rules we will follow")
  async def promise(self,ctx):
    #embed=discord.Embed(title="Promises we will follow:",color=random.randint(0, 16777215))
    #embed.add_field(name="Rule 1:",value="if you are worried about what the bot may collect, please send a DM to the bot, and we will try to compile the data the bot may have on you.")
    #embed.add_field(name="Rule 2:",value="in order to make sure our bot is safe, we will be making sure the token is secure and making sure anyone who works on the project is very trustworthy.")
    #embed.add_field(name="Rule 3:",value="we will not nuke your servers, as this happened to us before and we absolutely hated it.")
    #embed.add_field(name="Rule 4:",value="We will also give you a list of suspicious people")
    #embed.add_field(name="Rule 5:",value="we also made sure our code is open source so you can see what it does.")
    #embed.add_field(name="Rule 6:",value="We will also let you ask us questions directly, just DM me directly(the owner is listed in the owner command(and anyone should be able to friend me)")
    #embed.add_field(name="Rule 7:",value="Using our bot to attempt to break TOS, will cause us to ban you from using the bot, then upgrade our security")
    #embed.add_field(name="Rule 8:",value="Attempting to break discord TOS like having a giveaway but having people require to join an external guild(will eventually be reportable to us, if they owner counties, then the reporter should report to discord.(essentially breaking TOS near the functionalties with our bot)")
    #embed.add_field(name="Rule 9:",value="If our bot doesn't do the giveaway requirements we're actually safe, as we don't require it, however please report this to us, so we can contact them to get them to stop, Thanks. if they don't listen we'll tell you, then you can report them.")
    #await ctx.send(embed=embed)
    embed=discord.Embed(title="Basic rights that we guarantee", description="The promises we make about our privacy policy", color=0xffb300)
    embed.add_field(name="\u2800", value="If you wish to know what the bot knows about you please send a DM to the bot, and we will try to compile the data the bot may have on you.", inline=True)
    embed.add_field(name="\u2800", value="For the safety of the bot, we will be making sure the token is secure and making sure anyone who works on the project is very trustworthy.", inline=True)
    embed.add_field(name="\u2800", value="We will not nuke your servers, as this happened to us before and we absolutely hated it.", inline=True)
    await ctx.send(embed=embed)
    embed=discord.Embed(title="Basic rights that we guarantee", description="The promises we make about our privacy policy", color=0xffb300)
    embedtwo.set_author(name="Page 2")
    embedtwo.add_field(name="\u2800", value="The bot also has a feature to give you a list of suspicious people which shall never be removed", inline=True)
    embedtwo.add_field(name="\u2800", value="The bot source code is open source and that allows you to make sure the bot is safe and secure and even host your own instance", inline=True)
    embedtwo.add_field(name="\u2800", value="We also let you ask us questions directly, just DM me or any other maintainer directly (the owner is listed in the owner command(and anyone should be able to friend me or the maintaners)", inline=True)
    await ctx.send(embed=embedtwo)
    embedfinal=discord.Embed(title="Basic rights that we guarantee", description="The promises we make about our privacy policy", color=0xffb300)
    embedfinal.set_author(name="Page 3")
    embedfinal.add_field(name="\u2800", value="Using our bot to attempt to break TOS, will cause us to ban you from using the bot, and afterwars upgrade our security", inline=True)
    embedfinal.add_field(name="\u2800", value="Attempting to break discord TOS like having a giveaway but requiring people to join an external guild(will eventually be reportable to us, if the owner or the giveaway holder countinues then it should be reported to discord.(essentially breaking TOS using the functionalties our bot provides)", inline=True)
    embedfinal.add_field(name="\u2800", value="If our bot doesn't do the giveaway requirements properly, as we don't enforce them, you can however report this to us, so we can contact the person abusing the bot to atempt to get them to stop, Thanks. if they don't listen we'll tell you, then you can report them.", inline=True)
    await ctx.send(embed=embedfinal)
    

  @commands.command(brief="Privacy Policy",aliases=["privacy","promises"])
  async def privacypolicy(self,ctx):
 #   embed=discord.Embed(title="Privacy Policies",color=random.randint(0, 16777215))
 #   embed.add_field(name="1:",value="We have a channel that logs when the bot joins or leaves a guild")
 #   embed.add_field(name="2:",value="We will store any errors(which may go back to you, but this is console only.) This is in memory anyway, thus it doesn't store in any of our DBs.")
  #   embed.add_field(name="3:",value="we will only store user ids(in the future for balance commands and economy commands(opt in only)")
 #    embed.add_field(name="4:",value="We will store user id, and channel id(our channel), and last active, for ticket support if you need support. (is opt in)")
  #  embed.add_field(name="5:",value="we Finally store invalid commands")
  #  embed.add_field(name="6:",value="We may temporarily look at your mutual guilds with our bot or the list of servers our bot is in, with some information, just to test some things(like if a command is going hayware) or prevent abuse. If you want to look at the embeds with this, just ask, We will show you.")
 #   embed.add_field(name="6.1:",value="This is a temp command, which is stored no where else, and we also delete the embed when done :D. If you have a problem with this contact me.")
 #   embed.add_field(name="Final:",value="There should be no more except the sus list(list of ids I put together by hand of people who probaly shouldn't hang out with)")
#    embed.add_field(name="Who Gets this info:",value="Only us, and our DB provider MongoDB(but they are unlikely to use our data. Sus users do show up if they exist in the same guild though and the reason why.")
#    embed.add_field(name="More Info:",value="Contact me at JDJG Inc. Official#3493")
 #   await ctx.send(embed=embed)
     embed=discord.Embed(title="Our privacy policy ", description="This privacy policy applies to JDbot and other services ", color=0xffb300)
     embed.add_field(name="Our data request policy ", value="If you wish to know what the bot knows about you please send a DM to the bot, and we will try to compile the data the bot may have on you.", inline=True)
     embed.add_field(name="The data we collect ", value="We have a channel that logs when the bot joins or leaves a guild", inline=True)
     embed.add_field(name="\u2800", value="We will store any errors(which may go back to you, but this is console only.) This is in memory anyway, thus it doesn't store in any of our DBs.", inline=False)
     embed.set_footer(text="For more info please contact me at JDJG Inc. Official#3493 ")
     await ctx.send(embed=embed)
     embedtwo=discord.Embed(title="Our privacy policy ", description="This privacy policy applies to JDbot and other services ", color=0xffb300)
     embedtwo.set_author(name="Page 2")
     embedtwo.add_field(name="Continuation of previous page", value="We store the inputted invalid commands", inline=True)
     embedtwo.add_field(name="\u2800", value="We will in the future store user ids for balance commands and economy commands(opt in only) ", inline=True)
     embedtwo.add_field(name="\u2800", value="We currently store user ids, and channel ids(our channel), and last active channel, for ticket support if you will require support. (Opt in) ", inline=False)
     embedtwo.set_footer(text="For more info please contact me at JDJG Inc. Official#3493 ")
     await ctx.send(embed=embedtwo)
     embedfinal=discord.Embed(title="Our privacy policy", description="This privacy policy applies to JDbot and other services", color=0xffb300)
     embedfinal.set_author(name="Page 3")
     embedfinal.add_field(name="Continuation of previous page", value="We may reserve the right to look at your mutual guilds with our bot in it or the list of servers our bot is in, with some information, just to test some things(like if a command is going hayware) or prevent abuse. If you want to look at the embeds with this, just ask, We will show you.", inline=True)
     embedfinal.add_field(name="\u2800", value="We also have a suspicious users list that is used to store a list of users who may cause problems on your servers and that you should probably avoid ", inline=True)
     embedfinal.add_field(name="\u2800", value="This data can be accessed only by us, and our DB provider MongoDB(but they are unlikely to use our data). Suspicious users will show up if they exist in the same guild though and the reason why.", inline=True)
     await ctx.send(embed=embedfinal)

  @commands.command(brief="Sends you an invite to the official Bot support guild",aliases=["guild_invite"])
  async def support_invite(self,ctx):
    await ctx.send("You must say I agree this will send into the current channel.")
    message=await self.client.wait_for("message",check=utils.check(ctx))
    if message.content.lower() == "i agree":
      await ctx.send("https://discord.gg/sHUQCch")

  @commands.command(brief="This command gives you an alt bot to use",aliases=["alt_invite"])
  async def verify_issue(self,ctx):
    await ctx.send("You can invite the bot 831162894447804426(this will be an alt bot with almost the same code though some report functionalies will have their guild swapped :D")

  @commands.command()
  async def whyprefixtest(self,ctx):
    await ctx.send("Because I don't have any alternative suggestions, and I don't feel like changing it to jd! or something. I can confirm this isn't a test bot :D")

  @commands.command()
  async def closest_command(self,ctx,*,command=None):
    if command is None:
      await ctx.send("Please provide an arg.")

    if command:
      command_names = [str(x) for x in ctx.bot.commands]
      matches = difflib.get_close_matches(command, command_names)
      
      if matches:
        await ctx.send(f"Did you mean... `{matches[0]}`?")

      else:
        await ctx.send("got nothing sorry.")

def setup(client):
  client.add_cog(Bot(client))
