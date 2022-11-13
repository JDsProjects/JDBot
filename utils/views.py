from __future__ import annotations

import asyncio
import collections
import random
import traceback
import typing
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence, Union

import discord
import mathjspy
from discord import ButtonStyle, Embed, File, Interaction
from discord.abc import Messageable
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.flags import UserFlags
from discord.ui import Button, Modal, TextInput, View
from discord.utils import MISSING, maybe_coroutine

if TYPE_CHECKING:
    from .emoji import CustomEmoji

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
            if button.custom_id in ("page_indicator_button", "stop_button"):
                if button.custom_id == "page_indicator_button":
                    button.label = self.page_string
                else:
                    button.style = ButtonStyle.red
                continue

            elif button.custom_id in ("right_button", "last_button"):
                button.disabled = self._current_page >= self.max_pages - 1
            elif button.custom_id in ("left_button", "first_button"):
                button.disabled = self._current_page <= 0

            if not button.disabled:
                button.style = ButtonStyle.green
            elif button.disabled:
                button.style = ButtonStyle.secondary

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

        kwargs["attachments"] = kwargs.pop("files", [])
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
                if not "|" in page.footer.text:
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
                self.message = await self.interaction.original_response()  # type: ignore
                return self.message

        elif self.ctx is not MISSING:
            self.message = await self.ctx.send(**send_kwargs)  # type: ignore
            return self.message

        else:
            raise ValueError("ctx or interaction or send_to must be provided")


# thank you so much Soheab for allowing me to use this paginator you made and putting in the work to do this :D (That's his github name so...)


class TweetEmbed(Paginator):
    async def format_page(self, item) -> discord.Embed:

        tweet_url = f"https://twitter.com/twitter/statuses/{item.id}"

        embed = discord.Embed(
            title=f"Tweet!", description=f"{item.text}", url=tweet_url, color=0x1DA1F2, timestamp=item.created_at
        )
        embed.set_author(name=f"{self.username.data}", icon_url=self.image, url=self.profile_url)
        embed.set_footer(text=f"Requested by {self.ctx.author}\nJDJG does not own any of the content of the tweets")

        embed.set_thumbnail(url="https://i.imgur.com/zpLkfHo.png")

        return embed


class EmojiInfoEmbed(Paginator):
    async def format_page(self, item: typing.Union[str, CustomEmoji]) -> discord.Embed:
        DEFAULT_COLOUR = random.randint(0, 16777215)

        invalid_emoji_embed = discord.Embed(
            title="Invalid Emoji",
            description=f"The following input could not be resolved to a valid emoji: `{item}`",
            colour=DEFAULT_COLOUR,
        )
        # bail early if the emoji is invalid
        if isinstance(item, str):
            return invalid_emoji_embed

        emoji_type = "Custom Emoji" if not item.unicode else "Default Emoji"
        emoji_url = item.url if not item.unicode else f"https://emojiterra.com/{item.name.lower().replace(' ', '-')}/"
        field_name = "Emoji Info" if not item.unicode else "Unicode Info"

        main_embed = discord.Embed(
            title=f'Emoji Info for "{item.emoji}" ({emoji_type})',
            colour=DEFAULT_COLOUR,
        )
        main_embed.set_image(url=item.url)

        global_text = (f"**Name:** {item.name}", f"**ID:** {item.id}", f"**URL:** [click here]({emoji_url})")
        if item.unicode:
            # provide different styles because why not
            # twitter == twemoji
            styles = [
                f"[{style}]({item.with_style(style).url})"
                for style in ("twitter", "whatsapp", "apple", "google", "samsung")
            ]
            styles_text = "Styles: see how this emoji looks on different platforms: " + " | ".join(styles)
            global_text += (f"**Code:** {item.unicode}", styles_text)

        else:
            global_text += (
                f"**Created:** {item.created_at}",
                f"**Animated:** {item.animated}",
            )

        main_embed.add_field(
            name=field_name,
            value="\n".join(global_text),
        )

        return main_embed


class MutualGuildsEmbed(Paginator):
    def format_page(self, item):
        embed = discord.Embed(title="Mutual Servers:", description=item, color=random.randint(0, 16777215))

        return embed


class cdnViewer(Paginator):
    def format_page(self, item):
        embed = discord.Embed(title="CDN Viewer", description=f"Image ID: {item}", color=random.randint(0, 16777215))
        embed.set_image(url=f"https://cdn.jdjgbot.com/image/{item}.gif?opengraph_pass=true")

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
            name=f"User ID : {item}", value=f"**Reason :** {self.ctx.bot.sus_users.get(item)}", inline=False
        )
        return embed


