from __future__ import annotations

import asyncio
import collections
import random
import traceback
import typing

import discord
from discord.ext import commands
from discord.flags import UserFlags

from .paginators import MutualGuildsEmbed, grab_mutualguilds


class UserInfoButton(discord.ui.Button):
    def __init__(self, style, label: str, emoji, custom_id: str):
        super().__init__(style=style, label=label, emoji=emoji, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        guilds_list = grab_mutualguilds(self.view.ctx, self.view.user)

        pag = commands.Paginator(prefix="", suffix="")

        for g in guilds_list:
            pag.add_line(f"{g}")

        pages = pag.pages or ["None"]

        menu = MutualGuildsEmbed(pages, ctx=self.view.ctx, delete_after=True)

        for child in self.view.children:
            if isinstance(child, (discord.Button, discord.ui.Button)):
                self.view.remove_item(child)

        if self.custom_id == "0":
            await interaction.response.edit_message(
                content="Will be sending you the information, ephemerally", view=self.view
            )

            await menu.send(interaction=interaction, ephemeral=True)

        if self.custom_id == "1":
            await interaction.response.edit_message(
                content=f"Well be Dming you the paginator to view this info", view=self.view
            )

            await menu.send(send_to=self.view.ctx.author)

        if self.custom_id == "2":
            await interaction.response.edit_message(content=f"not sending the paginator to you", view=self.view)


def profile_converter(
    _type: typing.Literal["badges", "mobile", "status", "web", "desktop", "mobile", "activity"],
    _enum: typing.Union[
        discord.Status, discord.UserFlags, discord.Activity, discord.BaseActivity, discord.Spotify, str
    ],
):
    badges_emoji = {
        UserFlags.staff: "<:discord_staff:1040719569116999680>",
        UserFlags.partner: "<:discord_partner:1040723650162212985>",
        UserFlags.hypesquad: "<:hypesquad:1040720248158040154>",
        UserFlags.bug_hunter: "<:bug_hunter:1040719548128702544>",
        UserFlags.hypesquad_bravery: "<:bravery:917747437450457128>",
        UserFlags.hypesquad_brilliance: "<:brilliance:917747437509177384>",
        UserFlags.hypesquad_balance: "<:balance:917747437412704366>",
        UserFlags.early_supporter: "<:early_supporter:1040720490676895846>",
        UserFlags.team_user: "🤖",
        "system": "<:verifiedsystem1:848399959539843082><:verifiedsystem2:848399959241261088>",
        UserFlags.bug_hunter_level_2: "<:bug_hunter_2:1040721850520571914>",
        UserFlags.verified_bot: "<:verifiedbot1:848395737279496242><:verifiedbot2:848395736982749194>",
        UserFlags.verified_bot_developer: "<:early_developer:1040719588385624074>",
        UserFlags.discord_certified_moderator: "<:certified_moderator:1040719606102380687>",
        UserFlags.bot_http_interactions: "<:bot_http_interactions:1040746049821757522>",
        UserFlags.spammer: "⚠️",
        UserFlags.active_developer: "<:active_dev:1040717993895800853>",
        "bot": "<:bot:848395737138069514>",
    }

    status_emojis = {
        discord.Status.online: "<:online:917747437882458122>",
        discord.Status.dnd: "<:do_not_disturb:917747437756633088>",
        discord.Status.idle: "<:away:917747437479821332>",
        discord.Status.offline: "<:offline:917747437815349258>",
    }

    devices_emojis = {
        "mobile": {
            discord.Status.online: "<:mobile_online:917753163417813053>",
            discord.Status.dnd: "<:mobile_dnd:917753135672459276>",
            discord.Status.idle: "<:mobile_away:917753135672459275>",
            discord.Status.offline: "<:mobile_offline:917752338532425739>",
        },
        "desktop": {
            discord.Status.online: "<:desktop_online:917755694852235265>",
            discord.Status.dnd: "<:desktop_dnd:917755694839656448>",
            discord.Status.idle: "<:desktop_away:917755694902558790>",
            discord.Status.offline: "<:desktop_offline:917755694948708402> ",
        },
        "web": {
            discord.Status.online: "<:website_online:917753204396142623>",
            discord.Status.dnd: "<:website_dnd:917753204396142622>",
            discord.Status.idle: "<:website_away:917753204400336956> ",
            discord.Status.offline: "<:website_offline:917752338574348289>",
        },
    }

    activity_emojis = {
        discord.ActivityType.unknown: "❓",
        discord.ActivityType.playing: "🎮",
        discord.ActivityType.streaming: "<:streaming:917747437920219156>",
        discord.ActivityType.listening: "🎧",
        discord.ActivityType.watching: "📺",
        discord.Spotify: "<:spotify:1041484515748618343>",
        discord.ActivityType.competing: "🏃",
        discord.ActivityType.custom: "🎨",
    }

    dc = {"status": status_emojis, "badges": badges_emoji, "devices": devices_emojis, "activity": activity_emojis}
    is_devices = False
    if _type in ("mobile", "desktop", "web"):
        is_devices = True

    dict_to_use = dc.get(_type) if not is_devices else dc["devices"][_type]
    if _type == "activity":
        _enum = _enum.type if not isinstance(_enum, discord.Spotify) else _enum.__class__

    emoji = dict_to_use.get(_enum)
    if not emoji:
        raise ValueError(f"Could not find any emoji matching the input values:\n{_type=}\n{_enum=}")
    return emoji


def status_collect(user):
    statuses = []

    for name, status in (
        ("Status", user.status),
        ("Desktop", user.desktop_status),
        ("Mobile", user.mobile_status),
        ("Web", user.web_status),
    ):
        statuses.append((name, profile_converter(name.lower(), status)))

    return statuses


def badge_collect(user):
    badges = [profile_converter("badges", f) for f in user.public_flags.all()] if user.public_flags else []
    if user.bot:
        badges.append(profile_converter("badges", "bot"))

    if user.system:
        badges.append(profile_converter("badges", "system"))

    return badges


def activity_collect(user):
    activities = [profile_converter("activity", activity) for activity in user.activities] if user.activities else []
    return activities


class UserInfoSuperSelects(discord.ui.Select):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.banner = None
        self.banner_fetched = False

        options = [
            discord.SelectOption(label="Basic Info", description="Simple Info", value="basic", emoji="📝"),
            discord.SelectOption(
                label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"
            ),
            discord.SelectOption(label="Badges", description="Show's the badges they have", value="badges", emoji="📛"),
            discord.SelectOption(
                label="Avatar",
                description="Shows user's profile picture in large thumbnail.",
                emoji="🖼️",
                value="avatar",
            ),
            discord.SelectOption(label="Status", description="Shows user's current status.", emoji="🖼️", value="status"),
            discord.SelectOption(
                label="Activities", description="Shows user's current Activities.", emoji="🏃", value="activities"
            ),
            discord.SelectOption(
                label="Guild Info",
                description="Shows user's guild info",
                value="guildinfo",
                emoji="<:members:917747437429473321>",
            ),
            discord.SelectOption(
                label="Banner",
                description="Shows user banner",
                value="banner",
                emoji="🏳️",
            ),
            discord.SelectOption(
                label="Close",
                description="Closes the Select",
                value="close",
                emoji="❌",
            ),
        ]

        super().__init__(placeholder="What Info would you like to view?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        user = self.view.user

        embed = discord.Embed(title=f"{user}", color=random.randint(0, 16777215), timestamp=self.ctx.message.created_at)
        embed.set_image(url=user.display_avatar.url)

        statuses = []
        activities = []

        if isinstance(user, discord.Member):
            nickname = user.nick
            joined_guild = f"{discord.utils.format_dt(user.joined_at, style = 'd')}\n{discord.utils.format_dt(user.joined_at, style = 'T')}"
            highest_role = user.top_role

            statuses = status_collect(user)
            activities = activity_collect(user)

        else:
            nickname = "None Found"
            joined_guild = "N/A"
            highest_role = "None Found"

            member = discord.utils.find(lambda member: member.id == user.id, interaction.client.get_all_members())

            if member:
                statuses = status_collect(member)
                activities = activity_collect(member)

        join_statuses = (
            " \n| ".join(f"**{name}**: {value}" for name, value in statuses) if statuses else "**Status**: \nUnknown"
        )

        join_activities = (
            " \n| ".join(f"**{name}**" for name in activities) if activities else "**Activity**: \nUnknown"
        )

        if choice == "basic":
            embed.add_field(
                name="User Info: ",
                value=f"**Username**: {user.name} \n**Discriminator**: {user.discriminator} \n**ID**: {user.id}",
                inline=False,
            )

        if choice == "badges":
            badges = badge_collect(user)
            join_badges: str = "\u0020".join(badges) if badges else "N/A"

            embed.add_field(
                name="User Info 2:",
                value=f"Badges: {join_badges}",
                inline=False,
            )

        if choice == "misc":
            user_type = "Bot" if user.bot else "User" if isinstance(user, discord.User) else "Member"
            embed.add_field(
                name="User Info 2:",
                value=f"Type: {user_type} \n**Joined Discord**: \n{discord.utils.format_dt(user.created_at, style = 'd')}\n{discord.utils.format_dt(user.created_at, style = 'T')}",
                inline=False,
            )

        if choice == "avatar":
            embed = discord.Embed(color=random.randint(0, 16777215))
            embed.set_author(name=f"{user.name}'s avatar:", icon_url=user.display_avatar.url)
            embed.set_image(url=user.display_avatar.url)
            embed.set_footer(text=f"Requested by {self.ctx.author}")

        if choice == "status":
            embed.add_field(name=f"{join_statuses}", value="\u2800", inline=False)

        if choice == "activities":
            embed.add_field(name=f"{join_activities}", value="\u2800", inline=False)

        if choice == "guildinfo":
            embed.add_field(
                name="Guild Info:",
                value=f"**Joined Guild**: {joined_guild} \n**Nickname**: {nickname} \n**Highest Role:** {highest_role}",
                inline=False,
            )

        if choice == "banner":
            if self.banner is None and not self.banner_fetched:
                try:
                    user_banner = await interaction.client.fetch_user(user.id)

                except:
                    user_banner = user
                    traceback.print_exc()

                self.banner = user_banner.banner
                self.banner_fetched = True

            banner = self.banner
            if banner:
                embed.set_image(url=banner.url)

            else:
                embed.add_field(name="Banner:", value="No Banner Found", inline=False)

        if choice == "close":
            self.view.remove_item(self)
            return await interaction.response.edit_message(view=self.view, embed=None)

        await interaction.response.edit_message(embed=embed)


class UserInfoSuper(discord.ui.View):
    def __init__(self, ctx, user, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.user = user

        self.add_item(UserInfoButton(discord.ButtonStyle.success, "Ephemeral", "🕵️", custom_id="0"))
        self.add_item(UserInfoButton(label="Direct", style=discord.ButtonStyle.success, emoji="📥", custom_id="1"))
        self.add_item(UserInfoButton(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️", custom_id="2"))
        self.add_item((UserInfoSuperSelects(ctx)))

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


class OwnerSuperSelects(discord.ui.Select):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.banner = None
        self.banner_fetched = False

        options = [
            discord.SelectOption(label="Basic Info", description="Simple Info", value="basic", emoji="📝"),
            discord.SelectOption(
                label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"
            ),
            discord.SelectOption(label="Badges", description="Show's the badges they have", value="badges", emoji="📛"),
            discord.SelectOption(
                label="Avatar",
                description="Shows Owner's profile picture in large thumbnail.",
                emoji="🖼️",
                value="avatar",
            ),
            discord.SelectOption(
                label="Status", description="Shows Owner's current status.", emoji="🖼️", value="status"
            ),
            discord.SelectOption(
                label="Guild Info",
                description="Shows Owner's guild info",
                value="guildinfo",
                emoji="<:members:917747437429473321>",
            ),
            discord.SelectOption(
                label="Banner",
                description="Shows Owner banner",
                value="banner",
                emoji="🏳️",
            ),
            discord.SelectOption(
                label="Close",
                description="Closes the Select",
                value="close",
                emoji="❌",
            ),
        ]

        super().__init__(placeholder="What Info would you like to view?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        choice = self.values[0]

        user = self.view.user
        support_guild = self.view.support_guild
        statuses = []

        if isinstance(user, discord.Member):
            nickname = user.nick
            joined_guild = f"{discord.utils.format_dt(user.joined_at, style = 'd')}\n{discord.utils.format_dt(user.joined_at, style = 'T')}"
            highest_role = user.top_role

            statuses = status_collect(user)

        else:
            nickname = "None Found"
            joined_guild = "N/A"
            highest_role = "None Found"

            member = discord.utils.find(lambda member: member.id == user.id, interaction.client.get_all_members())
            if member:
                statuses = status_collect(member)

        join_statuses = (
            " \n| ".join(f"**{name}**: {value}" for name, value in statuses) if statuses else "**Status**: \nUnknown"
        )

        embed = discord.Embed(
            title=f"Bot Owner: {user}", color=random.randint(0, 16777215), timestamp=self.ctx.message.created_at
        )

        embed.set_image(url=user.display_avatar.url)

        if choice == "basic":
            embed.add_field(
                name="User Info: ",
                value=f"**Username**: {user.name} \n**Discriminator**: {user.discriminator} \n**ID**: {user.id}",
                inline=False,
            )

        if choice == "badges":
            badges = badge_collect(user)
            join_badges: str = "\u0020".join(badges) if badges else "N/A"

            embed.add_field(
                name="User Info 2:",
                value=f"Badges: {join_badges}",
                inline=False,
            )

        if choice == "misc":
            user_type = "Bot" if user.bot else "User" if isinstance(user, discord.User) else "Member"
            embed.add_field(
                name="User Info 2:",
                value=f"Type: {user_type} \n**Joined Discord**: \n{discord.utils.format_dt(user.created_at, style = 'd')}\n{discord.utils.format_dt(user.created_at, style = 'T')}",
                inline=False,
            )

        if choice == "avatar":
            embed = discord.Embed(color=random.randint(0, 16777215))
            embed.set_author(name=f"{user.name}'s avatar:", icon_url=user.display_avatar.url)
            embed.set_image(url=user.display_avatar.url)
            embed.set_footer(text=f"Requested by {self.ctx.author}")

        if choice == "status":
            embed.add_field(name=f"{join_statuses}", value="\u2800", inline=False)

        if choice == "guildinfo":
            embed.add_field(
                name="Guild Info:",
                value=f"**Joined Guild**: {joined_guild} \n**Nickname**: {nickname} \n**Highest Role:** {highest_role}",
                inline=False,
            )

        if choice == "banner":
            if self.banner is None and not self.banner_fetched:
                try:
                    user_banner = await interaction.client.fetch_user(user.id)

                except:
                    user_banner = user
                    traceback.print_exc()

                self.banner = user_banner.banner
                self.banner_fetched = True

            banner = self.banner
            if banner:
                embed.set_image(url=banner.url)

            else:
                embed.add_field(name="Banner:", value="No Banner Found", inline=False)

        if choice == "close":
            self.view.remove_item(self)
            return await interaction.response.edit_message(view=self.view, embed=None)

        embed.set_footer(text=f"Support Guild's Name: \n{support_guild}")

        await interaction.response.edit_message(embed=embed)


class OwnerInfoSuper(discord.ui.View):
    def __init__(self, ctx, user, support_guild, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.user = user
        self.support_guild = support_guild

        self.add_item(UserInfoButton(discord.ButtonStyle.success, "Ephemeral", "🕵️", custom_id="0"))
        self.add_item(UserInfoButton(label="Direct", style=discord.ButtonStyle.success, emoji="📥", custom_id="1"))
        self.add_item(UserInfoButton(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️", custom_id="2"))
        self.add_item((OwnerSuperSelects(ctx)))

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


class GuildInfoSelects(discord.ui.Select):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx

        options = [
            discord.SelectOption(label="Basic Info", description="Simple Info", value="basic", emoji="📝"),
            discord.SelectOption(
                label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"
            ),
            discord.SelectOption(
                label="Owner Info",
                description="Shows owner's info",
                value="owner",
                emoji="<:_:585789630800986114>",
            ),
            discord.SelectOption(
                label="Icon",
                description="Show's the guild's icon",
                emoji="🖼️",
                value="icon",
            ),
            discord.SelectOption(
                label="Role/Channel Count", description="Show's Channel and Role Count", emoji="🖼️", value="weirdcount"
            ),
            discord.SelectOption(
                label="Member Info",
                description="Shows the Bot/Human Count",
                value="bot_or_human",
                emoji="<:members:917747437429473321>",
            ),
            discord.SelectOption(
                label="Emoji Data",
                description="Gives Emoji Stats",
                value="emoji_data",
                emoji="📜",
            ),
            discord.SelectOption(label="Statuses", description="Users' Presences", emoji="🖼️", value="statuses"),
            discord.SelectOption(label="Extra", description="Shows leftover data", value="extra", emoji="📝"),
            discord.SelectOption(
                label="Close",
                description="Closes the Select",
                value="close",
                emoji="❌",
            ),
        ]

        super().__init__(placeholder="What Info would you like to view?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        choice = self.values[0]
        guild = self.view.guild

        embed = discord.Embed(title=f"{guild}", color=random.randint(0, 16777215))

        if choice == "basic":
            embed.add_field(
                name="Guild Info:",
                value=f"**Server Name**: {guild} \n**ID**: {guild.id}",
                inline=False,
            )

        if choice == "close":
            self.view.remove_item(self)
            return await interaction.response.edit_message(content="Select Completed", view=self.view, embed=None)

        if choice == "misc":
            # guild type maybe?
            # Type: {} \n
            # placed if maybe used, likely no though.

            embed.add_field(
                name="Guild Info 2:",
                value=f"**Server Creation**: \n{discord.utils.format_dt(guild.created_at, style = 'd')}\n{discord.utils.format_dt(guild.created_at, style = 'T')}",
                inline=False,
            )

        if choice == "owner":
            embed.add_field(name="Owner:", value=f"**Name**: {guild.owner} \n**ID**: {guild.owner_id}")

        embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")

        if choice == "icon":
            embed = discord.Embed(color=random.randint(0, 16777215))
            embed.set_author(
                name=f"{guild}'s icon:", icon_url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png"
            )
            embed.set_image(url=guild.icon.url if guild.icon else "https://i.imgur.com/3ZUrjUP.png")
            embed.set_footer(text=f"Requested by {self.ctx.author}")

        if choice == "weirdcount":
            embed.add_field(
                name="Channel/Role Count:",
                value=f"**Channels**: {len(guild.channels)} \n**Roles**: {len(guild.roles)}",
            )

        if choice == "bot_or_human":
            bots = [m for m in guild.members if m.bot]
            humans = [m for m in guild.members if not m.bot]

            embed.add_field(
                name="Member Count:",
                value=f"**Total** : {guild.member_count}\n**Users** : {len(humans)} \n**Bots** : {len(bots)} ",
            )

            # {var:,} for comma handling soon

        if choice == "statuses":
            base_status = collections.Counter([x.status for x in guild.members])
            online_users = base_status[discord.Status.online]
            dnd_users = base_status[discord.Status.dnd]
            idle_users = base_status[discord.Status.idle]
            offline_users = base_status[discord.Status.offline]

            embed.add_field(
                name="Members:",
                value=f"**Online** : {online_users} \n**DND** : {dnd_users} \n**Idle** : {idle_users} \n**Offline** : {offline_users}",
            )

        if choice == "emoji_data":
            static_emojis = sum(not e.animated for e in guild.emojis)
            animated_emojis = sum(e.animated for e in guild.emojis)
            usable_emojis = sum(e.available for e in guild.emojis)

            embed.add_field(
                name="Emoji Data:",
                value=f"**Limit** : {guild.emoji_limit}\n**Static** : {static_emojis} \n**Animated** : {animated_emojis} \n**Total** : {len(guild.emojis)}/{guild.emoji_limit*2} \n**Usable** : {usable_emojis}",
            )

        if choice == "extra":
            animated_value = guild.icon.is_animated() if guild.icon else False
            embed.add_field(
                name="Extra Info:",
                value=f"**Animated Icon**: {animated_value} \n**Max File Size**: {guild.filesize_limit/1000000} MB \n**Shard ID**: {guild.shard_id}",
            )

        await interaction.response.edit_message(embed=embed)


class GuildInfoView(discord.ui.View):
    def __init__(self, ctx, guild, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.guild = guild

        self.add_item((GuildInfoSelects(ctx)))

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


# The Basic Buttons Class.


class BasicButtons(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.value: str = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.value = True
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="✖️")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Delete", emoji="<:trash:362024157015441408>")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="I am deleting it for you", ephemeral=True)
        if self.view.message:
            await self.view.message.delete()


class DeleteButtonView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.add_item(DeleteButton())

    async def interaction_check(self, interaction: discord.Interaction):
        owner_check = await interaction.client.is_owner(interaction.user)

        if owner_check or interaction.user.id == self.ctx.author.id:
            return True

        await interaction.response.send_message(
            content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
            ephemeral=True,
        )
        return False


class BasicShuffleQuestion(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.value: str = None

    @discord.ui.button(label="Closest", style=discord.ButtonStyle.success, emoji="🔍")
    async def closest(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.value = False
        self.stop()

    @discord.ui.button(label="shuffle", style=discord.ButtonStyle.danger, emoji="🔀")
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.value = True
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


class BotSettings(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    @discord.ui.button(label="Suspend", style=discord.ButtonStyle.danger, emoji="🔒", row=0)
    async def suspend(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="Alright Suspending the bot(check the confirmation you will get).", view=None
        )
        interaction.client.suspended = True
        await interaction.followup.send(content="Alright Boss, I now locked the bot to owners only", ephemeral=True)

    @discord.ui.button(label="Unsuspend", style=discord.ButtonStyle.success, emoji="🔓", row=0)
    async def unsuspend(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Unsuspended the bot :)", view=None)
        interaction.client.suspended = False

        await interaction.followup.send(
            content="Alright Boss, I unlocked the commands, they will work with you all again.", ephemeral=True
        )

    @discord.ui.button(label="Prefixless", style=discord.ButtonStyle.success, emoji="<_:973270656860958730>", row=1)
    async def Prefixless(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="owner only blank prefixes are enabled", view=None)
        interaction.client.prefixless = True

        await interaction.followup.send(
            content="Alright Boss, I now made the bot prefixless(for owners only)", ephemeral=True
        )

    @discord.ui.button(label="Prefix", style=discord.ButtonStyle.danger, emoji="<:_:973270656969998376> ", row=1)
    async def prefix_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Requiring everyone to use prefixes again", view=None)
        interaction.client.prefixless = False

        await interaction.followup.send(
            content="Alright Boss, I now made the bot require a prefix for everyone.", ephemeral=True
        )

    @discord.ui.button(label="Cancel the Command", style=discord.ButtonStyle.success, emoji="✖️", row=2)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Canceling, this boss.", view=None)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


# A Nitro Button Class(not actual nitro)


class nitroButtons(discord.ui.View):
    @discord.ui.button(label=f'{"Claim":⠀^37}', custom_id="fun (nitro)", style=discord.ButtonStyle.success)
    async def nitroButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Oh no it was a fake", ephemeral=True)
        await asyncio.sleep(2)

        message = await interaction.original_response()

        # message = await interaction.followup.send(
        # content="You closed the message, so I can't edit it.", ephemeral=True
        # )

        await message.edit(content="Prepare to get rickrolled...(it's a good song anyway)")
        await asyncio.sleep(2)

        await message.edit(content="https://i.imgur.com/NQinKJB.gif")

        button.disabled = True
        button.style = discord.ButtonStyle.secondary
        button.label = f'{"Claimed":⠀^39}'

        embed = discord.Embed(
            title="You received a gift, but...",
            description="The gift link has either expired or has been\nrevoked.",
            color=3092790,
        )
        embed.set_thumbnail(url="https://i.imgur.com/w9aiD6F.png")

        await interaction.message.edit(view=self, embed=embed)

    async def on_timeout(self):
        self.children[0].disabled = True
        self.children[0].style = discord.ButtonStyle.secondary
        self.children[0].label = f'{"Claimed":⠀^39}'

        embed = discord.Embed(
            title="You received a gift, but...",
            description="The gift link has either expired or has been\nrevoked.",
            color=3092790,
        )
        embed.set_thumbnail(url="https://i.imgur.com/w9aiD6F.png")

        await self.message.edit(view=self, embed=embed)


class ReRun(discord.ui.View):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.view = view
        self.ctx = view.ctx

    @discord.ui.button(label="Rerun", style=discord.ButtonStyle.success, emoji="🔁")
    async def rerun(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        self.view.message = await interaction.followup.send(
            content=self.view.content, embed=self.view.embed, ephemeral=True, view=self.view, wait=True
        )

    @discord.ui.button(label="Replay", style=discord.ButtonStyle.success, emoji="🔂")
    async def replay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=self.view.content, embed=self.view.embed, view=self.view)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.success, emoji="🔒")
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.view.message.edit(content="Looks it like it timed out.(may want to make an new game)", view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.",
                ephemeral=True,
            )

        return True


class RpsGameButton(discord.ui.Button):
    def __init__(self, label: str, emoji, custom_id):
        super().__init__(style=discord.ButtonStyle.success, label=label, custom_id=custom_id, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        assert self.view is not None
        view = self.view
        view.content = view.message.content
        view.embed = view.message.embeds[0]
        message = view.message
        choosen = int(self.custom_id)
        await view.message.edit(content="Results:", view=None)
        deciding = random.randint(1, 3)
        number_to_text = {1: "Rock", 2: "Paper", 3: "Scissors"}

        embed = discord.Embed(title=f"RPS Game", color=random.randint(0, 16777215), timestamp=message.created_at)

        if choosen == deciding:
            text = "Tie!"

        if choosen == 1 and deciding == 3 or choosen == 2 and deciding == 1 or choosen == 3 and deciding == 2:
            text = "You Won!"

        if choosen == 3 and deciding == 1 or choosen == 1 and deciding == 2 or choosen == 2 and deciding == 3:
            text = "You lost!"

        embed.set_author(name=text, icon_url=view.ctx.author.display_avatar.url)
        embed.set_footer(text=f"{view.ctx.author.id}")

        embed.add_field(name="You Picked:", value=f"{number_to_text[choosen]}")
        embed.add_field(name="Bot Picked:", value=f"{number_to_text[deciding]}")

        embed.set_image(url="https://i.imgur.com/bFYroWk.gif")

        for i in view.children:
            if i.custom_id == "4":
                view.remove_item(i)

        self.view.gun_check()

        view = ReRun(view)
        await message.edit(
            content="Here's the results(Hit the Rerun button to run again, if not exit with the exit button):",
            embed=embed,
            view=view,
        )


class RpsGameButtonGun(discord.ui.Button):
    def __init__(self, label: str, emoji, custom_id):
        super().__init__(style=discord.ButtonStyle.success, label=label, custom_id=custom_id, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="You got the legendary gun :) \nYou Instantly Won!", ephemeral=True
        )
        assert self.view is not None
        view = self.view
        view.content = view.message.content
        view.embed = view.message.embeds[0]
        message = view.message
        choosen = int(self.custom_id)
        await view.message.edit(content="Results:", view=None)
        deciding = random.randint(1, 3)
        number_to_text = {1: "Rock", 2: "Paper", 3: "Scissors", 4: "Gun"}

        embed = discord.Embed(title=f"RPS Game", color=random.randint(0, 16777215), timestamp=message.created_at)

        text = "You Won"

        embed.set_author(name=text, icon_url=view.ctx.author.display_avatar.url)
        embed.set_footer(text=f"{view.ctx.author.id}")

        embed.add_field(name="You Picked:", value=f"{number_to_text[choosen]}")
        embed.add_field(name="Bot Picked:", value=f"{number_to_text[deciding]}")

        embed.set_image(url="https://i.imgur.com/bFYroWk.gif")

        for i in view.children:
            if i.custom_id == "4":
                view.remove_item(i)

        self.view.gun_check()

        view = ReRun(view)
        await message.edit(
            content="Here's the results(Hit the Rerun button to run again, if not exit with the exit button):",
            embed=embed,
            view=view,
        )


# a custom Rps Game View
class RpsGame(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.add_item(RpsGameButton("Rock", "🪨", "1"))
        self.add_item(RpsGameButton("Paper", "📰", "2"))
        self.add_item(RpsGameButton("Scissors", "✂️", "3"))
        self.gun_check()

    def gun_check(self):
        if random.random() < 0.167:
            self.add_item(RpsGameButtonGun("Gun", "🔫", "4"))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(
            content="You didn't respond fast enough, you lost.(Play again by running game again)", view=self
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.",
                ephemeral=True,
            )

        return True


class CoinFlipButton(discord.ui.Button):
    def __init__(self, label: str, emoji):
        super().__init__(style=discord.ButtonStyle.success, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        assert self.view is not None
        view = self.view
        view.content = view.message.content
        view.embed = view.message.embeds[0]
        message = view.message
        await view.message.edit(view=None)

        choosen = self.label
        value = random.choice(["Heads", "Tails"])
        win = choosen == value

        url_dic = {"Heads": "https://i.imgur.com/C3tF8ud.png", "Tails": "https://i.imgur.com/tSmhWgg.png"}
        embed = discord.Embed(title="coin flip", color=random.randint(0, 16777215))
        embed.set_author(name=f"{view.ctx.author}", icon_url=view.ctx.author.display_avatar.url)
        embed.add_field(name=f"The Coin Flipped:", value=f"{value}")
        embed.add_field(name="You guessed:", value=f"{choosen}")
        embed.set_thumbnail(url=url_dic[value])
        text = "You Won" if (win) else "You lost"
        embed.add_field(name="Result: ", value=text)
        view = ReRun(view)
        await message.edit(
            content="Here's the results(Hit the Rerun button to run again, if not exit with the exit button):",
            embed=embed,
            view=view,
        )


class CoinFlip(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.add_item(CoinFlipButton("Heads", "<:Moon:960236758342172722>"))
        self.add_item(CoinFlipButton("Tails", "<:Star:960236759944409178>"))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks it like it timed out.(may want to make an new game)", view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.",
                ephemeral=True,
            )

        return True


class GuessingButton(discord.ui.Button):
    def __init__(self, number: int, emoji: str):
        self.number = number
        super().__init__(style=discord.ButtonStyle.success, label=str(number), emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        assert self.view is not None
        view = self.view
        view.content = view.message.content
        view.embed = view.message.embeds[0]
        message = view.message
        await view.message.edit(view=None)

        choosen = self.label
        value = str(random.choice(self.view.numbers))
        win = choosen == value

        embed = discord.Embed(title="Picked Random Number", color=random.randint(0, 16777215))
        embed.set_author(name=f"{view.ctx.author}", icon_url=view.ctx.author.display_avatar.url)
        embed.add_field(name=f"The Bot picked:", value=f"{value}")
        embed.add_field(name="You guessed:", value=f"{choosen}")
        embed.set_image(url="https://i.imgur.com/SSgk15U.gif")
        text = "You Won" if (win) else "You lost"
        embed.add_field(name="Result: ", value=text)
        view = ReRun(view)
        await message.edit(
            content="Here's the results(Hit the Rerun button to run again, if not exit with the exit button):",
            embed=embed,
            view=view,
        )


class GuessingGame(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        numbers = random.sample(range(10, 100), k=4)
        self.numbers = numbers
        self.add_item(GuessingButton(numbers[0], "<:dice:949543735417524234>"))
        self.add_item(GuessingButton(numbers[1], "<:dice:949543734985490493>"))
        self.add_item(GuessingButton(numbers[2], "<:dice:949543735404949504>"))
        self.add_item(GuessingButton(numbers[-1], "🎲"))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks it like it timed out.(may want to make an new game)", view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.",
                ephemeral=True,
            )

        return True
