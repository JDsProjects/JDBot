import discord
import asyncio
import random
from discord.ext import commands
import mathjspy

from typing import Literal, Optional, Dict, Any, List, Union, Tuple


class PaginatorButton(discord.ui.Button["Paginator"]):
    def __init__(
        self,
        *,
        emoji: Optional[Union[discord.PartialEmoji, str]] = None,
        label: Optional[str] = None,
        style: discord.ButtonStyle = discord.ButtonStyle.blurple,
        position: Optional[int] = None,
    ) -> None:

        super().__init__(emoji=emoji, label=label, style=style)

        if not emoji and not label:
            raise ValueError("A label or emoji must be provided.")

        self.position: Optional[int] = position

    async def callback(self, interaction: discord.Interaction):

        assert self.view is not None

        if self.custom_id == "stop_button":
            await self.view.stop()
            return

        if self.custom_id == "right_button":
            self.view.current_page += 1
        elif self.custom_id == "left_button":
            self.view.current_page -= 1
        elif self.custom_id == "first_button":
            self.view.current_page = 0
        elif self.custom_id == "last_button":
            self.view.current_page = self.view.max_pages - 1

        self.view.page_string: str = f"Page {self.view.current_page + 1}/{self.view.max_pages}"

        if self.view.PAGE_BUTTON is not None:
            self.view.PAGE_BUTTON.label = self.view.page_string

        if self.view.current_page == 0:
            if self.view.FIRST_BUTTON is not None:
                self.view.FIRST_BUTTON.disabled = True
            if self.view.LEFT_BUTTON is not None:
                self.view.LEFT_BUTTON.disabled = True
        else:
            if self.view.FIRST_BUTTON is not None:
                self.view.FIRST_BUTTON.disabled = False
            if self.view.LEFT_BUTTON is not None:
                self.view.LEFT_BUTTON.disabled = False

        if self.view.current_page >= self.view.max_pages - 1:
            if self.view.LAST_BUTTON is not None:
                self.view.LAST_BUTTON.disabled = True
            if self.view.RIGHT_BUTTON is not None:
                self.view.RIGHT_BUTTON.disabled = True
        else:
            if self.view.LAST_BUTTON is not None:
                self.view.LAST_BUTTON.disabled = False
            if self.view.RIGHT_BUTTON is not None:
                self.view.RIGHT_BUTTON.disabled = False

        page_kwargs, _ = await self.view.get_page_kwargs(self.view.current_page)
        assert interaction.message is not None and self.view.message is not None

        try:
            await interaction.message.edit(**page_kwargs)
        except (discord.HTTPException, discord.Forbidden, discord.NotFound):
            await self.view.message.edit(**page_kwargs)