class BlacklistedUsersEmbed(Paginator):
    async def format_page(self, item):
        embed = discord.Embed(title="Users Blacklisted by JDJG Inc. Official", color=random.randint(0, 16777215))
        embed.add_field(
            name=f"User ID : {item}", value=f"**Reason :** {self.ctx.bot.blacklisted_users.get(item)}", inline=False
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


class HelpEmbed(discord.Embed):
    def __init__(self, ctx, *args, **kwargs):
        super().__init__(title=f"{ctx.bot.user} Help Menu", *args, **kwargs)
        self.set_author(name=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)


class SendHelp(Paginator):
    async def format_page(self, item):
        emby = HelpEmbed(self.ctx, description=item, color=15428885)
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


class ScanStatusEmbed(Paginator):
    async def format_page(self, item):
        ctx = self.ctx
        embed = discord.Embed(title="Status Scan Complete!", description=item, color=15428885)
        embed.set_author(name=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
        return embed


def guild_join(guilds):
    return "\n".join(map(str, guilds))


def grab_mutualguilds(ctx, user):

    if isinstance(user, discord.ClientUser):
        return ctx.author.mutual_guilds

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

    @discord.ui.button(label="Ephemeral", style=discord.ButtonStyle.success, emoji="🕵️")
    async def secretMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="Will be sending you the information, ephemerally", view=self)

        await self.menu.send(interaction=interaction, ephemeral=True)

    @discord.ui.button(label="Direct", style=discord.ButtonStyle.success, emoji="📥")
    async def dmMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="Well be Dming you the paginator to view this info", view=self)

        await self.menu.send(send_to=self.channel)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️")
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

    async def on_timeout(self):
        await self.message.edit(content="You took too long to respond, so I cancelled the paginator", view=None)


class TweetHandler(discord.ui.View):
    def __init__(self, ctx, menu=None, channel: discord.DMChannel = None, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.channel = channel
        self.menu = menu

    @discord.ui.button(label="Normal", style=discord.ButtonStyle.success, emoji="📄")
    async def NormalMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.menu.message = interaction.message
        page = self.menu.get_page(0)
        kwargs = await self.menu.get_kwargs_from_page(page)
        await self.menu._edit_message(interaction, **kwargs)

    @discord.ui.button(label="Ephemeral", style=discord.ButtonStyle.success, emoji="🕵️")
    async def secretMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="ephemerally sending Tweets", view=self)

        await self.menu.send(interaction=interaction, ephemeral=True)

    @discord.ui.button(label="Direct", style=discord.ButtonStyle.success, emoji="📥")
    async def dmMessage(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content="Dming Tweets", view=self)

        await self.menu.send(send_to=self.channel)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="✖️")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.clear_items()
        await self.message.edit(content=f"I will not send you the tweets", view=self)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        await self.message.edit(content="You took too long to respond, so I cancelled the paginator", view=None)


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

            await self.view.message.edit(content="Will be sending you the information, ephemerally", view=self.view)

            await menu.send(interaction=interaction, ephemeral=True)

        if self.custom_id == "1":

            await interaction.response.edit_message(
                content=f"Well be Dming you the paginator to view this info", view=self.view
            )

            if self.view.ctx.author.dm_channel is None:
                await self.view.ctx.author.create_dm()

            await menu.send(send_to=self.view.ctx.author.dm_channel)

        if self.custom_id == "2":

            await interaction.response.edit_message(content=f"not sending the paginator to you", view=self.view)


def profile_converter(
    _type: typing.Literal["badges", "mobile", "status", "web", "desktop", "mobile", "activity"],
    _enum: typing.Union[discord.Status, discord.UserFlags, discord.BaseActivity, str],
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
        discord.Activity: "🏃",
        discord.Streaming: "<:streaming:917747437920219156>",
        discord.Spotify: "<:spotify:1041484515748618343>",
        discord.Game: "🎮",
        discord.CustomActivity: "🎨",
    }

    dc = {"status": status_emojis, "badges": badges_emoji, "devices": devices_emojis, "activity": activity_emojis}
    is_devices = False
    if _type in ("mobile", "desktop", "web"):
        is_devices = True

    dict_to_use = dc.get(_type) if not is_devices else dc["devices"][_type]
    emoji = dict_to_use.get(_enum)
    if not emoji:
        emoji = status_emojis[_enum]
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

    activities = [profile_converter("activities", activity) for activity in user.activities] if user.activities else []
    return activities


