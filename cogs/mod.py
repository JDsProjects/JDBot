import random
import re
import typing

import discord
from better_profanity import profanity
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import utils


class Moderation(commands.Cog):
    "Commands For Moderators to use"

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 90, BucketType.user)
    @commands.command(brief="a command to warn people, but if you aren't admin it doesn't penalize.")
    async def warn(self, ctx, *, member: utils.SuperConverter = commands.Author):
        warn_useable = utils.warn_permission(ctx, member)
        # modal for a reason(basically the same button as well above)
        # soon

        if warn_useable:
            embed = discord.Embed(color=random.randint(0, 16777215))
            embed.set_author(name=f"You have been warned by {ctx.author}", icon_url=("https://i.imgur.com/vkleJ9a.png"))
            embed.set_image(url="https://i.imgur.com/jDLcaYc.gif")
            embed.set_footer(text=f"ID: {ctx.author.id}")

            try:
                await member.send(embed=embed)

            except discord.Forbidden:
                await ctx.send("they don't seem like a valid user or they weren't DMable.")

            embed.set_footer(
                text=f"ID: {ctx.author.id}\nWarned by {ctx.author}\nWarned ID: {member.id} \nWarned: {member}"
            )
            await self.bot.support_webhook.send(embed=embed)

            try:
                await ctx.author.send(content=f"Why did you warn {member}?")

            except discord.Forbidden:
                await ctx.send("we can't DM them :(")

        elif warn_useable is False:
            await ctx.send(
                f"{ctx.author.mention}, you don't have permission to use that. You need to have manage_messages, have a higher hieracy in a guild, and have higher permissions than the target to use that.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @commands.cooldown(1, 90, BucketType.user)
    @commands.command(
        help="a command to scan for malicious bots, specificially ones that only give you random invites and are fake"
    )
    async def scan_guild(self, ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))
            count = 0

            # some code here to do a list compreshion to see if they are cached using get_user, those who return as None will be passed to query_members

            ids = [u for u in list(sus_users.keys()) if not ctx.guild.get_member(u)]

            await ctx.guild.query_members(limit=100, cache=True, user_ids=ids)

            pag = commands.Paginator(prefix="", suffix="")

            for x in sus_users:
                user = ctx.guild.get_member(x)
                if user:
                    count += 1
                    pag.add_line(f"Found {x}. \nUsername: {user} \nReason: {sus_users[x]}")

            if count < 1:
                await ctx.send("No Bad users found.")

            else:
                menu = utils.ScanGuildEmbed(pag.pages, ctx=ctx, delete_after=True)
                await menu.send()

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("please use the global version")

    @commands.cooldown(1, 90, BucketType.user)
    @commands.command(brief="scan globally per guild")
    async def scan_global(self, ctx):
        sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))

        ss_users = [self.bot.get_user(u) for u in sus_users if not None]

        ss_users = list(filter(lambda user: user is not None, ss_users))

        if not (ss_users):
            await ctx.send("no sus users found")

        else:
            mutual_guild_users = [u for u in ss_users if u.mutual_guilds]

            valid_users = [u for u in mutual_guild_users if utils.mutual_guild_check(ctx, u)]

            menu = utils.ScanGlobalEmbed(valid_users, ctx=ctx, delete_after=True)

            await menu.send()

    @commands.command(brief="gives stats about the sus users")
    async def ss_stats(self, ctx):
        sus_users = dict(await self.bot.db.fetch("SELECT * FROM SUS_USERS;"))
        await ctx.send(content=f"Total sus user count: {len(sus_users)}")

    @commands.command(brief="gives you info if someone is a sus user or etc")
    async def is_sus(self, ctx, *, user: typing.Optional[discord.User] = commands.Author):
        result = await self.bot.db.fetchrow("SELECT * FROM SUS_USERS WHERE user_id = ($1);", user.id)

        if not result:
            await ctx.send(f"{user} is not in the sus list.")

        else:
            reason = tuple(result)[1]
            await ctx.send(f"{user} for {reason}")

    @commands.command(
        help="a way to report a user, who might appear in the sus list. also please provide ids and reasons"
    )
    async def report(self, ctx, *, user: utils.SuperConverter = None):
        if not user:
            await ctx.send("Please Pick a user to report like this.")
            return await ctx.send_help(ctx.command)

        modal = utils.ReportView(ctx, timeout=180.0)
        message = await ctx.send(
            "Please Submit your Reason Here(if you don't respond with in 3 minutes, it will not work):", view=modal
        )
        await modal.wait()

        if modal.value:
            embed = discord.Embed(color=random.randint(0, 16777215))
            embed.set_author(name=f"Report by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="Details:", value=modal.value)
            embed.add_field(name="User Reported:", value=f"{user}")
            embed.set_footer(text=f"Reporter's ID is {ctx.author.id}")
            await self.bot.support_webhook.send("<@168422909482762240> Report", embed=embed)
            await message.edit(content="report sent to JDJG", embed=embed)

        if modal.value is None:
            await message.edit(content="You didn't give enough information to use.")

    @commands.command(brief="cleat amount/purge messages above to 100 msgs each", aliases=["purge"])
    async def clear(self, ctx, *, amount: typing.Optional[int] = None):
        if not amount:
            return await ctx.send("you didn't give an amount to use to clear.")

        if not utils.clear_permission(ctx):
            return await ctx.send("you can't use that(you don't have manage messages).")

        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send("Bot can't use that it doesn't have manage messages :(")

        amount += 1

        if amount > 100:
            await ctx.send("too high setting to 100")
            amount = 101

        try:
            messages = await ctx.channel.purge(limit=amount)
            await ctx.send(f"I deleted {len(messages)} messages, plus the {amount} messages you wanted me to delete.")
        except Exception as e:
            await ctx.send(f"An Error occured with {e}")

    @commands.command(brief="Unarchives thread channel")
    async def unlock_thread(self, ctx, channel: typing.Optional[discord.Thread] = commands.CurrentChannel):
        if isinstance(channel, discord.Thread):
            if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
                await ctx.send("Now unarchiving thread")

                thread = await channel.edit(archived=False)
                await ctx.send(f"Succesfully made {thread} unarchived again")

            if not ctx.me.guild_permissions.manage_threads:
                await ctx.send("can't unarchive channel because the bot doesn't have permissions to do so.")

            if not ctx.author.guild_permissions.manage_threads:
                await ctx.send("you don't have permission to edit to the thread channel.")

        else:
            await ctx.send(
                "You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread."
            )

    @commands.command(brief="Archives thread channel")
    async def archive_thread(self, ctx, channel: typing.Optional[discord.Thread] = commands.CurrentChannel):
        if isinstance(channel, discord.Thread):
            if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
                await ctx.send("Now archiving thread")

                thread = await channel.edit(archived=True)
                await ctx.send(f"Succesfully made {thread} archived again")

            if not ctx.me.guild_permissions.manage_threads:
                await ctx.send("can't archive channel because the  bot doesn't have permissions to do so.")

            if not ctx.author.guild_permissions.manage_threads:
                await ctx.send("you don't have permission to edit to the thread channel.")

        else:
            await ctx.send(
                "You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread."
            )

    @commands.command(brief="locks the thread channel")
    async def lock_thread(self, ctx, channel: typing.Optional[discord.Thread] = commands.CurrentChannel):
        if isinstance(channel, discord.Thread):
            if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
                await ctx.send("Now locking thread")

                thread = await channel.edit(locked=True)
                await ctx.send(f"Succesfully made {thread} locked.")

            if not ctx.me.guild_permissions.manage_threads:
                await ctx.send("can't lock channel because the bot doesn't have permissions to do so.")

            if not ctx.author.guild_permissions.manage_threads:
                await ctx.send("you don't have permission to edit to the thread channel.")

        else:
            await ctx.send(
                "You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread."
            )

    @commands.command(brief="unlocks the thread channel")
    async def unlock_thread(self, ctx, channel: typing.Optional[discord.Thread] = commands.CurrentChannel):
        if isinstance(channel, discord.Thread):
            if ctx.me.guild_permissions.manage_threads and ctx.author.guild_permissions.manage_threads:
                await ctx.send("Now unlocking thread")

                thread = await channel.edit(locked=False)
                await ctx.send(f"Succesfully made {thread} unlocked.")

            if not ctx.me.guild_permissions.manage_threads:
                await ctx.send("can't unlock channel because the bot doesn't have permissions to do so.")

            if not ctx.author.guild_permissions.manage_threads:
                await ctx.send("you don't have permission to edit to the thread channel.")

        else:
            await ctx.send(
                "You can only do that in thread channels, if you did try it on a thread channel, send a command in the thread channel so the bot caches the thread."
            )

    @commands.command(brief="scans statuses/activities to see if there is any bad ones.")
    @commands.has_permissions(manage_messages=True)
    async def scan_status(self, ctx):
        def scan(word):
            if profanity.contains_profanity(word):
                return {"type": "Profanity"}
            regex = re.compile(r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")
            if regex.search(word):
                return {"type": "Server Invite"}

            regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-\_@\.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
            if regex.search(word):
                return {"type": "External Link"}
            else:
                return None

        pages = []
        i = 0
        fi = 1
        count = [mem.activity for mem in ctx.guild.members if mem.activity is not None]
        count = len([scan(act.name) for act in count if scan(act.name) is not None])
        chunck = "**Total Members With A Bad Status: {}**\n\n".format(count)
        for member in ctx.guild.members:
            act = member.activity
            if act is not None:
                sc = scan(act.name)
                if sc is not None:
                    chunck += f"{fi}) **{member}** ({member.mention}) - **Reason**: {sc['type']}\n"
                    if i == 10:
                        pages.append(chunck)
                        chunck = "**Total Members With A Bad Status: {}**\n\n".format(count)
                        i = 0
                    i += 1
                    fi += 1

        pages.append(chunck)

        menu = utils.ScanStatusEmbed(pages, ctx=ctx, delete_after=True)
        await menu.send()


async def setup(bot):
    await bot.add_cog(Moderation(bot))
