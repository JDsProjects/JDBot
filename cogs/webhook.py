from discord.ext import commands
import discord, re, random, aiohttp

class Webhook(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="a way to send stuff to webhooks.",help="this uses webhook urls, and sends stuff to them")
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
            webhook=discord.Webhook.from_url(check.group(), adapter=discord.AsyncWebhookAdapter(session))
            
            embed = discord.Embed(title=f"Webhook {webhook.name}'s Message",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value=args)
            await webhook.execute(embed=embed)

          if response.status != 200:
            await ctx.send("Not a valid link or an error occured")

        if isinstance(ctx.channel, discord.TextChannel):
          await ctx.message.delete()

      if not check:
        await ctx.send("not a proper webhook url.")

  @commands.command(brief="a way to create webhooks",help="make commands with this.")
  async def webhook_create(self, ctx, arg = None, *, args = None):
    if isinstance(ctx.channel, discord.TextChannel):
      if ctx.author.guild_permissions.manage_webhooks:
        if arg:
          if args is None:
            try:
              webhook=await ctx.channel.create_webhook(name=arg)
            except Exception as e:
              return await ctx.send(f"give the bot manage webhook permissions for this to work and give the error to {e} if an issue.")
            embed = discord.Embed(title=f"{ctx.author}'s message:",color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
            embed.add_field(name="Content:",value="Test")
          if args:
            try:
              webhook=await ctx.channel.create_webhook(name=arg,reason=args)

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
          
          await webhook.execute(embed=embed)
          
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

def setup(bot):
  bot.add_cog(Webhook(bot))