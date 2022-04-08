from __future__ import annotations

import discord
import asyncio
import random
import mathjspy

from discord import Interaction, ButtonStyle, Embed, File
from discord.abc import Messageable
from discord.utils import MISSING, maybe_coroutine
from discord.ui import Button, TextInput, Modal, View

from discord.ext.commands.context import Context
from typing import Callable, Optional, Any, Union, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    PossiblePage = Union[str, Embed, File, Sequence[Union[Embed, Any]], tuple[Union[File, Any], ...], dict[str, Any]]


def default_check(author_id: int, /, *, interaction: Interaction = MISSING, ctx: Context = MISSING) -> bool:
    if interaction is MISSING and ctx is MISSING:
        return True

    client = interaction.client if interaction is not MISSING else ctx.bot  # type: ignore
    author = interaction.user if interaction is not MISSING else ctx.author  # type: ignore
    TO_CHECK = {author.id}.union(set(getattr(client, "owner_ids", set())))
    if getattr(client, "owner_id", None):
        TO_CHECK.union({client.owner_id})  # type: ignore

    return author_id in TO_CHECK


class ChooseNumber(Modal):
    def __init__(self, current_page: int, total_pages: int, page_string: str, /):
        super().__init__(
            title="Which page would you like to go to?",
            timeout=15,
            custom_id="paginator:modal:choose_number",
        )

        self._current_page: int = current_page
        self._total_pages: int = total_pages

        self.value: Optional[int] = None  # filled in by on_submit

        self.number_input = TextInput(
            placeholder=f"Current: {page_string}",
            label=f"Enter a page number between 1 and {total_pages}",
            custom_id="paginator:choose_number",
            max_length=len(str(total_pages)),
            min_length=1,
        )

        self.add_item(self.number_input)

    async def on_submit(self, interaction: Interaction) -> None:
        assert isinstance(self.number_input.value, str)

        if (
            not self.number_input.value.isdigit()
            or int(self.number_input.value) <= 0
            or int(self.number_input.value) > self._total_pages
        ):
            await interaction.response.send_message(
                f"Please enter a valid number between 1 and {self._total_pages}", ephemeral=True
            )
            self.stop()
            return

        number = int(self.number_input.value) - 1

        if number == self._current_page:  # type: ignore
            await interaction.response.send_message("That is the current page!", ephemeral=True)
            self.stop()
            return

        self.value = number
        await interaction.response.send_message(f"There is page {self.value + 1} for you <3", ephemeral=True)
        self.stop()


class PaginatorButton(Button["Paginator"]):
    def __init__(
        self,
        *,
        emoji: Optional[str] = None,
        label: Optional[str] = None,
        custom_id: Optional[str] = None,
        style: ButtonStyle = ButtonStyle.blurple,
        row: Optional[int] = None,
        disabled: bool = False,
        position: int = MISSING,
    ):
        super().__init__(emoji=emoji, label=label, custom_id=custom_id, style=style, row=row, disabled=disabled)
        self.position = position
        self.view: Paginator

    async def __handle_number_modal(self, interaction: Interaction) -> Optional[int]:
        modal = ChooseNumber(self.view._current_page, self.view.max_pages, self.view.page_string)
        await interaction.response.send_modal(modal)
        await modal.wait()
        return modal.value

    async def callback(self, interaction: Interaction) -> None:
        self.view.interaction = interaction

        if self.custom_id == "stop_button":
            await self.view.stop()
            return

        if self.custom_id == "right_button":
            self.view._current_page += 1
        elif self.custom_id == "left_button":
            self.view._current_page -= 1
        elif self.custom_id == "first_button":
            self.view._current_page = 0
        elif self.custom_id == "last_button":
            self.view._current_page = self.view.max_pages - 1
        elif self.custom_id == "page_indicator_button":
            new_page = await self.__handle_number_modal(interaction)
            if new_page is not None:
                self.view._current_page = new_page
            else:
                return

        self.view._update_buttons_state()
        pages = self.view.get_page(self.view._current_page)
        edit_kwargs = (await self.view.get_kwargs_from_page(pages)).copy()
        edit_kwargs["attachments"] = edit_kwargs.pop("files")

        await self.view._edit_message(interaction, **edit_kwargs)