class Paginator(discord.ui.View):

    FIRST_BUTTON: PaginatorButton
    LAST_BUTTON: PaginatorButton
    LEFT_BUTTON: PaginatorButton
    RIGHT_BUTTON: PaginatorButton
    STOP_BUTTON: PaginatorButton
    PAGE_BUTTON: PaginatorButton

    def __init__(
        self,
        pages: Union[List[discord.Embed], List[str]],
        ctx: Optional[commands.Context] = None,
        author_id: Optional[int] = None,
        *,
        buttons: Dict[str, Union[PaginatorButton, None]] = {},
        disable_after: bool = False,
        delete_message_after: bool = False,
        clear_after: bool = False,
        timeout: int = 180,
    ):

        super().__init__(timeout=timeout)

        DEFAULT_BUTTONS: Dict[str, Union[PaginatorButton, None]] = {
            "first": PaginatorButton(emoji="⏮️", style=discord.ButtonStyle.secondary),
            "left": PaginatorButton(emoji="◀️", style=discord.ButtonStyle.secondary),
            "right": PaginatorButton(emoji="▶️", style=discord.ButtonStyle.secondary),
            "last": PaginatorButton(emoji="⏭️", style=discord.ButtonStyle.secondary),
            "stop": PaginatorButton(emoji="⏹️", style=discord.ButtonStyle.secondary),
            "page": None,
        }

        self.ctx: Optional[commands.Context] = ctx
        self.author_id: Optional[int] = author_id

        self._disable_after = disable_after
        self._delete_message_after = delete_message_after
        self._clear_after = clear_after
        self.buttons: Dict[str, Union[PaginatorButton, None]] = buttons or DEFAULT_BUTTONS
        self.message: Optional[discord.Message] = None

        self.pages: Union[List[discord.Embed], List[str]] = pages
        self.current_page: int = 0
        self.max_pages: int = len(self.pages)
        self.page_string: str = f"Page {self.current_page + 1}/{self.max_pages}"

        self._add_buttons(DEFAULT_BUTTONS)

    def _add_buttons(self, default_buttons: Dict[str, Union[PaginatorButton, None]]) -> None:

        if self.max_pages <= 1:
            super().stop()
            return

        VALID_KEYS = ["first", "left", "right", "last", "stop", "page"]
        if all(b in VALID_KEYS for b in self.buttons.keys()) is False:
            raise ValueError(f"Buttons keys must be in: `{', '.join(VALID_KEYS)}`")

        if all(isinstance(b, PaginatorButton) or b is None for b in self.buttons.values()) is False:
            raise ValueError("Buttons values must be PaginatorButton instances or None.")

        button: Union[PaginatorButton, None]

        for name, button in default_buttons.items():

            for custom_name, custom_button in self.buttons.items():

                if name == custom_name:
                    button = custom_button

            setattr(self, f"{name}_button".upper(), button)

            if button is None:
                continue

            button.custom_id = f"{name}_button"

            if button.custom_id == "page_button":
                button.label = self.page_string
                button.disabled = True

            if button.custom_id in ("first_button", "last_button") and self.max_pages <= 2:
                continue

            if button.custom_id in ("first_button", "left_button") and self.current_page <= 0:
                button.disabled = True

            if button.custom_id in ("last_button", "right_button") and self.current_page >= self.max_pages - 1:
                button.disabled = True

            self.add_item(button)

        self._set_button_positions()

    def _set_button_positions(self) -> None:
        """Moves the buttons to the desired position"""

        button: PaginatorButton

        for button in self.children:

            if button.position is not None:

                self.children.insert(button.position, self.children.pop(self.children.index(button)))

    async def format_page(self, page: Union[discord.Embed, str]) -> Union[discord.Embed, str]:
        return page

    async def get_page_kwargs(self: "Paginator", page: int, send_kwargs: Optional[Dict[str, Any]] = None):

        if send_kwargs is not None:
            send_kwargs.pop("content", None)
            send_kwargs.pop("embed", None)
            send_kwargs.pop("embeds", None)

        formatted_page = await discord.utils.maybe_coroutine(self.format_page, self.pages[page])

        files = []
        if isinstance(formatted_page, tuple):
            if len(formatted_page) == 2 and isinstance(formatted_page[1], discord.File):
                files.append(formatted_page[1])
                formatted_page = formatted_page[0]

        kwargs = {"content": None, "embed": None, "view": self}
        if files:
            kwargs["files"] = files

        if isinstance(formatted_page, str):
            formatted_page += f"\n\n{self.page_string}"
            kwargs["content"] = formatted_page
            return kwargs, send_kwargs or {}

        elif isinstance(formatted_page, discord.Embed):
            if files:
                formatted_page.set_image(url=f"attachment://{files[0].filename}")

            formatted_page.set_footer(text=self.page_string)

            kwargs["embed"] = formatted_page
            return kwargs, send_kwargs or {}

        else:
            return {}, send_kwargs or {}

    async def on_timeout(self) -> None:
        await self.stop()

    async def interaction_check(self, interaction: discord.Interaction):

        if not interaction.user or not self.ctx or not self.author_id:
            return True

        if self.author_id and not self.ctx:
            return interaction.user.id == self.author_id
        else:

            if not interaction.user.id in {
                getattr(self.ctx.bot, "owner_id", None),
                self.ctx.author.id,
                *getattr(self.ctx.bot, "owner_ids", {}),
            }:
                return False

        return True

    async def stop(self):

        super().stop()

        assert self.message is not None

        if self._delete_message_after:
            await self.message.delete()
            return

        elif self._clear_after:
            await self.message.edit(view=None)
            return

        elif self._disable_after:

            for item in self.children:
                item.disabled = True

            await self.message.edit(view=self)

    async def send_as_interaction(
        self, interaction: discord.Interaction, ephemeral: bool = False, *args, **kwargs
    ) -> Optional[Union[discord.Message, discord.WebhookMessage]]:
        page_kwargs, send_kwargs = await self.get_page_kwargs(self.current_page, kwargs)
        if not interaction.response.is_done():
            send = interaction.response.send_message
        else:

            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=ephemeral)

            send_kwargs["wait"] = True
            send = interaction.followup.send

        ret = await send(*args, ephemeral=ephemeral, **page_kwargs, **send_kwargs)

        if not ret:
            try:
                self.message = await interaction.original_message()
            except (discord.ClientException, discord.HTTPException):
                self.message = None
        else:
            self.message = ret

        return self.message

    async def send(
        self, send_to: Union[discord.abc.Messageable, discord.Message], *args: Any, **kwargs: Any
    ) -> discord.Message:

        page_kwargs, send_kwargs = await self.get_page_kwargs(self.current_page, kwargs)

        if isinstance(send_to, discord.Message):

            self.message = await send_to.reply(*args, **page_kwargs, **send_kwargs)
        else:

            self.message = await send_to.send(*args, **page_kwargs, **send_kwargs)

        return self.message


