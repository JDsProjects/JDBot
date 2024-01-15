from __future__ import annotations
import random
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union

import discord
from discord.ext.paginators import button_paginator

from tweepy.models import Media

from .views import HelpEmbed, grab_mutualguilds, guild_join, get_sus_reason
from .tweet import TweepyTweet

if TYPE_CHECKING:
    from .emoji import CustomEmoji

    from discord.ext import commands
    Context = commands.Context

__all__ = (
    "Paginator",
    "EmojiInfoEmbed",
    "MutualGuildsEmbed",
    "cdnViewer",
    "ServersEmbed",
    "PrefixesEmbed",
    "LeaderboardEmbed",
    "RandomHistoryEmbed",
    "TestersEmbed",
    "SusUsersEmbed",
    "BlacklistedUsersEmbed",
    "ErrorEmbed",
    "RtfmEmbed",
    "SendHelp",
    "charinfoMenu",
    "InviteInfoEmbed",
    "GoogleEmbed",
    "ScanStatusEmbed",
    "ScanGlobalEmbed",
    "TodoEmbed",
    "TweetsPaginator",
)


DEFAULT_BUTTONS = {
    "FIRST": button_paginator.PaginatorButton(emoji="⏮️", position=0, style=discord.ButtonStyle.secondary),
    "LEFT": button_paginator.PaginatorButton(emoji="◀️", position=1, style=discord.ButtonStyle.secondary),
    "PAGE_INDICATOR": None,
    "STOP": button_paginator.PaginatorButton(emoji="⏹️", position=2, style=discord.ButtonStyle.danger),
    "RIGHT": button_paginator.PaginatorButton(emoji="▶️", position=3, style=discord.ButtonStyle.secondary),
    "LAST": button_paginator.PaginatorButton(emoji="⏭️", position=4, style=discord.ButtonStyle.secondary),
}

class Paginator(button_paginator.ButtonPaginator):
    def __init__(
        self,
        pages: Sequence[Any],
        *,
        ctx: Context[Any] | None = None,
        interaction: discord.Interaction | None = None,
        author_id: int | None = None,
        timeout: float | int = 180.0,
        always_show_stop_button: bool = False,
        delete_after:bool = False,
        disable_after: bool = False,
        clear_buttons_after: bool = False,
        per_page: int = 1,
        **kwargs: Any,
    ) -> None:
        _author_id = None
        if ctx is not None:
            _author_id = ctx.author.id
        elif interaction is not None:
            _author_id = interaction.user.id
        elif author_id is None:
            _author_id = author_id

        self.ctx: Context[Any] | None = ctx
        self.interaction: discord.Interaction | None = interaction

        kwargs["buttons"] = kwargs.get("buttons", DEFAULT_BUTTONS)
        super().__init__(
            pages,
            author_id=_author_id,
            timeout=timeout,
            always_show_stop_button=always_show_stop_button,
            delete_after=delete_after,
            disable_after=disable_after,
            clear_buttons_after=clear_buttons_after,
            per_page=per_page,
            **kwargs
        )

    @property
    def author(self) -> discord.User | discord.Member | None:
        if self.ctx is not None:
            return self.ctx.author
        elif self.interaction is not None:
            return self.interaction.user
        else:
            return None

    async def send(
        self,
        destination: discord.abc.Messageable | discord.Interaction[Any] | None = None,
        *,
        override_page_kwargs: bool = False,
        edit_message: bool = False,
        **send_kwargs: Any,
    ) -> Optional[discord.Message]:
        destination = destination or self.ctx or self.interaction
        if destination is None:
            raise TypeError("destination is None")
        
        return await super().send(  # type: ignore
            destination,
            override_page_kwargs=override_page_kwargs,  # type: ignore
            edit_message=edit_message,
            **send_kwargs
        )  


class EmojiInfoEmbed(Paginator):
    async def format_page(self, item: str | CustomEmoji) -> discord.Embed:
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
                f"**Created:** {discord.utils.format_dt(item.created_at, 'R') if item.created_at else 'Unknown'}",
                f"**Animated:** {item.animated}",
            )

        main_embed.add_field(
            name=field_name,
            value="\n".join(global_text),
        )

        return main_embed
    
class MutualGuildsEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Mutual Servers:", description=item, color=random.randint(0, 16777215))
        return embed


class cdnViewer(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="CDN Viewer", description=f"Image ID: {item}", color=random.randint(0, 16777215))
        embed.set_image(url=f"https://cdn.jdjgbot.com/image/{item}.gif?opengraph_pass=true")

        return embed


class ServersEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Servers:", description=item, color=random.randint(0, 16777215))
        return embed


class PrefixesEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Usable Prefixes:", description=item, color=random.randint(0, 16777215))
        return embed


class LeaderboardEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        emby = discord.Embed(title="Leaderboard", color=15428885)
        if self.author:
            emby.set_author(
                name=f"Leaderboard Requested by {self.author}", icon_url=self.author.display_avatar.url,
            )

        for i, b, w in item:
            emby.add_field(
                name=f"**${i}:**", value=f"```yaml\nBank: ${b:,}\nWallet: ${w:,}\nTotal: ${b+w:,}```", inline=False
            )

        return emby


class RandomHistoryEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Random History:", description=f"{item}", color=random.randint(0, 16777215))
        embed.set_footer(text="Powered by Random quotes From: \nhttps://www.youtube.com/watch?v=xuCn8ux2gbs")
        return embed


class TestersEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Testing Users:", color=random.randint(0, 16777215))
        embed.add_field(name="User ID:", value=f"{item}", inline=False)

        return embed


class SusUsersEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Users Deemed Suspicious by JDJG Inc. Official", color=random.randint(0, 16777215))
        embed.add_field(
            name=f"User ID : {item}", value=f"**Reason :** {self.ctx.bot.sus_users.get(item)}", inline=False
        )
        return embed


class BlacklistedUsersEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Users Blacklisted by JDJG Inc. Official", color=random.randint(0, 16777215))
        embed.add_field(
            name=f"User ID : {item}", value=f"**Reason :** {self.ctx.bot.blacklisted_users.get(item)}", inline=False
        )
        return embed


class ErrorEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        item = discord.utils.escape_markdown(item, as_needed=False, ignore_links=True)
        return discord.Embed(title="Error", description=item, color=random.randint(0, 16777215))


class RtfmEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Packages:", description=item, color=random.randint(0, 16777215))
        return embed


class SendHelp(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        emby = HelpEmbed(self.ctx, description=item, color=15428885)
        return emby


class charinfoMenu(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        return discord.Embed(description=item, color=random.randint(0, 16777215))


class InviteInfoEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
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
            embed.set_footer(text="If this is a consistent problem please contact JDJG Inc. Official#3493 (jdjg)")

        return embed


class GoogleEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
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
    def format_page(self, item: str) -> discord.Embed:
        embed = discord.Embed(title="Status Scan Complete!", description=item, color=15428885)
        if self.author:
            embed.set_author(name=f"Requested by {self.author}", icon_url=self.author.display_avatar.url)
        return embed


class ScanGlobalEmbed(Paginator):
    async def format_page(self, item: discord.User | discord.Member ) -> discord.Embed:
        embed = discord.Embed(color=random.randint(0, 16777215))

        embed.set_author(name=f"{item}", icon_url=item.display_avatar.url)

        embed.add_field(name="Shared Guilds:", value=f"{guild_join(grab_mutualguilds(self.ctx, item))}")
        embed.set_footer(text=f"Sus Reason : {await get_sus_reason(self.ctx, item)}")
        return embed


class TodoEmbed(Paginator):
    def format_page(self, item: str) -> discord.Embed:
        if self.ctx:
            embed = discord.Embed(
                description=item, color=random.randint(0, 16777215), timestamp=self.ctx.message.created_at
            )

            embed.set_author(name=f"Todo Requested By {self.ctx.author}:", icon_url=self.ctx.author.display_avatar.url)
            return embed

        raise TypeError("self.ctx is None")


class TweetsPaginator(Paginator):
    class ShowImagesButton(discord.ui.Button):
        view: "TweetsPaginator"

        def __init__(self) -> None:
            super().__init__(label="Show Images")
            self.position: int = 4
            self.medias: list[Media] = []

        async def callback(self, interaction: discord.Interaction[Any]) -> None:
            pag = Paginator(
                ctx=self.view.ctx,
                pages=self.medias,  # type: ignore
                delete_after=self.view.delete_after,
                always_show_stop_button=True,
            )
            pag.format_page = self.view.media_page_formater  # type: ignore
            if not self.view.ctx:
                raise TypeError("self.ctx is None")

            await pag.send(self.view.ctx)

    def __init__(
        self,
        *,
        ctx: commands.Context,
        tweets: TweepyTweet,
        delete_after: bool = False,
        author_name: str,
        author_url: str,
        author_icon: str,
        **kwargs,
    ):
        self.media_button = self.ShowImagesButton()
        super().__init__(ctx=ctx, pages=tweets, delete_after=delete_after, **kwargs)  # type: ignore
        self.add_item(self.media_button)
        self.author_name: str = author_name
        self.author_url: str = author_url
        self.author_icon: str = author_icon
        self._update_buttons_state()

    def media_page_formater(self, media: Media) -> discord.Embed:
        embed = discord.Embed(title=f"Images", description=f"url: {media.url}", color=0x1DA1F2)
        embed.set_image(url=media.url)
        return embed

    def format_page(self, item: TweepyTweet) -> discord.Embed:
        tweet_url = f"https://twitter.com/twitter/statuses/{item.id}"

        embed = discord.Embed(
            title=f"Tweet!", description=f"{item.text}", url=tweet_url, color=0x1DA1F2, timestamp=item.created_at
        )
        embed.set_author(name=self.author_name, url=self.author_url, icon_url=self.author_icon)
        embed.set_footer(text=f"Requested by {self.ctx.author}\nJDJG does not own any of the content of the tweets")

        embed.set_thumbnail(url="https://i.imgur.com/zpLkfHo.png")

        return embed

    def _update_buttons_state(self) -> None:
        current_page = self.get_page(self.current_page)
        self.media_button.medias = [x for x in current_page.media if x.url]  # type: ignore
        self.media_button.disabled = not self.media_button.medias  # type: ignore
        super()._update_buttons_state()