class UserInfoSuperSelects(discord.ui.Select):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.banner = None
        self.banner_fetched = False

        options = [
            discord.SelectOption(label="Basic Info", description="Simple Info", value="basic", emoji="📝"),
            discord.SelectOption(label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"),
            discord.SelectOption(label="Badges", description="Show's the badges they have", value="badges", emoji="📛"),
            discord.SelectOption(
                label="Avatar",
                description="Shows user's profile picture in large thumbnail.",
                emoji="🖼️",
                value="avatar",
            ),
            discord.SelectOption(
                label="status", description="Shows user's current status.", emoji="🖼️", value="status"
            ),
            discord.SelectOption(
                label="Activies", description="Shows user's current Activies.", emoji="🏃", value="activities"
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
                activities = activity_collect(user)

        join_statuses = (
            " \n| ".join(f"**{name}**: {value}" for name, value in statuses) if statuses else "**Status**: \nUnknown"
        )

        join_activities = (
            "\n | ".join(f"**{name}**" for name in activities) if activities else "**Activity**: \nUnknown"
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
            embed.add_field(name="f{join_activities}", value="\u2800", inline=False)

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
            discord.SelectOption(label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"),
            discord.SelectOption(label="Badges", description="Show's the badges they have", value="badges", emoji="📛"),
            discord.SelectOption(
                label="Avatar",
                description="Shows Owner's profile picture in large thumbnail.",
                emoji="🖼️",
                value="avatar",
            ),
            discord.SelectOption(
                label="status", description="Shows Owner's current status.", emoji="🖼️", value="status"
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
            discord.SelectOption(label="Misc Info", description="Shows even more simple info", value="misc", emoji="📝"),
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


class TokenInvalidatorSettings(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    @discord.ui.button(label="DM ☑️", style=discord.ButtonStyle.success, emoji="📩", row=0)
    async def dm_switch(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="DM Invalidation On", view=None, embed=None)

    @discord.ui.button(label="Global ☑️", style=discord.ButtonStyle.success, emoji="<:_:411642484528119810>", row=0)
    async def global_switch(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Global Token Invalidator", view=None, embed=None)

    @discord.ui.button(label="Guild ☑️", style=discord.ButtonStyle.success, emoji="<a:_:803876680166408192> ", row=0)
    async def guild_switch(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Guild Token Invalidator", view=None, embed=None)

    @discord.ui.button(label="Channel ☑️", style=discord.ButtonStyle.success, emoji="<a:_:803876680166408192> ", row=0)
    async def channel_switch(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Channel Token Invalidator", view=None, embed=None)

    async def interaction_check(self, interaction: discord.Interaction):

        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.view.message.edit(content="May want to start from the top", view=self)


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
        super().__init__(label=f"{label}", row=row, style=style)
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
class CodeBlockModal(discord.ui.Modal, title="Pep8 Project Formatter:"):
    code = discord.ui.TextInput(
        label="Code Block:", placeholder="Please Put your code here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

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

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="✖️", custom_id="Deny")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):

        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="<:click:264897397337882624>", row=1)
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CodeBlockModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.code
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class MailModal(discord.ui.Modal, title="Mail:"):
    message = discord.ui.TextInput(
        label="Message:", placeholder="Please Put Your Message Here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

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
        modal = MailModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.message
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class ChatBotModal(discord.ui.Modal, title="ChatBot(Travitia API):"):
    args = discord.ui.TextInput(
        label="Message:",
        placeholder="Please Put Your Message Here:",
        style=discord.TextStyle.paragraph,
        min_length=3,
        max_length=60,
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.args
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        response = await self.view.ask(args, self.view.ctx.author.id)
        await self.view.message.edit(content=f"{response}", view=self.view)

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run chatbot again.", view=self.view)


class ChatBotModal2(discord.ui.Modal, title="ChatBot (Some Random Api):"):
    args = discord.ui.TextInput(
        label="Message:",
        placeholder="Please Put Your Message Here:",
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.args
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        # response = await self.view.ask2(args)
        # await self.view.message.edit(content=f"{response}", view=self.view)

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
        modal = ChatBotModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Submit 2", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit_alt(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChatBotModal2(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.success, emoji="✖️")
    async def Close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(content="Closing ChatBot", view=None)


class ReportModal(discord.ui.Modal, title="Report:"):
    report = discord.ui.TextInput(
        label="Report Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

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
        modal = ReportModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.report
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AddBotModal(discord.ui.Modal, title="Reason:"):
    reason = discord.ui.TextInput(
        label="Addbot Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

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
        modal = AddBotModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.reason
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AceModal(discord.ui.Modal):
    name = discord.ui.TextInput(label="Name", style=discord.TextStyle.short)
    text = discord.ui.TextInput(label="Text", style=discord.TextStyle.paragraph, max_length=240)

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

        default = f"{self.view.ctx.author}"
        self.name.default = default
        self.name.placeholder = default

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.message.delete()
        name = self.name
        text = self.text
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