class Paginator(View):
    FIRST: Optional[PaginatorButton] = None  # filled in __add_buttons
    LEFT: Optional[PaginatorButton] = None  # filled in __add_buttons
    RIGHT: Optional[PaginatorButton] = None  # filled in __add_buttons
    LAST: Optional[PaginatorButton] = None  # filled in __add_buttons
    STOP: Optional[PaginatorButton] = None  # filled in __add_buttons
    PAGE_INDICATOR: Optional[PaginatorButton] = None  # filled in __add_buttons

    def __init__(
        self,
        pages: Sequence[PossiblePage],
        *,
        ctx: Context = MISSING,
        interaction: Interaction = MISSING,
        author_id: int = MISSING,
        per_page: int = 1,
        buttons: dict = MISSING,
        check: Callable = MISSING,
        timeout: Union[int, float] = 180.0,
        always_show_stop_button: bool = False,
        delete_after: bool = False,
        disable_after: bool = False,
        clear_buttons_after: bool = False,
    ) -> None:
        """Initialize the Paginator."""
        super().__init__(timeout=timeout)
        if ctx is not MISSING and interaction is not MISSING:
            raise ValueError("ctx and interaction cannot be used together")

        DEFAULT_BUTTONS = {
            "FIRST": PaginatorButton(emoji="⏮️", position=0, style=ButtonStyle.secondary),
            "LEFT": PaginatorButton(emoji="◀️", position=1, style=ButtonStyle.secondary),
            # "PAGE_INDICATOR": PaginatorButton(label="Page N/A / N/A", position=2, style=ButtonStyle.secondary),
            "PAGE_INDICATOR": None,
            "STOP": PaginatorButton(emoji="⏹️", position=2, style=ButtonStyle.danger),
            "RIGHT": PaginatorButton(emoji="▶️", position=3, style=ButtonStyle.secondary),
            "LAST": PaginatorButton(emoji="⏭️", position=4, style=ButtonStyle.secondary),
        }

        self._buttons: dict[str, PaginatorButton] = DEFAULT_BUTTONS.copy()
        if buttons is not MISSING:
            self._buttons.update(buttons)

        self.timeout: Union[int, float] = timeout
        # self._message: PossibleMessage = None  # type: ignore # this cannot be None # filled in .send()

        self.ctx = ctx  # can be filled in .send()
        self.interaction = interaction  # can be filled in .send() and when the paginator is used
        self.author_id: int = author_id
        self.check = check if check is not MISSING else default_check

        self.pages: Sequence[PossiblePage] = pages
        self.per_page: int = per_page

        self._max_pages_passed: int = len(pages)
        self._should_always_show_stop_button: bool = always_show_stop_button
        self._should_delete_after: bool = delete_after
        self._should_disable_after: bool = disable_after
        self._should_clear_buttons_after: bool = clear_buttons_after

        self._current_page: int = 0

        if per_page > self._max_pages_passed or per_page < 1:
            raise ValueError(  # nice try though
                f"per_page ({per_page}) must be >= 1 or = len(pages) # >>> {self._max_pages_passed}"
            )

        total_pages, left_over = divmod(self._max_pages_passed, per_page)
        if left_over:
            total_pages += 1

        self._max_pages = total_pages
        self.__add_buttons()

        self.__base_kwargs = {"content": None, "embeds": [], "files": [], "view": self}

    def __reset_base_kwargs(self) -> None:
        self.__base_kwargs = {"content": None, "embeds": [], "files": [], "view": self}

    def __add_buttons(self) -> None:
        if not self._max_pages > 1:
            if self._should_always_show_stop_button:
                if "STOP" not in self._buttons:
                    raise ValueError("STOP button is required if always_show_stop_button is True.")

                name = "STOP"
                button = self._buttons[name]
                button.custom_id = f"{name.lower()}_button"
                setattr(self, name, button)
                self.add_item(button)
                return
            else:
                super().stop()
            return

        _buttons: dict[str, PaginatorButton] = {
            name: button for name, button in self._buttons.items() if button is not None
        }
        sorted_buttons = sorted(_buttons.items(), key=lambda b: b[1].position if b[1].position is not MISSING else 0)
        for name, button in sorted_buttons:
            button.custom_id = f"{name.lower()}_button"
            setattr(self, name, button)

            if button.custom_id == "page_indicator_button":
                button.label = self.page_string
                if self._max_pages <= 2:
                    button.disabled = True

            if button.custom_id in ("first_button", "last_button") and self.max_pages <= 2:
                continue

            self.add_item(button)

        self._update_buttons_state()

    def _update_buttons_state(self) -> None:
        button: PaginatorButton
        for button in self.children:  # type: ignore
            if button.custom_id in ("page_indicator_button",):
                if button.custom_id == "page_indicator_button":
                    button.label = self.page_string
                continue

            elif button.custom_id in ("right_button", "last_button"):
                button.disabled = self._current_page >= self.max_pages - 1
            elif button.custom_id in ("left_button", "first_button"):
                button.disabled = self._current_page <= 0

    @property
    def current_page(self) -> int:
        return self._current_page

    @current_page.setter
    def current_page(self, value: int) -> None:
        self._current_page = value
        self._update_buttons_state()

    @property
    def max_pages(self) -> int:
        return self._max_pages

    @property
    def page_string(self) -> str:
        return f"Page {self.current_page + 1} / {self.max_pages}"

    async def on_timeout(self) -> None:
        await self.stop()

    async def interaction_check(self, interaction: Interaction):
        # Allow everyone if interaction.user or ctx or author_id is None.
        if self.author_id is MISSING and self.ctx is MISSING and self.interaction is MISSING:
            return True

        is_allowed = await maybe_coroutine(
            self.check, interaction.user.id, interaction=interaction, ctx=self.ctx  # type: ignore
        )
        return is_allowed

    async def _edit_message(self, interaction: Interaction = MISSING, /, **kwargs: Any) -> None:
        if interaction is not MISSING:
            self.interaction = interaction

        if self.interaction is not MISSING:
            respond = self.interaction.response.edit_message  # type: ignore
            if self.interaction.response.is_done():  # type: ignore
                respond = self.message.edit if self.message else _interaction.message.edit  # type: ignore

            await respond(**kwargs)
        else:
            await self.message.edit(**kwargs)

    async def stop(self) -> None:
        self.__reset_base_kwargs()
        super().stop()

        if self._should_delete_after:
            await self.message.delete()
            return

        if self._should_clear_buttons_after:
            await self._edit_message(view=None)
            return
        elif self._should_disable_after:
            for button in self.children:
                button.disabled = True  # type: ignore

            await self._edit_message(view=self)
            return

    def format_page(self, page: Union[PossiblePage, Sequence[PossiblePage]]) -> PossiblePage:
        return page  # type: ignore

    def get_page(self, page_number: int) -> Union[PossiblePage, Sequence[PossiblePage]]:
        if page_number < 0 or page_number >= self.max_pages:
            self._current_page = 0
            return self.pages[self._current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        else:
            base = page_number * self.per_page
            return self.pages[base : base + self.per_page]

    async def get_kwargs_from_page(
        self,
        page: Union[PossiblePage, Sequence[PossiblePage]],
        send_kwargs: dict[str, Any] = {},
        skip_formatting: bool = False,
    ) -> dict[str, Any]:
        if not skip_formatting:
            self.__reset_base_kwargs()
            page = await maybe_coroutine(self.format_page, page)

        if send_kwargs:
            for key, value in send_kwargs.items():
                if key in ("embed", "file"):
                    self.__base_kwargs[f"{key}s"] = value
                elif key == "view":
                    continue
                else:
                    self.__base_kwargs.update(send_kwargs)  # type: ignore

        if self.per_page > 1 and isinstance(page, (list, tuple)):
            raise ValueError("format_page must be used to format multiple pages.")

        if isinstance(page, (list, tuple)):
            _page: PossiblePage
            for _page in page:  # type: ignore
                await self.get_kwargs_from_page(_page, skip_formatting=True)  # type: ignore

        if isinstance(page, str):
            self.__base_kwargs["content"] = f"{page}\n\n{self.page_string}"
        elif isinstance(page, dict):
            self.__base_kwargs.update(page)  # type: ignore
        elif isinstance(page, Embed):
            # self.__base_kwargs["embeds"].append(page)
            # set_footer_on = self.__base_kwargs["embeds"][-1]
            # if not set_footer_on.footer.text or set_footer_on.footer.text == self.page_string:
            if not page.footer.text:
                page.set_footer(text=self.page_string)
            else:
                # set_footer_on.set_footer(text=f"{set_footer_on.footer.text} | {self.page_string}")
                page.set_footer(text=f"{page.footer.text} | {self.page_string}")
            self.__base_kwargs["embeds"].append(page)

        elif isinstance(page, File):
            page.reset()
            self.__base_kwargs["files"].append(page)

            if not self.__base_kwargs["content"]:
                self.__base_kwargs["content"] = self.page_string
            else:
                self.__base_kwargs["content"] += f"\n\n{self.page_string}"

        return self.__base_kwargs

    async def send(
        self,
        *,
        ctx: Context = MISSING,
        send_to: Messageable = MISSING,
        interaction: Interaction = MISSING,
        override_custom: bool = True,
        **kwargs,
    ):
        if interaction is not MISSING and ctx is not MISSING:
            raise ValueError("ctx and interaction cannot be used together")

        page = self.get_page(self.current_page)
        send_kwargs = await self.get_kwargs_from_page(page, send_kwargs=kwargs if override_custom else {})

        self.interaction = self.interaction if interaction is MISSING else interaction  # type: ignore
        self.ctx = self.ctx if ctx is MISSING else ctx  # type: ignore

        if send_to is not MISSING:
            self.message = await send_to.send(**send_kwargs)
            return self.message

        elif self.interaction is not MISSING:
            respond = self.interaction.response.send_message  # type: ignore
            if self.interaction.response.is_done():  # type: ignore
                send_kwargs["wait"] = True  # type: ignore

                respond = self.interaction.followup.send  # type: ignore

            maybe_message = await respond(**send_kwargs)
            if maybe_message:
                self.message = maybe_message
                return self.message
            else:
                self.message = await self.interaction.original_message()  # type: ignore
                return self.message

        elif self.ctx is not MISSING:
            self.message = await self.ctx.send(**send_kwargs)  # type: ignore
            return self.message

        else:
            raise ValueError("ctx or interaction or send_to must be provided")


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
    async def secretMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="Will be sending you the information, ephemerally", view=self)

        await self.menu.send(interaction=interaction, ephemeral=True)

    @discord.ui.button(label="Secret Message(DM)", style=discord.ButtonStyle.success, emoji="📥")
    async def dmMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="Well be Dming you the paginator to view this info", view=self)

        await self.menu.send(send_to=self.channel)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content=f"not sending the paginator to you", view=self)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True