# thank you so much Soheab for allowing me to use this paginator you made and putting in the work to do this :D (That's his github name so...)


class MutualGuildsEmbed(Paginator):
    def format_page(self, item):
        embed = discord.Embed(title="Mutual Servers:", description=item, color=random.randint(0, 16777215))

        return embed


class ServersEmbed(Paginator):
    def format_page(self, item):
        embed = discord.Embed(title="Servers:", description=item, color=random.randint(0, 16777215))
        return embed


class PrefixesEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Usable Prefixes:", description=item, color=random.randint(0, 16777215))
        return embed


class LeaderboardEmbed(Paginator):
    async def format_page(self, item):

        emby = discord.Embed(title="Leaderboard", color=15428885)
        emby.set_author(
            name=f"Leaderboard Requested by {self.ctx.author}", icon_url=(self.ctx.author.display_avatar.url)
        )

        for i, b, w in item:
            emby.add_field(
                name=f"**${i}:**", value=f"```yaml\nBank: ${b:,}\nWallet: ${w:,}\nTotal: ${b+w:,}```", inline=False
            )

        return emby


class RandomHistoryEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Random History:", description=f"{item}", color=random.randint(0, 16777215))
        embed.set_footer(text="Powered by Random quotes From: \nhttps://www.youtube.com/watch?v=xuCn8ux2gbs")
        return embed


class TestersEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Testing Users:", color=random.randint(0, 16777215))
        embed.add_field(name="User ID:", value=f"{item}", inline=False)

        return embed


class SusUsersEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Users Deemed Suspicious by JDJG Inc. Official", color=random.randint(0, 16777215))
        embed.add_field(
            name=f"User ID : {item.get('user_id')}", value=f"**Reason :** {item.get('reason')}", inline=False
        )
        return embed


class BlacklistedUsersEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Users Blacklisted by JDJG Inc. Official", color=random.randint(0, 16777215))
        embed.add_field(
            name=f"User ID : {item.get('user_id')}", value=f"**Reason :** {item.get('reason')}", inline=False
        )
        return embed


class ErrorEmbed(Paginator):
    async def format_page(self, item):

        item = discord.utils.escape_markdown(item, as_needed=False, ignore_links=True)
        return discord.Embed(title="Error", description=item, color=random.randint(0, 16777215))


class RtfmEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Packages:", description=item, color=random.randint(0, 16777215))
        return embed


class SendHelp(Paginator):
    async def format_page(self, item):
        emby = discord.Embed(description=item, color=15428885)
        return emby


class charinfoMenu(Paginator):
    async def format_page(self, item):
        return discord.Embed(description=item, color=random.randint(0, 16777215))


class InviteInfoEmbed(Paginator):
    async def format_page(self, item):
        if isinstance(item, discord.Invite):

            if item.guild:
                image = item.guild.icon.url if item.guild.icon else "https://i.imgur.com/3ZUrjUP.png"
                guild = item.guild
                guild_id = item.guild.id
            if item.guild is None:
                guild = "Group Chat"
                image = "https://i.imgur.com/pQS3jkI.png"
                guild_id = "Unknown"
            embed = discord.Embed(title=f"Invite for {guild}:", color=random.randint(0, 16777215))
            embed.set_author(name="Discord Invite Details:", icon_url=(image))
            embed.add_field(name="Inviter:", value=f"{item.inviter}")
            embed.add_field(name="User Count:", value=f"{item.approximate_member_count}")
            embed.add_field(name="Active User Count:", value=f"{item.approximate_presence_count}")

            embed.add_field(
                name="Invite Channel",
                value=f"{item.channel}\nChannel Mention : {'None' if isinstance(item.channel, discord.Object) else item.channel.mention}",
            )

            embed.set_footer(text=f"ID: {guild_id}\nInvite Code: {item.code}\nInvite Url: {item.url}")

        if isinstance(item, str):
            embed = discord.Embed(
                title="Failed grabbing the invite code:",
                description=f"Discord couldnt fetch the invite with the code {item}.",
                color=random.randint(0, 16777215),
            )
            embed.set_footer(text="If this is a consistent problem please contact JDJG Inc. Official#3493")

        return embed


class GoogleEmbed(Paginator):
    async def format_page(self, item):

        embed = discord.Embed(
            title="Gooogle Search",
            description=f"[{item.title}]({item.link}) \n{item.snippet}",
            color=random.randint(0, 16777215),
        )

        if item.image:
            embed.set_image(url=item.image)

        embed.set_footer(
            text=f"Google does some sketchy ad stuff, and descriptions from google are shown here, please be careful :D, thanks :D"
        )

        return embed


def guild_join(guilds):
    return "\n".join(map(str, guilds))


def grab_mutualguilds(ctx, user):
    mutual_guilds = set(ctx.author.mutual_guilds)
    mutual_guilds2 = set(user.mutual_guilds)

    return list(mutual_guilds.intersection(mutual_guilds2))


async def get_sus_reason(ctx, user):
    sus_users = dict(await ctx.bot.db.fetch("SELECT * FROM SUS_USERS;"))
    return sus_users.get(user.id)


class ScanGlobalEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(color=random.randint(0, 16777215))

        embed.set_author(name=f"{item}", icon_url=item.display_avatar.url)

        embed.add_field(name="Shared Guilds:", value=f"{guild_join(grab_mutualguilds(self.ctx, item))}")
        embed.set_footer(text=f"Sus Reason : {await get_sus_reason(self.ctx, item)}")
        return embed


