from discord.ext import commands, menus
import re, discord, random, mystbin, typing, emoji
import utils
from difflib import SequenceMatcher
from discord.ext.commands.cooldowns import BucketType


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        help="gives you info about a guild",
        aliases=[
            "server_info",
            "guild_fetch",
            "guild_info",
            "fetch_guild",
            "guildinfo",
        ],
    )
    async def serverinfo(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
        guild = guild or ctx.guild

        if guild is None:
            await ctx.send("Guild wanted has not been found")

        if guild:
            await utils.guildinfo(ctx, guild)

    @commands.command(
        aliases=["user info", "user_info", "user-info"],
        brief="a command that gives information on users",
        help="this can work with mentions, ids, usernames, and even full names.",
    )
    async def userinfo(self, ctx, *, user: utils.BetterUserconverter = None):
        user = user or ctx.author
        user_type = user_type = ["User", "Bot"][user.bot]

        if ctx.guild:
            member_version = ctx.guild.get_member(user.id)
            if member_version:
                nickname = str(member_version.nick)
                joined_guild = member_version.joined_at.strftime("%m/%d/%Y %H:%M:%S")
                status = str(member_version.status).upper()
                highest_role = member_version.roles[-1]
            if not member_version:
                nickname = str(member_version)
                joined_guild = "N/A"
                status = "Unknown"
                for guild in self.client.guilds:
                    member = guild.get_member(user.id)
                    if member:
                        status = str(member.status).upper()
                        break
                highest_role = "None Found"
        if not ctx.guild:
            nickname = "None"
            joined_guild = "N/A"
            status = "Unknown"
            for guild in self.client.guilds:
                member = guild.get_member(user.id)
                if member:
                    status = str(member.status).upper()
                    break
            highest_role = "None Found"

        guilds_list = [
            guild
            for guild in self.client.guilds
            if guild.get_member(user.id) and guild.get_member(ctx.author.id)
        ]
        if not guilds_list:
            guild_list = "None"

        x = 0
        for g in guilds_list:
            if x < 1:
                guild_list = g.name
            if x > 0:
                guild_list = guild_list + f", {g.name}"
            x = x + 1

        embed = discord.Embed(
            title=f"{user}",
            description=f"Type: {user_type}",
            color=random.randint(0, 16777215),
            timestamp=ctx.message.created_at,
        )
        embed.add_field(name="Username: ", value=user.name)
        embed.add_field(name="Discriminator:", value=user.discriminator)
        embed.add_field(name="Nickname: ", value=nickname)
        embed.add_field(
            name="Joined Discord: ",
            value=(user.created_at.strftime("%m/%d/%Y %H:%M:%S")),
        )
        embed.add_field(name="Joined Guild: ", value=joined_guild)
        embed.add_field(name="Mutual Guilds:", value=guild_list)
        embed.add_field(name="ID:", value=user.id)
        embed.add_field(name="Status:", value=status)
        embed.add_field(name="Highest Role:", value=highest_role)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief="uploads your emojis into a mystbin link")
    async def look_at(self, ctx):
        if isinstance(ctx.message.channel, discord.TextChannel):
            message_emojis = ""
            for x in ctx.guild.emojis:
                message_emojis = message_emojis + " " + str(x) + "\n"
            mystbin_client = mystbin.Client(session=self.client.session)
            paste = await mystbin_client.post(message_emojis)
            await ctx.send(paste.url)

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("We can't use that in DMS")

    @commands.command(help="gives the id of the current guild or DM if you are in one.")
    async def guild_get(self, ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=ctx.guild.id)

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(ctx.channel.id)

    @commands.command(brief="a command to tell you the channel id")
    async def this(self, ctx):
        await ctx.send(ctx.channel.id)

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(help="fetch invite details")
    async def fetch_invite(self, ctx, *invites: typing.Union[discord.Invite, str]):
        if len(invites) > 0:
            menu = menus.MenuPages(
                utils.InviteInfoEmbed(invites, per_page=1), delete_message_after=True
            )
            await menu.start(ctx)
        if len(invites) < 1:
            await ctx.send("Please get actual invites to attempt grab")

        if len(invites) > 50:
            await ctx.send(
                "Reporting using more than 50 invites in this command. This is to prevent ratelimits with the api."
            )

            jdjg = self.client.get_user(
                168422909482762240
            ) or await self.client.fetch_user(168422909482762240)
            await self.client.get_channel(738912143679946783).send(
                f"{jdjg.mention}.\n{ctx.author} causes a ratelimit issue with {len(invites)} invites"
            )

    @fetch_invite.error
    async def fetch_invite_error(self, ctx, error):
        await ctx.send(error)

    @commands.command(brief="gives info about a file")
    async def file(self, ctx):
        if len(ctx.message.attachments) < 1:
            await ctx.send(ctx.message.attachments)
            await ctx.send("no file submitted")
        if len(ctx.message.attachments) > 0:
            embed = discord.Embed(
                title="Attachment info", color=random.randint(0, 16777215)
            )
            for x in ctx.message.attachments:
                embed.add_field(name=f"ID: {x.id}", value=f"[{x.filename}]({x.url})")
                embed.set_footer(
                    text="Check on the url/urls to get a direct download to the url."
                )
            await ctx.send(embed=embed, content="\nThat's good")

    @commands.command(
        brief="a command to get the avatar of a user",
        help="using the userinfo technology it now powers avatar grabbing.",
        aliases=["pfp", "av"],
    )
    async def avatar(self, ctx, *, user: utils.BetterUserconverter = None):
        user = user or ctx.author
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{user.name}'s avatar:", icon_url=(user.avatar_url))
        embed.set_image(url=(user.avatar_url))
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(brief="this is a way to get the nearest channel.")
    async def closest_channel(self, ctx, *, args=None):
        if args is None:
            await ctx.send("Please specify a channel")

        if args:
            if isinstance(ctx.channel, discord.TextChannel):
                channel = discord.utils.get(ctx.guild.channels, name=args)
                if channel:
                    await ctx.send(channel.mention)
                if channel is None:
                    await ctx.send("Unforantely we haven't found anything")

            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("You can't use it in a DM.")

    @commands.command(brief="a command to get the closest user.")
    async def closest_user(self, ctx, *, args=None):
        if args is None:
            await ctx.send("please specify a user")
        if args:
            userNearest = discord.utils.get(self.client.users, name=args)
            user_nick = discord.utils.get(self.client.users, display_name=args)
            if userNearest is None:
                userNearest = sorted(
                    self.client.users,
                    key=lambda x: SequenceMatcher(None, x.name, args).ratio(),
                )[-1]
            if user_nick is None:
                user_nick = sorted(
                    self.client.users,
                    key=lambda x: SequenceMatcher(None, x.display_name, args).ratio(),
                )[-1]
            await ctx.send(f"Username: {userNearest}")
            await ctx.send(f"Display name: {user_nick}")

        if isinstance(ctx.channel, discord.TextChannel):
            member_list = []
            for x in ctx.guild.members:
                if x.nick is None:
                    pass
                if x.nick:
                    member_list.append(x)

            nearest_server_nick = sorted(
                member_list, key=lambda x: SequenceMatcher(None, x.nick, args).ratio()
            )[-1]
            await ctx.send(f"Nickname: {nearest_server_nick}")

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You unforantely don't get the last value.")

    @commands.command(
        help="gives info on default emoji and custom emojis", name="emoji"
    )
    async def emoji_info(self, ctx, *emojis: typing.Union[utils.EmojiConverter, str]):
        if len(emojis) > 0:
            menu = menus.MenuPages(
                utils.EmojiInfoEmbed(emojis, per_page=1), delete_message_after=True
            )
            await menu.start(ctx)
        if len(emojis) < 1:
            await ctx.send("Looks like there was no emojis.")

    @commands.command()
    async def fetch_content(self, ctx, *, args=None):
        if args is None:
            await ctx.send("please send actual text")
        if args:
            args = discord.utils.escape_mentions(args)
            args = discord.utils.escape_markdown(
                args, as_needed=False, ignore_links=False
            )
        for x in ctx.message.mentions:
            args = args.replace(x.mention, f"\{x.mention}")
        emojis = emoji.emoji_lis(args)
        emojis_return = [d["emoji"] for d in emojis]
        for x in emojis_return:
            args = args.replace(x, f"\{x}")
        for x in re.findall(r":\w*:\d*", args):
            args = args.replace(x, f"\{x}")
        await ctx.send(f"{args}")


def setup(client):
    client.add_cog(Info(client))
