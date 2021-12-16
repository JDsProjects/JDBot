from discord.ext import commands
import utils
import random , discord, os, importlib, typing, aioimgur, functools, tweepy
import traceback, textwrap
from discord.ext.menus.views import ViewMenuPages

class Owner(commands.Cog):
  "Owner Only Commands"
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="a command to send mail")
  async def mail(self, ctx, *, user: utils.BetterUserconverter = None):
    if user is None:
      await ctx.reply("User not found, returning Letter")
      user = ctx.author
    if user:
      await ctx.reply("Please give me a message to use.")
      message = await self.bot.wait_for("message",check = utils.check(ctx))
      embed_message = discord.Embed(title=message.content, timestamp=(message.created_at), color=random.randint(0, 16777215))
      embed_message.set_author(name=f"Mail from: {ctx.author}",icon_url=(ctx.author.display_avatar.url))
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
      await self.bot.get_channel(855217084710912050).send(embed=embed_message)

  @commands.command()
  async def load(self, ctx, *, cog = None):
    if cog:
      try:
        self.bot.load_extension(cog)
      except Exception as e:
        await ctx.send(e)
        traceback.print_exc()

      await ctx.send("Loaded cog(see if there's any errors)")

    if cog is None:
      await ctx.send("you can't ask to load no cogs.")
  
  @commands.command()
  async def reload(self, ctx, *, cog = None):
    
    cog = cog or "all"

    if cog == "all":
      for x in list(self.bot.extensions):
        try:
          self.bot.reload_extension(x)
        except commands.errors.ExtensionError as e:
          await ctx.send(e)
          traceback.print_exc()

      await ctx.send("done reloading all cogs(check for any errors)")

    else:
      try:
        self.bot.reload_extension(cog)

      except commands.errors.ExtensionError as e:
        await ctx.send(e)
        traceback.print_exc()

      await ctx.send("Cog reloaded :D (check for any errors)")
  
  @commands.command()
  async def unload(self, ctx, *, cog = None):
    if cog:
      try:
        self.bot.unload_extension(cog)
      except commands.errors.ExtensionError as e:
        await ctx.send(e)
        traceback.print_exc()
      await ctx.send("Cog should be unloaded just fine :D.(check any errors)")
    if cog is None:
      await ctx.send("you can't ask to reload no cogs")

  @commands.command()
  async def shutdown(self, ctx):
    await ctx.send("shutdown/logout time happening.")
    await self.bot.close()

  async def cog_check(self, ctx):
    return await self.bot.is_owner(ctx.author)

  async def cog_command_error(self, ctx, error):
    if ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
      
      traceback.print_exc()

    #I need to fix all cog_command_error

  @commands.command(brief="Changes Bot Status(Owner Only)")
  async def status(self , ctx, *, args = None):

    await self.bot.change_presence(status=discord.Status.do_not_disturb, activity= discord.Activity(type=discord.ActivityType.watching,name=args))

    await ctx.send("Changed succesfully...")
  
  @commands.command(brief="Only owner command to change bot's nickname")
  async def change_nick(self, ctx, *, name = None):
      if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send("Changing Nickname")
        try:
          await ctx.guild.me.edit(nick=name)
        except discord.Forbidden:
          await ctx.send("Appears not to have valid perms")

      if isinstance(ctx.channel,discord.DMChannel):
        await ctx.send("You can't use that in Dms.")
  
  @commands.command(brief="a command to give a list of servers(owner only)",help="Gives a list of guilds(Bot Owners only)")
  async def servers(self, ctx):

    pag = commands.Paginator()
    for g in self.bot.guilds:
      pag.add_line(f"[{len(g.members)}/{g.member_count}] **{g.name}** (`{g.id}`) | {(g.system_channel or g.text_channels[0]).mention}")

    pages = [page.strip("`") for page in pag.pages]
    menu = ViewMenuPages(utils.ServersEmbed(pages, per_page=1),delete_message_after=True)

    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()

    await menu.start(ctx, channel = ctx.author.dm_channel)

  @commands.command(brief="only works with JDJG, but this command is meant to send updates to my webhook")
  async def webhook_update(self, ctx, *, args = None):
      if args:
        if isinstance(ctx.channel, discord.TextChannel):
          try:
            await ctx.message.delete()
          
          except:
            await ctx.send("It couldn't delete the message in this guils so, I kept it here.")
    
      webhook=discord.Webhook.from_url(os.environ["webhook99"], session = self.bot.session)
      embed=discord.Embed(title="Update",color=(35056),timestamp=(ctx.message.created_at))
      embed.add_field(name="Update Info:",value=args)
      embed.set_author(name="JDJG's Update",icon_url='https://i.imgur.com/pdQkCBv.png')
      embed.set_footer(text="JDJG's Updates")
      await webhook.send(embed=embed)

      await ctx.send("Sent Succesfully :D")

      if args is None:
        await ctx.send("You sadly can't use it like that.")

  @commands.command(brief="Commands to see what guilds a person is in.")
  async def mutualguilds(self, ctx, *, user: utils.BetterUserconverter = None):
    user = user or ctx.author
    pag = commands.Paginator()

    for g in user.mutual_guilds:
      pag.add_line(f"{g}")

    pages = [page.strip("`") for page in pag.pages]
    pages = pages or ["No shared servers"]

    menu = ViewMenuPages(utils.mutualGuildsEmbed(pages, per_page=1),delete_message_after = True)

    if (ctx.author.dm_channel is None):
        await ctx.author.create_dm()

    await menu.start(ctx, channel = ctx.author.dm_channel)

  @commands.command(brief="A command to add sus_users with a reason")
  async def addsus(self, ctx, *, user: utils.BetterUserconverter = None):
    if user is None:
      await ctx.send("can't have a user be none.")

    if user:
      await ctx.reply("Please give me a reason why:")
      reason = await self.bot.wait_for("message", check= utils.check(ctx))

      await self.bot.db.execute("INSERT INTO sus_users VALUES ($1, $2)", user.id, reason.content)
      
      await ctx.send("added sus users, succesfully")

  @commands.command(brief="a command to remove sus users.")
  async def removesus(self, ctx, *, user: utils.BetterUserconverter = None):
    if user is None:
      await ctx.send("You can't have a none user.")

    if user:

      await self.bot.db.execute("DELETE FROM sus_users WHERE user_id = $1", user.id)

      await ctx.send("Removed sus users.")

  @commands.command(brief="a command to grab all in the sus_users list")
  async def sus_users(self, ctx):
    sus_users = await self.bot.db.fetch("SELECT * FROM SUS_USERS;")
   
    menu = ViewMenuPages(utils.SusUsersEmbed(sus_users, per_page=1),delete_message_after=True)
    await menu.start(ctx)

  @sus_users.error
  async def sus_users_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief = "a command listed all the commands")
  async def testers(self, ctx):

    menu = ViewMenuPages(utils.TestersEmbed(self.bot.testers, per_page = 1), delete_message_after = True)
    await menu.start(ctx)

  @commands.command(aliases=["bypass_command"])
  async def command_bypass(self, ctx ,user: utils.BetterUserconverter = None, *, command = None):
    #make sure to swap to autoconverter if it gets added.
    user = user or ctx.author
    if command:
      command_wanted=self.bot.get_command(command)
      if command_wanted:
        await ctx.send(f"{command_wanted.name} now accessible for the {user} for one command usage!")
        self.bot.special_access[user.id]=command_wanted.name
      if command_wanted is None:
        await ctx.send("Please specify a valid command.")
    if command is None:
      await ctx.send("select a command :(")

  @commands.command(brief = "resets cooldown for you.",aliases = ["reset_cooldown"])
  async def resetcooldown(self, ctx, *, command = None):
    if not command:
      return await ctx.send("please specificy a command")
    
    command_wanted = self.bot.get_command(command)

    if not command_wanted:
      return await ctx.send("please specify a command")

    if not command_wanted.is_on_cooldown(ctx):
      return await ctx.send("That doesn't have a cooldown/isn't on a cooldown.")

    command_wanted.reset_cooldown(ctx)
    await ctx.send(f"reset cooldown of {command_wanted}")

  @commands.command(brief = "leaves a guild only use when needed or really wanted. Otherwise no thanks.")
  async def leave_guild(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
    guild = guild or ctx.guild
    if guild is None: return await ctx.send("Guild is None can't do anything.")
    await ctx.send("Bot leaving guild :(")
    try:
     await guild.leave()
    
    except Exception as e:
      await ctx.send(f"Somehow an error occured: {e}")
      traceback.print_exc()
  
  @commands.command()
  async def aioinput_test(self, ctx, *, args = None):
    args = args or "Test"

    result=await self.bot.loop.run_in_executor(None, input, (f"{args}:"))
    await ctx.send(f"Result of the input was {result}")

  @commands.command(brief="a powerful owner tool to reload local files that aren't reloadable.")
  async def reload_basic(self, ctx, *, args = None):
    if args is None:await ctx.send("Can't reload module named None")

    if args:
      try: module = importlib.import_module(name=args)
      except Exception as e:
        traceback.print_exc()
        return await ctx.send(e)

      try: value=importlib.reload(module)
      except Exception as e: 
        traceback.print_exc()
        return await ctx.send(e)

      await ctx.send(f"Sucessfully reloaded {value.__name__} \nMain Package: {value.__package__}")


  @commands.command(brief="backs up a channel and then sends it into a file or CharlesBin")
  async def channel_backup(self, ctx):

    messages = await ctx.channel.history(limit = None, oldest_first = True).flatten()

    new_line = "\n"
    
    page = "\n".join(f"{msg.author} ({('Bot' if msg.author.bot else 'User')}) : {msg.content} {new_line}Attachments : {msg.attachments}" if msg.content else f"{msg.author} ({('Bot' if msg.author.bot else 'User')}) : {new_line.join(f'{e.to_dict()}' for e in msg.embeds)} {new_line}Attachments : {msg.attachments}" for msg in messages)
    
    paste = await utils.post(self.bot, code = page)
    #max paste size is 400,000(find easiest to upload and to render then use textwrap in asyncio to handle it.)

    await ctx.author.send(content=f"Added text file to CharlesBin: \n{paste}")

  @channel_backup.error
  async def channel_backup_error(self, ctx, error):
    etype = type(error)
    trace = error.__traceback__

    values=''.join(map(str,traceback.format_exception(etype, error, trace)))
 
    pages = textwrap.wrap(values, width = 1992)

    menu = ViewMenuPages(utils.ErrorEmbed(pages, per_page = 1),delete_message_after = True)

    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()

    await menu.start(ctx, channel = ctx.author.dm_channel)

    paste = await utils.post(self.bot, code = values)
    #max paste size is 400,000(find easiest to upload and to render then use textwrap in asyncio to handle it.)

    await ctx.send(f"Traceback: {paste}")

  @commands.command(brief = "adds packages and urls to rtfm DB", aliases=["add_rtfm"])
  async def addrtfm(self, ctx, name = None, *, url = None):
    if not name or not url or not name and not url:
      return await ctx.send("You need a name and also url.")

    await self.bot.db.execute("INSERT INTO RTFM_DICTIONARY VALUES ($1, $2)", name, url)

    await ctx.send(f"added {name} and {url} to the rtfm DB")

  @commands.command(brief = "removes packages from the rtfm DB", aliases = ["remove_rtfm"])
  async def removertfm(self, ctx, *, name = None):
    if name is None:
      return await ctx.send("You can't remove None")

    await self.bot.db.execute("DELETE FROM RTFM_DICTIONARY WHERE name = $1", name)
    await ctx.send(f"Removed the rtfm value {name}.")

  @commands.command(brief = "a command to save images to imgur(for owner only lol)")
  async def save_image(self, ctx):
    if not ctx.message.attachments:
      return await ctx.send("You need to provide some attachments.")

    await ctx.send("JDJG doesn't take any responbility for what you upload here :eyes: don't upload anything bad okay?")

    for a in ctx.message.attachments:
      try:
        discord.utils._get_mime_type_for_image(await a.read())

      except Exception as e:
        traceback.print_exc()
        return await ctx.send(e)

      
      imgur_client= aioimgur.ImgurClient(os.environ["imgur_id"], os.environ["imgur_secret"])

      imgur_url = await imgur_client.upload(await a.read())
      await ctx.send(f"{imgur_url['link']}")

  @commands.command(brief="A command to remove testers")
  async def remove_tester(self, ctx, *, user: utils.BetterUserconverter = None):
    if user is None:
      await ctx.send("You can't have a non existent user.")

    if user:
      
      await self.bot.db.execute("DELETE FROM testers_list WHERE user_id = ($1)", user.id)
      
      if not user.id in self.bot.testers: 
        return await ctx.send(f"{user} isn't in the testers list.")

      else:
        self.bot.testers.remove(user.id)
        await ctx.send(f"Removed tester known as {user}")

  @commands.command(brief="A command to add testers")
  async def add_tester(self, ctx, *, user: utils.BetterUserconverter = None):
    if user is None:
      await ctx.send("You can't have a non existent user.")

    if user:
      await self.bot.db.execute("INSERT INTO testers_list VALUES ($1)", user.id)
      
      if not user.id in self.bot.testers: 
        self.bot.testers.append(user.id)
        await ctx.send(f"added tester known as {user}")

      else:
        return await ctx.send(f"{user} is in the testers list already!")

  def tweepy_post(self, post_text = None):

    consumer_key = os.getenv('tweet_key')
    consumer_secret = os.getenv('tweet_secret')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    access_token = os.getenv('tweet_access')
    access_secret = os.getenv('tweet_token')

    auth.set_access_token(access_token, access_secret)

    twitter_api = tweepy.API(auth)

    return twitter_api.update_status(status = post_text)

  @commands.command(brief = "sends tweet to JDBot Twitter")
  async def send_tweet(self, ctx, *, args = None):
    
    if not args:
      return await ctx.send("you can't send nothing to twitter.")

    try:
      tweet_time = functools.partial(self.tweepy_post, args)
      post = await self.bot.loop.run_in_executor(None, tweet_time)
      
    except Exception as e:
      traceback.print_exc()
      return await ctx.send(f"Exception occured at {e}")

    await ctx.send(f"Url of sent tweet is: https://twitter.com/twitter/statuses/{post.id}")

  @commands.command(brief = "chunks a guild for the purpose of testing purpose(it's owner only to be used in testing guilds only)")
  async def chunk_guild(self, ctx):
    if ctx.guild is None:
      return await ctx.send("You can't chunk a guild that doesn't exist or a channel that is a DM.")

    if ctx.guild.chunked:
      return await ctx.send("No need to chunk this guild, it appears to be chunked")

    await ctx.guild.chunk(cache = True)

    await ctx.send("Finished chunking..")

  @chunk_guild.error
  async def chunk_guild_error(self, ctx, error):
    await ctx.send(error)
    traceback.print_exc()

  
  @commands.command(brief = "displays the guild status and user status immediately")
  async def stats_status(self, ctx):
    await ctx.send("changing status, check now....")
    
    await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} servers | {len(self.bot.users)} users"))


  @stats_status.error
  async def stats_status_error(self, ctx, error):
    await ctx.send(error) 

  @commands.command(brief="a command to give a list of servers(owner only)",help="Gives a list of guilds(Bot Owners only) but with join dates updated.")
  async def servers2(self, ctx):

    sorted_guilds = sorted(self.bot.guilds, key=lambda guild: guild.me.joined_at)

    pag = commands.Paginator()
    for g in sorted_guilds:
      pag.add_line(f"{discord.utils.format_dt(g.me.joined_at, style = 'd')} {discord.utils.format_dt(g.me.joined_at, style = 'T')} \n[{len(g.members)}/{g.member_count}] **{g.name}** (`{g.id}`) | {(g.system_channel or g.text_channels[0]).mention}\n")

    pages = [page.strip("`") for page in pag.pages]
    menu = ViewMenuPages(utils.ServersEmbed(pages, per_page=1),delete_message_after=True)

    if (ctx.author.dm_channel is None):
      await ctx.author.create_dm()

    await menu.start(ctx, channel = ctx.author.dm_channel)

  @commands.command(brief = "changes money of people(for moderation of economy)")
  async def money(self, ctx, user : typing.Optional[discord.User] = None, *, number : typing.Optional[int] = None):

    user = user or ctx.author  
    number = number or 100

    await self.bot.db.execute("UPDATE economy SET wallet = ($1) WHERE user_id = ($2)", number, user.id)

    await ctx.send(f"{user} succesfully now has ${number} in wallet.")

  @commands.command(brief = "does say but more powerful with the optional option of a channel to say in but doesn't say who used the command(which is why it's owner only)")
  async def say3(self, ctx, channel : typing.Optional[typing.Union[discord.TextChannel, discord.Thread, discord.User]] = None, *, args = None):

    channel = channel or ctx.channel

    if isinstance(channel, discord.User):
      if (channel.dm_channel is None):
        await channel.create_dm()

      channel = channel.dm_channel

    args = args or "You didn't give us any text to use."
    args = discord.utils.escape_markdown(args, as_needed = False,ignore_links = False)
    
    bot_member = channel.me if isinstance(channel, discord.DMChannel) else channel.guild.me
      
    if channel.permissions_for(bot_member).send_messages or not channel.id == ctx.channel.id:

      if isinstance(bot_member, discord.Member):

        author_member = await bot_member.guild.try_member(ctx.author.id)

        channel = channel if author_member else ctx.channel

      try:
        await channel.send(f"{args}", allowed_mentions = discord.AllowedMentions.none())

      except Exception as e:
        await ctx.send(f"Failed :( with reason {e}")

      await ctx.send("sent message boss :D")

    else:
      await ctx.send("doesn't have permissions to send in that channel.")

  @commands.command(brief = "suspends the bot so the bot is only usable by the owner")
  async def suspend(self, ctx):

    self.bot.suspended = True
    await ctx.send("Locked all commands to only owners of the bot.")

  @commands.command(brief = "unsuspends the bot, so the bot is running normally")
  async def unsuspend(self, ctx):
    
    self.bot.suspended = False
    await ctx.send("Unlock commands, so operation is running like normal.")

def setup(bot):
  bot.add_cog(Owner(bot))