class UserInfoSuper(discord.ui.View):
    def __init__(self, ctx, menu=None, channel: discord.DMChannel = None, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.channel = channel
        self.menu = menu

    @discord.ui.button(label="Secret Message(Ephemeral)", style=discord.ButtonStyle.success, emoji="🕵️")
    async def secretMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        for child in self.children:
            if isinstance(child, (discord.Button, discord.ui.Button)):
                self.remove_item(child)

        await self.message.edit(content="Will be sending you the information, ephemerally", view=self)

        await self.menu.send(interaction=interaction, ephemeral=True)

    @discord.ui.button(label="Secret Message(DM)", style=discord.ButtonStyle.success, emoji="📥")
    async def dmMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        for child in self.children:
            if isinstance(child, (discord.Button, discord.ui.Button)):
                self.remove_item(child)

        await interaction.response.edit_message(content=f"Well be Dming you the paginator to view this info", view=self)

        await self.menu.send(send_to=self.channel)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):

        for child in self.children:
            if isinstance(child, (discord.Button, discord.ui.Button)):
                self.remove_item(child)

        await interaction.response.edit_message(content=f"not sending the paginator to you", view=self)

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

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌")
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

    @discord.ui.button(label="Prefixless", style=discord.ButtonStyle.success, emoji="🔛", row=1)
    async def Prefixless(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="owner only blank prefixes are enabled", view=None)
        interaction.client.prefixless = True

        await interaction.followup.send(
            content="Alright Boss, I now made the bot prefixless(for owners only)", ephemeral=True
        )

    @discord.ui.button(
        label="Prefix", style=discord.ButtonStyle.danger, emoji="<:Toggle_Off:904381963828346930>", row=1
    )
    async def prefix_back(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Requiring everyone to use prefixes again", view=None)
        interaction.client.prefixless = False

        await interaction.followup.send(
            content="Alright Boss, I now made the bot require a prefix for everyone.", ephemeral=True
        )

    @discord.ui.button(label="Cancel the Command", style=discord.ButtonStyle.success, emoji="❌", row=2)
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
    async def rerun(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(view=None)
        self.view.message = await interaction.followup.send(
            content=self.view.content, embed=self.view.embed, ephemeral=True, view=self.view, wait=True
        )

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.success, emoji="🔒")
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):

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
        await interaction.response.defer(ephemeral=False)
        assert self.view is not None
        self.view.clear_items()
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

        view.__init__(view.ctx)
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
        self.view.clear_items()
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

        view.__init__(view.ctx)
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

        if random.random() < 0.167:
            self.add_item(RpsGameButtonGun("Gun", "🔫", "4"))

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
    if "e" in result:
        result = result.split("e")[0]
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
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = True

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="❌", custom_id="Deny")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):

        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="<:click:264897397337882624>", row=1)
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
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
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
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
                label="Message:",
                placeholder="Please Put Your Message Here:",
                style=discord.TextStyle.paragraph,
                min_length=3,
                max_length=60,
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.children[0].value
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        response = await self.view.ask(args, self.view.ctx.author.id)
        await self.view.message.edit(f"{response}", view=self.view)

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run chatbot again.", view=self.view)


