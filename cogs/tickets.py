from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol, TypedDict

import utils

if TYPE_CHECKING:
    from asyncpg import Pool

    from ..main import JDBot, JDBotContext

    class RecordType(Protocol):
        def get(self, key: str) -> Any:
            ...

    class TicketType(TypedDict):
        author: discord.User
        remote: int
        timestamp: datetime.datetime


import datetime
import time
import traceback
from dataclasses import dataclass

import discord
from discord.ext import commands


@dataclass
class Ticket:
    author: int
    remote: int
    timestamp: datetime.datetime


class TicketCog(commands.Cog, name="Ticket"):
    def __init__(self, bot: JDBot):
        self.bot = bot
        self.pool: Optional[Pool] = self.bot.db
        self.ticket_cache: Dict[int, Ticket] = {}
        self.main_channel: Optional[
            discord.TextChannel
        ] = None  # filled in create_ticket
        self.support_role: Optional[discord.Role] = None  # filled in create_ticket

    async def cog_load(self):
        pool = self.pool

        records: list[RecordType] = await pool.fetch("SELECT * FROM TICKETS")
        now = discord.utils.utcnow()
        for record in records:
            author: int = record.get("author_id")
            remote: int = record.get("remote_id")
            end_timestamp: int = (record.get("end_timestamp")) / 1000

            end_timestamp = datetime.datetime.fromtimestamp(
                end_timestamp, tz=datetime.timezone.utc
            )  # type: ignore
            if now > end_timestamp:  # type: ignore
                # How did this even exist in first place ?
                await pool.execute(
                    "DELETE FROM TICKETS WHERE author_id = $1 AND remote_id = $2",
                    author,
                    remote,
                )
                continue
            self.ticket_cache[author] = self.ticket_cache[remote] = Ticket(
                author, remote, end_timestamp  # type: ignore
            )

    async def handle_ticket_db_side(self, author_id: int, remote_id: int):
        timestamp = discord.utils.utcnow()
        timestamp = timestamp + datetime.timedelta(4)
        self.ticket_cache[author_id] = self.ticket_cache[remote_id] = Ticket(
            author_id, remote_id, end_timestamp  # type: ignore
        )
        unix = timestamp.timetuple()
        unix = time.mktime(unix) * 1000
        await self.pool.execute(
            "INSERT INTO TICKETS VALUES ($1, $2, $3)", author_id, remote_id, unix
        )

    @commands.command(brief="Closes support ticket.")
    async def close(self, context: JDBotContext):
        if not context.guild:
            if context.author.id not in self.ticket_cache:
                return await context.send("You did not create any tickets.")
            remote = self.ticket_cache[context.author.id].remote
            remote_channel = await self.bot.try_channel(remote)
            await remote_channel.send("The user closed the ticket.")

        else:
            if not context.channel.id in self.ticket_cache:
                return await context.send("This is not ticket channel.")
            ticket = self.ticket_cache[context.channel.id]
            author = ticket.author
            remote = ticket.remote
            author = await self.bot.try_user(author)
            await author.send("Support team has closed your ticket.")

        del self.ticket_cache[remote]
        del self.ticket_cache[context.author.id]
        await self.pool.execute(
            "DELETE FROM TICKETS WHERE author_id = $1 AND remote_id = $2",
            context.author.id,
            remote,
        )

    @commands.command(
        brief="creates a ticket for support", aliases=["ticket_make", "ticket"]
    )
    @commands.dm_only()
    async def create_ticket(
        self, context: JDBotContext, *, starter_message: Optional[str] = None
    ):
        if context.author.id in self.ticket_cache:
            return await context.send(
                "You cannot create another ticket while a ticket is not responded."
            )
        ticket_channel = self.main_channel
        thread_channel = await ticket_channel.create_thread(
            name=f"User {context.author} - {context.author.id}",
            type=discord.ChannelType.public_thread,
            reason="Support Request",
        )
        await self.handle_ticket_db_side(context.author.id, thread_channel.id)

        if not starter_message:
            starter_message = (
                "Hello i need help, i Haven't provided a reason quite yet."
            )
            modal = utils.ReportView(context, timeout=180.0)
            message = await context.send(
                "Please Submit your Reason Here(if you don't respond with in 3 minutes, it will use a default):",
                view=modal,
            )
            await modal.wait()
            starter_message = modal.value or "I need help, i've provided no reason."

        await thread_channel.send(f"`{context.author}:` {starter_message}")
        await context.send(
            "Created, now you can keep sending messages here to send it to remote channel."
        )
        await ticket_channel.send("<@168422909482762240> New support ticket.")

    @create_ticket.error
    async def create_ticker_error(self, context: JDBotContext, exception: Exception):
        error = getattr(exception, "original", exception)

        if isinstance(error, commands.PrivateMessageOnly):
            return await context.send("You have to run this command in DM.")
        else:
            await context.send(error)
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        context = await self.bot.get_context(message)

        if isinstance(message.channel, discord.DMChannel):
            if context.prefix is None or self.bot.user.mentioned_in(message):
                if message.author.id != self.bot.user.id and context.valid is False:
                    await message.channel.send(
                        "Ticket Support is coming soon. For now Contact our Developers: Shadi#9492 or JDJG Inc. Official#3493"
                    )

        # edit later idk

        if not self.main_channel:
            self.main_channel: Any = self.bot.get_channel(855947100730949683)
            self.support_role = self.bot.get_guild(736422329399246990).get_role(
                855219483295875072
            )

        if (
            message.guild
            and message.guild.id == 736422329399246990
            and message.channel.id in self.ticket_cache
        ):

            if self.support_role not in message.author.roles:
                return await message.reply(
                    "<a:yangsmh:800522615235805204> Sorry you can't use this as you aren't a support team member."
                )

            author = self.ticket_cache[message.channel.id].author
            author = await self.bot.try_user(author)
            await author.send(f"`{message.author}:` {message.content}")

        elif not message.guild and message.author.id in self.ticket_cache:
            thread = self.ticket_cache[message.author.id].remote
            thread = await self.bot.try_channel(thread)
            await thread.send(f"`{message.author}:` {message.content}")


async def setup(bot: JDBot):
    await bot.add_cog(TicketCog(bot))
