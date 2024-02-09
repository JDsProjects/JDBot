from typing import Any, Sequence

import discord
from discord.ext import commands
from discord.ext.paginators import button_paginator


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
        ctx: commands.Context[Any] | None = None,
        interaction: discord.Interaction | None = None,
        author_id: int | None = None,
        timeout: float | int = 180.0,
        always_show_stop_button: bool = False,
        delete_after: bool = False,
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

        self.ctx: commands.Context[Any] | None = ctx
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
            **kwargs,
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
            **send_kwargs,
        )