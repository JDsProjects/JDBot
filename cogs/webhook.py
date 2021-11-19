from discord.ext import commands
import discord, re, random, aiohttp

class Webhook(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="a way to send stuff to webhooks.",help = "this uses webhook urls, and sends stuff to them")
  async def webhook(self, ctx, *, args=None):
    if args is None:
      await ctx.send("You didn't send anything")

    if args:
      check=re.match(r"https://discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,21})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})",args)
      
      if check:
        args = args.replace(f"{check.group()} ","")
        if args == check.group():
          args = "No Content"

          session = self.bot.session
          response=await session.get(check.group())
          if response.status == 200:
            webhook=discord.Webhook.from_url(check.group(), session=session)
            
            embed = discord.Embed(title=f"Webhook {webhook.name}'s Message", color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value=args
            )
            await webhook.send(embed=embed)

            await ctx.send(f"Message was sent to the desired webhook channel.")


          if response.status != 200:
            await ctx.send("Not a valid link or an error occured")

        if isinstance(ctx.channel, discord.TextChannel):
          try:
            await ctx.message.delete()
          except:
            await ctx.send("deleting the webhook failed, delete asap")

      if not check:
        await ctx.send("not a proper webhook url.")

  @commands.command(brief="a way to create webhooks",help="make commands with this.")
  async def webhook_create(self, ctx, arg = None, *, args = None):
    if isinstance(ctx.channel, discord.TextChannel):
      if ctx.author.guild_permissions.manage_webhooks:
        if arg:
          if args is None:
            try:
              webhook=await ctx.channel.create_webhook(name = arg)
            except Exception as e:
              return await ctx.send(f"give the bot manage webhook permissions for this to work and give the error to {e} if an issue.")
            embed = discord.Embed(title=f"{ctx.author}'s message:",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value="Test")
          if args:
            try:
              webhook = await ctx.channel.create_webhook(name=arg,reason=args)

            except Exception as e:
              return await ctx.send(f"give the bot manage webhook permissions for this to work and give the error to {e} if an issue.")

            embed = discord.Embed(title=f"{ctx.author}'s message:",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value=args)

          if ctx.message.attachments:
            image=await ctx.message.attachments[0].read()
            pass_test = True
            try:
              discord.utils._get_mime_type_for_image(image)
            except discord.errors.InvalidArgument:
              pass_test = False
            
            if pass_test:
              await webhook.edit(avatar=image)
            if pass_test is False:
              await ctx.send("not a valid image")
          
          await webhook.send(embed=embed)
          
          if (ctx.author.dm_channel is None):
            await ctx.author.create_dm()

          try:
            await ctx.author.send("Webhook url coming up")
            await ctx.author.send(webhook.url)
          except discord.Forbidden:
            await ctx.send(f"We couldn't DM you {ctx.author.mention}")
            
        if arg is None:
          await ctx.send("You need to use values for it to work")
      if ctx.author.guild_permissions.manage_webhooks is False:
        await ctx.send("you can't use that.")
        

    if isinstance(ctx.channel, discord.DMChannel):
      await ctx.send("You can't use that silly")

  @webhook_create.error
  async def webhook_create_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief = "tells you a webhook's avatar.")
  async def webhook_avatar(self, ctx, *, args = None):
    if not args:
      return await ctx.send("You didn't give me an arguments to go over.")

    check = re.match(r"https://discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,21})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})",args)
    if check:
      args = args.replace(f"{check.group()} ","")
      if args == check.group():

        session = self.bot.session
        response=await session.get(check.group())
        if not response.status != 200:
          webhook=discord.Webhook.from_url(check.group(), session=session)

          embed = discord.Embed(title = f"{webhook.name}"'s avatar:', color = random.randint(0, 16777215), timestamp = ctx.message.created_at)
          embed.set_image(url = webhook.avatar.url)

          await ctx.send(content = "Got the Webhook's avatar url",embed = embed)

        if response.status != 200:
          await ctx.send("Not a valid link or an error occured")

      if isinstance(ctx.channel, discord.TextChannel):
          try:
            await ctx.message.delete()
          except:
            await ctx.send("deleting the webhook failed, delete asap")

  @webhook_avatar.error
  async def webhook_avatar_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief = "deletes a webhook by url")
  async def webhook_delete(self, ctx, *, args = None):
    if not args:
      return await ctx.send("You didn't give me an arguments to go over.")

    check = re.match(r"https://discord(?:app)?.com/api/webhooks/(?P<id>[0-9]{17,21})/(?P<token>[A-Za-z0-9\.\-\_]{60,68})",args)
    if check:
      args = args.replace(f"{check.group()} ","")
      if args == check.group():

        session = self.bot.session
        response=await session.get(check.group())
        if not response.status != 200:
          webhook = discord.Webhook.from_url(check.group(), session = session)

          info = await response.json()

          if not info.get("guild_id") or not info.get("channel_id"):
            return await ctx.send(f"can't grab permissions from a {None} Guild or {None} Channel \nGuild ID: {webhook.guild_id}\nChannel ID: {webhook.channel_id}")
          

          channel = self.bot.get_channel(int(info.get("channel_id")))
          guild = self.bot.get_guild(int(info.get("guild_id")))

          if not guild or not channel:
            return await ctx.send("I can't check permissions of a guild that is none.")

          member = await guild.try_member(ctx.author.id)

          if member is None:
            return await ctx.send("You don't exist in the guild that you used the webhook of.")

          if channel.permissions_for(member).manage_webhooks:
            
            try:
              await webhook.delete()
              await ctx.send(f"succeeded in deleting webhook in {guild} in {channel.mention}!")

            except Exception as e:
              await ctx.send(f"An error occured with reason:\n{e}")

        if response.status != 200:
          await ctx.send("Not a valid link or an error occured")

      if isinstance(ctx.channel, discord.TextChannel):
          try:
            await ctx.message.delete()
          except:
            await ctx.send("deleting the webhook failed, delete asap unless it told you the link was deleted")
    
  @webhook_delete.error
  async def webhook_delete_error(self, ctx, error):
    await ctx.send(error)

def setup(bot):
  bot.add_cog(Webhook(bot))