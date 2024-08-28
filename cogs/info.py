import contextlib
import random
import re
import typing
import unicodedata

from difflib import SequenceMatcher, get_close_matches

import discord
import emoji
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import utils


class Info(commands.Cog):
    """Provides information about data you are allowed to access"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Gives you info about a guild",
        aliases=["server_info", "guild_fetch", "guild_info", "fetch_guild", "guildinfo"],
    )
    async def serverinfo(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
        guild = guild or ctx.guild
        if not guild:
            return await ctx.send("Could not find the guild you were looking for.")

        embed = discord.Embed(title=str(guild), color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

        view = utils.GuildInfoView(ctx, guild)
        await ctx.send("Get More Information for the guild you selected", embed=embed, view=view)

    @commands.command(
        aliases=["user_info", "user-info", "ui", "whois"],
        brief="A command that gives information on users",
        help="This can work with mentions, ids, usernames, and even full names.",
    )
    async def userinfo(self, ctx, *, user: utils.SuperConverter = commands.Author):
        embed = discord.Embed(title=str(user), color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.set_image(url=user.display_avatar.url)

        view = utils.UserInfoSuper(ctx, user)
        await ctx.send("Please Note this is being upgraded to a cooler version(it is a bit broken right now)")
        await ctx.send(
            "Pick a way for Mutual Guilds to be sent to you or not if you really don't the mutualguilds",
            embed=embed,
            view=view,
        )

    @app_commands.command(description="Get info about a user", name="userinfo")
    async def userinfo_slash(
        self, interaction: discord.Interaction, user: typing.Optional[typing.Union[discord.Member, discord.User]] = None
    ):
        user = user or interaction.user
        if isinstance(user, discord.Member):
            user = await self.bot.try_member(user.guild, user.id)

        ctx = await self.bot.get_context(interaction)
        embed = discord.Embed(title=str(user), color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.set_image(url=user.display_avatar.url)

        view = utils.UserInfoSuper(ctx, user)
        await ctx.send(
            "Pick a way for Mutual Guilds to be sent to you or not if you really don't the mutualguilds",
            embed=embed,
            view=view,
        )

    @commands.command(brief="Uploads your emojis into a Senarc Bin link")
    async def look_at(self, ctx):
        if isinstance(ctx.message.channel, discord.TextChannel):
            message_emojis = " ".join(f"{x}\n" for x in ctx.guild.emojis)
            paste = await utils.post(self.bot, message_emojis)
            await ctx.send(paste)
        elif isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("We can't use that in DMS as it takes emoji regex and puts it into a paste.")

    @commands.command(help="Gives the id of the current guild or DM if you are in one.")
    async def guild_get(self, ctx):
        await ctx.send(ctx.guild.id if isinstance(ctx.channel, discord.TextChannel) else ctx.channel.id)

    @commands.command(brief="A command to tell you the channel id", aliases=["GetChannelId"])
    async def this(self, ctx):
        await ctx.send(ctx.channel.id)

    @commands.command(brief="Gives you mention info don't abuse(doesn't mention tho)")
    async def mention(self, ctx, *, user: utils.SuperConverter = commands.Author):
        await ctx.send(
            f"Discord Mention: {user.mention} \nRaw Mention: {discord.utils.escape_mentions(user.mention)}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(help="Fetch invite details")
    async def fetch_invite(self, ctx, *invites: typing.Union[discord.Invite, str]):
        if not invites:
            await ctx.send("Please get actual invites to attempt grab")
            ctx.command.reset_cooldown(ctx)
            return

        menu = utils.InviteInfoEmbed(invites, ctx=ctx, delete_after=True)
        await menu.send()

        if len(invites) > 50:
            await ctx.send(
                "Reporting using more than 50 invites in this command. This is to prevent ratelimits with the api."
            )
            jdjg = await self.bot.try_user(168422909482762240)
            await self.bot.support_webhook.send(
                f"{jdjg.mention}.\n{ctx.author} causes a ratelimit issue with {len(invites)} invites"
            )

    @commands.command(brief="Gives info about a file")
    async def file(self, ctx):
        if not ctx.message.attachments:
            await ctx.send("No file submitted")
            return

        embed = discord.Embed(title="Attachment info", color=random.randint(0, 16777215))
        for a in ctx.message.attachments:
            embed.add_field(name=f"ID: {a.id}", value=f"[{a.filename}]({a.url})")
        embed.set_footer(text="Check on the url/urls to get a direct download to the url.")
        await ctx.send(embed=embed, content="That's good")

    @commands.command(
        brief="A command to get the avatar of a user",
        help="Using the userinfo technology it now powers avatar grabbing.",
        aliases=["pfp", "av"],
    )
    async def avatar(self, ctx, *, user: utils.SuperConverter = commands.Author):
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{user.name}'s avatar:", icon_url=user.display_avatar.url)
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(brief="This is a way to get the nearest channel.")
    async def find_channel(self, ctx, *, args=None):
        if not args:
            return await ctx.send("Please specify a channel")

        if isinstance(ctx.channel, discord.TextChannel):
            channel = discord.utils.get(ctx.guild.channels, name=args)
            if channel:
                await ctx.send(channel.mention)
            else:
                await ctx.send("Unfortunately we haven't found anything")
        elif isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You can't use it in a DM.")

    @commands.command(brief="A command to get the closest user.")
    async def closest_user(self, ctx, *, args=None):
        if not args:
            return await ctx.send("Please specify a user")

        if not self.bot.users:
            return await ctx.send("There are no users cached :(")

        userNearest = discord.utils.get(self.bot.users, name=args)
        user_nick = discord.utils.get(self.bot.users, display_name=args)

        if userNearest is None:
            userNearest = max(self.bot.users, key=lambda x: SequenceMatcher(None, x.name, args).ratio())

        if user_nick is None:
            user_nick = max(self.bot.users, key=lambda x: SequenceMatcher(None, x.display_name, args).ratio())

        if isinstance(ctx.channel, discord.TextChannel):
            member_list = [x for x in ctx.guild.members if x.nick]
            nearest_server_nick = max(member_list, key=lambda x: SequenceMatcher(None, x.nick, args).ratio())
        else:
            nearest_server_nick = "You unfortunately don't get the last value(a nickname) as it's a DM."

        await ctx.send(f"Username: {userNearest} \nDisplay name: {user_nick} \nNickname: {nearest_server_nick}")

    @commands.command(help="Gives info on default emoji and custom emojis", name="emoji")
    async def emoji_info(
        self,
        ctx: commands.Context,
        *,
        emojis: typing.Annotated[utils.EmojiConverter.ConvertedEmojis, utils.EmojiConverter],
    ):
        menu = utils.EmojiInfoEmbed(emojis.all, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="Gives info on emoji_id and emoji image.")
    async def emoji_id(
        self,
        ctx,
        *,
        emoji: typing.Optional[typing.Union[discord.PartialEmoji, discord.Message, utils.EmojiBasic]] = None,
    ):
        if isinstance(emoji, discord.Message):
            emoji_message = emoji.content
            emoji = None

            with contextlib.suppress(commands.CommandError, commands.BadArgument):
                emoji = await utils.EmojiBasic.convert(
                    ctx, emoji_message
                ) or await commands.PartialEmojiConverter().convert(ctx, emoji_message)

        if emoji:
            embed = discord.Embed(description=f"Emoji ID: {emoji.id}", color=random.randint(0, 16777215))
            embed.set_image(url=emoji.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Not a valid emoji id.")

    @commands.command()
    async def fetch_content(self, ctx, *, args=None):
        if not args:
            return await ctx.send("Please send actual text")

        args = discord.utils.escape_mentions(args)
        args = discord.utils.escape_markdown(args, as_needed=False, ignore_links=False)

        for x in ctx.message.mentions:
            args = args.replace(x.mention, f"\\{x.mention}")

        emojis = emoji.emoji_lis(args)
        emojis_return = [d["emoji"] for d in emojis]

        for x in emojis_return:
            args = args.replace(x, f"\\{x}")

        for x in re.findall(r":\w*:\d*", args):
            args = args.replace(x, f"\\{x}")

        await ctx.send(args, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(brief="Gives info about a role.", aliases=["roleinfo"])
    async def role_info(self, ctx, *, role: typing.Optional[discord.Role] = None):
        if role:
            await utils.roleinfo(ctx, role)
        else:
            await ctx.send("The role you wanted was not found.")


async def setup(bot):
    await bot.add_cog(Info(bot))