class EmojiInfoEmbed(Paginator):
    async def format_page(self, item):
        if isinstance(item, discord.PartialEmoji):
            if item.is_unicode_emoji():
                digit = f"{ord(str(item)):x}"
                unicode = f"\\U{digit:>08}"
                emoji_name = item.name.replace(":", "")
                # emoji_url = await emoji_to_url(f"{item}", session = self.ctx.bot.session)
                # wip
                emoji_url = "https://i.imgur.com/3ZUrjUP.png"
                embed = discord.Embed(
                    title="Default Emote:",
                    url=f"http://www.fileformat.info/info/unicode/char/{digit}",
                    color=random.randint(0, 16777215),
                )
                embed.add_field(name="Name:", value=f"{emoji_name}")
                embed.add_field(name="Unicode:", value=unicode)
                embed.add_field(
                    name="unicode url", value=f"[site](http://www.fileformat.info/info/unicode/char/{digit})"
                )
                embed.set_image(url=emoji_url)
                embed.set_footer(text=f"click the title for more unicode data")
                return embed

            else:
                embed = discord.Embed(title=f"Custom Emoji: **{item.name}**", color=random.randint(0, 16777215))
                embed.set_image(url=item.url)
                embed.set_footer(text=f"Emoji ID:{item.id}")
                return embed

        else:
            embed = discord.Embed(
                title="Failed grabbing emoji:",
                description=f"Discord couldn't fetch the emoji with regex: {item}",
                color=random.randint(0, 16777215),
            )
            return embed


class TodoEmbed(Paginator):
    def format_page(self, item):
        embed = discord.Embed(
            description=item, color=random.randint(0, 16777215), timestamp=self.ctx.message.created_at
        )

        embed.set_author(name=f"Todo Requested By {self.ctx.author}:", icon_url=self.ctx.author.display_avatar.url)
        return embed


# this is using the paginator above, which is why It's not underneath the BasicButtons.


