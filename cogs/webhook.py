from discord.ext import commands
import discord
import random
import utils


class Webhook(commands.Cog):
    "Commands dealing with webhooks"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="a way to send stuff to webhooks.", help="this uses webhook urls, and sends stuff to them")
    async def webhook(self, ctx, webhook: utils.WebhookConverter, *, content=None):
        content = content or "No Content"

        session = self.bot.session
        response = await session.get(webhook.group())

        if response.status != 200:
            return await ctx.send("Not a valid link or an error occured.")

        if response.status == 200:
            webhook = discord.Webhook.from_url(webhook.group(), session=session)

            embed = discord.Embed(
                title=f"Webhook {webhook.name}'s Message",
                color=random.randint(0, 16777215),
                timestamp=(ctx.message.created_at),
            )
            embed.add_field(name="Content:", value=content)
            await webhook.send(embed=embed)

            await ctx.send(f"Message was sent to the desired webhook channel.")

    @commands.command(brief="a way to create webhooks", help="make commands with this.")
    async def webhook_create(self, ctx, name: str = None, *, args=None):
        if ctx.guild:
            if ctx.author.guild_permissions.manage_webhooks:
                if not name:
                    return await ctx.send("Please input a webhook name.")

                try:
                    webhook = await ctx.channel.create_webhook(name=name)
                except Exception as e:
                    return await ctx.send(
                        f"give the bot manage webhook permissions for this to work and give the error to {e} if an issue."
                    )
                embed = discord.Embed(
                    title=f"{ctx.author}'s message:",
                    color=random.randint(0, 16777215),
                    timestamp=(ctx.message.created_at),
                )
                embed.add_field(name="Content:", value=args or "Test")

                if ctx.message.attachments:
                    await ctx.trigger_typing()

                    image = await ctx.message.attachments[0].read()
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

                if ctx.author.dm_channel is None:
                    await ctx.author.create_dm()

                try:
                    await ctx.author.send("Webhook url coming up")
                    await ctx.author.send(webhook.url)
                except discord.Forbidden:
                    await ctx.send(f"We couldn't DM you {ctx.author.mention}")

            else:
                return await ctx.send("You don't have sufficient permissions.")

        else:
            return await ctx.send("You cannot use this in DMs!")

    @commands.command(brief="tells you a webhook's avatar.")
    async def webhook_avatar(self, ctx, *, webhook: utils.WebhookConverter = None):
        if not webhook:
            return await ctx.send("Please pass in a webhook url.")

        webhook = webhook.group()
        session = self.bot.session
        response = await session.get(webhook)
        if not response.status != 200:
            webhook = discord.Webhook.from_url(webhook, session=session)

            embed = discord.Embed(
                title=f"{webhook.name}" "s avatar:",
                color=random.randint(0, 16777215),
                timestamp=ctx.message.created_at,
            )
            embed.set_image(url=webhook.avatar.url)

            await ctx.send(content="Got the Webhook's avatar url", embed=embed)

        if response.status != 200:
            await ctx.send("Not a valid link or an error occured")

        try:
            await ctx.message.delete()

        except Exception:
            print(Exception)

    @commands.command(brief="deletes a webhook by url")
    async def webhook_delete(self, ctx, *, webhook: utils.WebhookConverter = None):
        if not webhook:
            return await ctx.send("Please pass in a webhook url.")

        webhook = webhook.group()
        session = self.bot.session
        response = await session.get(webhook)
        if not response.status != 200:
            webhook = discord.Webhook.from_url(webhook, session=session)

            info = await response.json()

            guild_id = info.get("guild_id")
            channel_id = info.get("channel_id")

            if not info.get("guild_id") or not info.get("channel_id"):
                return await ctx.send(
                    f"can't grab permissions from a {None} Guild or {None} Channel \nGuild ID: {webhook.guild_id}\nChannel ID: {webhook.channel_id}"
                )

            channel = self.bot.get_channel(int(channel_id))
            guild = self.bot.get_guild(int(guild_id))

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
                    return await ctx.send(f"An error occured with reason:\n{e}")
            else:
                return await ctx.send("You do not have proper permissions to delete webhooks in that channel.")

        if response.status != 200:
            return await ctx.send("Not a valid link or an error occured")


def setup(bot):
    bot.add_cog(Webhook(bot))