class ChatBotModal2(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Message:",
                placeholder="Please Put Your Message Here:",
                style=discord.TextStyle.paragraph,
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.children[0].value
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        response = await self.view.ask(args, self.view.ctx.author.id)
        await self.view.message.edit(f"{response}", view=self.view)

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
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChatBotModal(self, title="ChatBot:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Submit 2", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit_alt(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChatBotModal2(self, title="ChatBot:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.success, emoji="❌")
    async def Close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Closing ChatBot", view=None)


class ReportModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Report Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run report again.", view=self.view)
        self.stop()


class ReportView(discord.ui.View):
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
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReportModal(self, title="Report:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.children[0].value
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AddBotModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)
        self.add_item(
            discord.ui.TextInput(
                label="Addbot Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run addbot again.", view=self.view)
        self.stop()


class AddBotView(discord.ui.View):
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
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddBotModal(self, title="Reason:", timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.children[0].value
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AceModal(discord.ui.Modal):
    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

        default = f"{self.view.ctx.author}"
        self.add_item(
            discord.ui.TextInput(label="Name:", default=default, placeholder=default, style=discord.TextStyle.short)
        )
        self.add_item(discord.ui.TextInput(label="Text:", style=discord.TextStyle.paragraph, max_length=240))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.message.delete()
        name = self.children[0].value
        text = self.children[1].value
        buf = await self.view.jeyy_client.ace(name, self.side, text)
        buf.seek(0)
        file = discord.File(buf, "out.gif")
        await self.view.ctx.message.reply(
            content="Take That! (Thank you Jeyy for providing your api):",
            file=file,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run ace again.", view=self.view)


class AceView(discord.ui.View):
    def __init__(self, ctx, jeyy_client, **kwargs):
        self.ctx = ctx
        self.jeyy_client = jeyy_client
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

    @discord.ui.button(label="Attorney", style=discord.ButtonStyle.success, emoji="<a:think:626236311539286016>")
    async def Attorney(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AceModal(self, title="Attorney Text:", timeout=180.0)
        modal.side = button.label.lower()
        await interaction.response.send_modal(modal)
        self.stop()

    @discord.ui.button(
        label="Prosecutor", style=discord.ButtonStyle.danger, emoji="<a:edgeworthZoom:703531746699903046>"
    )
    async def Prosecutor(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AceModal(self, title="Prosecutor Text:", timeout=180.0)
        modal.side = button.label.lower()
        await interaction.response.send_modal(modal)
        self.stop()