class dm_or_ephemeral(discord.ui.View):
    def __init__(self, ctx, menu=None, channel: discord.DMChannel = None, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.channel = channel
        self.menu = menu

    @discord.ui.button(label="Secret Message(Ephemeral)", style=discord.ButtonStyle.success, emoji="🕵️")
    async def secretMessage(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.clear_items()
        await self.message.edit(content="Will be sending you the information, ephemerally", view=self)

        await self.menu.send_as_interaction(interaction, ephemeral=True)

    @discord.ui.button(label="Secret Message(DM)", style=discord.ButtonStyle.success, emoji="📥")
    async def dmMessage(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.clear_items()
        await self.message.edit(content="Well be Dming you the paginator to view this info", view=self)

        await self.menu.send(self.channel)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.clear_items()
        await self.message.edit(content=f"not sending the paginator to you", view=self)

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
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.value = True
        self.stop()

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):

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


class BotSettings(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    @discord.ui.button(label="Suspend", style=discord.ButtonStyle.danger, emoji="🔒", row=0)
    async def suspend(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(
            content="Alright Suspending the bot(check the confirmation you will get).", view=None
        )
        self.ctx.bot.suspended = True
        await interaction.followup.send(content="Alright Boss, I now locked the bot to owners only", ephemeral=True)

    @discord.ui.button(label="Unsuspend", style=discord.ButtonStyle.success, emoji="🔓", row=0)
    async def unsuspend(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(content="Unsuspended the bot :)", view=None)
        self.ctx.bot.suspended = False

        await interaction.followup.send(
            content="Alright Boss, I unlocked the commands, they will work with you all again.", ephemeral=True
        )

    @discord.ui.button(label="Prefixless", style=discord.ButtonStyle.success, emoji="🔛", row=1)
    async def Prefixless(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(content="owner only blank prefixes are enabled", view=None)
        self.ctx.bot.prefixless = True

        await interaction.followup.send(
            content="Alright Boss, I now made the bot prefixless(for owners only)", ephemeral=True
        )

    @discord.ui.button(
        label="Prefix", style=discord.ButtonStyle.danger, emoji="<:Toggle_Off:904381963828346930>", row=1
    )
    async def prefix_back(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(content="Requiring everyone to use prefixes again", view=None)
        self.ctx.bot.prefixless = False

        await interaction.followup.send(
            content="Alright Boss, I now made the bot require a prefix for everyone.", ephemeral=True
        )

    @discord.ui.button(label="Cancel the Command", style=discord.ButtonStyle.success, emoji="❌", row=2)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):

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
    async def nitroButton(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.send_message(content="Oh no it was a fake", ephemeral=True)
        await asyncio.sleep(2)

        await interaction.edit_original_message(content="Prepare to get rickrolled...(it's a good song anyway)")
        await asyncio.sleep(2)

        await interaction.edit_original_message(content="https://i.imgur.com/NQinKJB.gif")

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
    async def rerun(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(view=None)
        self.view.message = await interaction.followup.send(
            content=self.view.content, embed=self.view.embed, ephemeral=True, view=self.view, wait=True
        )

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.success, emoji="🔒")
    async def exit(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(view=None)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.view.message.edit("Looks it like it timed out.(may want to make an new game)", view=self)

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

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(
            "You didn't respond fast enough, you lost.(Play again by running game again)", view=self
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
        assert self.view is not None
        view = self.view
        view.content = view.message.content
        view.embed = view.message.embeds[0]
        message = view.message
        await view.message.edit(view=None)

        choosen = self.label
        value = random.choice(["Heads", "Tails"])
        win = choosen == value

        url_dic = {"Heads": "https://i.imgur.com/MzdU5Z7.png", "Tails": "https://i.imgur.com/qTf1owU.png"}
        embed = discord.Embed(title="coin flip", color=random.randint(0, 16777215))
        embed.set_author(name=f"{view.ctx.author}", icon_url=view.ctx.author.display_avatar.url)
        embed.add_field(name=f"The Coin Flipped:", value=f"{value}")
        embed.add_field(name="You guessed:", value=f"{choosen}")
        embed.set_image(url=url_dic[value])
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
        self.add_item(CoinFlipButton("Heads", "<:coin:693942559999000628>"))
        self.add_item(CoinFlipButton("Tails", "🪙"))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit("Looks it like it timed out.(may want to make an new game)", view=self)

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

        await self.message.edit("Looks it like it timed out.(may want to make an new game)", view=self)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.",
                ephemeral=True,
            )

        return True


# A bunch of Select Classes and views for them(below me).


class RtfmSelects(discord.ui.Select):
    def __init__(self, options):

        super().__init__(placeholder="Chose a library to lookup from.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class RtfmChoice(discord.ui.View):
    def __init__(self, ctx, libraries, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("link") for o in libraries][0]
        self.ctx = ctx

        self.add_item(
            RtfmSelects([discord.SelectOption(label=o["name"], value=o["link"], emoji="🔍") for o in libraries])
        )

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


class JobSelects(discord.ui.Select):
    def __init__(self, options):

        super().__init__(placeholder="Chose a Job to do.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class JobChoice(discord.ui.View):
    def __init__(self, ctx, jobs, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("job_name") for o in jobs][0]
        self.ctx = ctx

        self.add_item(JobSelects([discord.SelectOption(label=o["job_name"], emoji="🧑‍💼") for o in jobs]))

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


class SubRedditSelects(discord.ui.Select):
    def __init__(self, options):

        super().__init__(placeholder="Chose a Subreddit.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class SubredditChoice(discord.ui.View):
    def __init__(self, ctx, subreddits, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("name") for o in subreddits][0]
        self.ctx = ctx

        self.add_item(
            SubRedditSelects(
                [discord.SelectOption(label=o["name"], emoji="<:reddit:309459767758290944>") for o in subreddits]
            )
        )

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


# These are Calculator Functions
def get_highest(iterable):
    resp = 0
    for i in iterable:
        if i > resp:
            resp = i
    return resp


def get_last_operator(response: str):
    try:
        plus = response.rindex("+")
    except ValueError:
        plus = None
    try:
        minus = response.rindex("-")
    except ValueError:
        minus = None
    try:
        mul = response.rindex("*")
    except ValueError:
        mul = None
    try:
        div = response.rindex("/")
    except ValueError:
        div = None
    valid = [n for n in [plus, minus, mul, div] if n != None]
    indx = get_highest(valid)
    return response[indx:]


async def default_execution_function(view, label, interaction: discord.Interaction):
    view.expression += str(label)
    await interaction.response.edit_message(content=view.expression)


async def operator_handler(view, label, interaction: discord.Interaction):
    if not view.expression or not view.expression[0].isdigit():
        return await interaction.response.send_message("You cannot use operators at start.", ephemeral=True)
    if not view.expression[-1].isdigit():
        return await interaction.response.send_message("You cannot add operator after operator.", ephemeral=True)
    view.expression += label
    await interaction.response.edit_message(content=view.expression)


async def give_result_operator(view, label, interaction: discord.Interaction):
    parser = view.parser
    if not view.expression:
        return await interaction.response.send_message("You didn't tell me anything to evaluate.", ephemeral=True)
    if view.expression.replace(".", "").isdigit() and view.last_expr:
        view.expression += view.last_expr
    else:
        view.last_expr = get_last_operator(view.expression)
    result = str(float(parser.eval(view.expression)))
    view.expression = result
    await interaction.response.edit_message(content=result)


async def stop_button(view, label, interaction: discord.Interaction):
    for i in view.children:
        i.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()


async def go_back(view, label, interaction: discord.Interaction):
    if not view.expression:
        return
    view.expression = view.expression[:-1]
    await interaction.response.edit_message(content=view.expression)


# These are Calculator Buttons
class CalcButton(discord.ui.Button):
    def __init__(
        self, label: str, row: int, execution_function=default_execution_function, style=discord.ButtonStyle.blurple
    ):
        super().__init__(label=label, row=row, style=style)
        self.__func = execution_function

    async def callback(self, interaction: discord.Interaction):
        await self.__func(self.view, self.label, interaction)


# Actual Calculator Buttons
class CalcView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.parser = mathjspy.MathJS()
        self.expression = ""
        self.last_expr = ""
        numb = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        for row in range(len(numb)):
            for i in numb[row]:
                self.add_item(CalcButton(i, row))
        self.add_item(CalcButton("=", 3, give_result_operator, discord.ButtonStyle.gray))
        self.add_item(CalcButton("<==", 3, go_back))
        for label, row in [["+", 0], ["-", 1], ["*", 2], ["/", 3]]:
            self.add_item(CalcButton(label, row, operator_handler, discord.ButtonStyle.green))
        self.add_item(CalcButton(f'{"Stop":⠀^20}', 4, stop_button, discord.ButtonStyle.red))
        self.add_item(CalcButton(".", 4, style=discord.ButtonStyle.green))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                f"This button can only be accessed by {self.ctx.author.name}.", ephemeral=True
            )
            return False
        else:
            return True

    async def on_timeout(self):
        for i in self.children:
            i.disabled = True
        await self.message.edit(content="If you want your calculator to work you need to make a new one.", view=self)
        self.stop()


# Modal Classes
class CodeBlockModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Code Block:", placeholder="Please Put your code here:", style=discord.TextStyle.paragraph
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Code Block Submitted and Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run the pep8 formatter again.", view=self.view)
        self.stop()


class CodeBlockView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.value: str = None
        self.value2: str = None
        self.ctx = ctx
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅", custom_id="accept")
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):

        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = True

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌", custom_id="Deny")
    async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):

        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="<:click:264897397337882624>", row=1)
    async def Submit(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = CodeBlockModal(self, title="Pep8 Project Formatter:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.children[0].value
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class MailModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Message:", placeholder="Please Put Your Message Here:", style=discord.TextStyle.paragraph
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run mail again.", view=self.view)
        self.stop()


class MailView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.value: str = None
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = MailModal(self, title="Mail:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.children[0].value
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class ChatBotModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Message:", placeholder="Please Put Your Message Here:", style=discord.TextStyle.paragraph
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        arg = self.children[0].value
        self.view.message = await interaction.followup.send(f"{arg}", view=self.view, ephemeral=True)

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run chatbot again.", view=self.view)


class ChatBotView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = ChatBotModal(self, title="ChatBot:", timeout=180.0)
        await interaction.defer()
        await interaction.followup.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.success, emoji="❌")
    async def Close(self, button: discord.ui.Button, interaction: discord.Interaction):

        await interaction.response.edit_message(content="Closing ChatBot", view=None)
