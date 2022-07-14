from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Protocol, TypedDict

if TYPE_CHECKING:
    from asyncpg import Pool

    from ..main import JDBot, JDBotContext

    class RecordType(Protocol):
        def get(self, key: str) -> Any:
            ...

    class TicketCacheData(TypedDict):
        author: discord.User
        remote: int
        timestamp: datetime.datetime


import datetime
import time
import traceback

import discord
from discord.ext import commands


class Ticket(commands.Cog):
    def __init__(self, bot: JDBot):
        self.bot = bot
        self.pool: Pool = self.bot.db
        self.ticket_cache: dict[int, TicketCacheData] = {}
        self.main_channel: discord.TextChannel = None  # filled in create_ticket
        self.support_role: discord.Role = None  # filled in create_ticket

    async def cog_load(self):
        pool = self.pool

        records: list[RecordType] = await pool.fetch("SELECT * FROM TICKETS")
        now = discord.utils.utcnow()
        for record in records:
            author: int = record.get("author_id")
            remote: int = record.get("remote_id")
            end_timestamp: int = (record.get("end_timestamp")) / 1000

            end_timestamp = datetime.datetime.fromtimestamp(end_timestamp, tz=datetime.timezone.utc)
            if now > end_timestamp:
                # How did this even exist in first place ?
                await pool.execute("DELETE FROM TICKETS WHERE author_id = $1 AND remote_id = $2", author, remote)
                continue
            self.ticket_cache[author] = self.ticket_cache[remote] = {
                "author": author,
                "remote": remote,
                "timestamp": end_timestamp,
            }

    async def handle_ticket_db_side(self, author_id: int, remote_id: int):
        timestamp = discord.utils.utcnow()
        timestamp = timestamp + datetime.timedelta(4)
        self.ticket_cache[author_id] = self.ticket_cache[remote_id] = {
            "author": author_id,
            "remote": remote_id,
            "timestamp": timestamp,
        }
        unix = timestamp.timetuple()
        unix = time.mktime(unix) * 1000
        await self.pool.execute("INSERT INTO TICKETS VALUES ($1, $2, $3)", author_id, remote_id, unix)

    @commands.command(brief="Closes support ticket.")
    async def close(self, context: JDBotContext):
        if not context.guild:
            if context.author.id not in self.ticket_cache:
                return await context.send("You did not create any tickets.")
            remote = self.ticket_cache[context.author.id]["remote"]
            remote = self.bot.get_channel(remote)
            await remote.send("The user closed the ticket.")

        else:
            if not context.channel.id in self.ticket_cache:
                return await context.send("This is not ticket channel.")
            cache = self.ticket_cache[context.channel.id]
            author = self.bot.get_user(cache["author"])
            remote = self.bot.get_channel(cache["remote"])
            await author.send("Support team has closed your ticket.")

        del self.ticket_cache[remote.id]
        del self.ticket_cache[context.author.id]
        await self.pool.execute(
            "DELETE FROM TICKETS WHERE author_id = $1 AND remote_id = $2", context.author.id, remote.id
        )

    @commands.command(brief="creates a ticket for support", aliases=["ticket_make", "ticket"])
    @commands.dm_only()
    async def create_ticket(self, context: JDBotContext, *, starter_message: Optional[str] = None):
        if not self.main_channel:
            self.main_channel = self.bot.get_channel(996930071359148162)
            self.support_role = self.bot.get_guild(995422814230302821).get_role(855219483295875072)

        if context.author.id in self.ticket_cache:
            return await context.send("You cannot create another ticket while a ticket is not responded.")
        ticket_channel = self.main_channel
        thread_channel = await ticket_channel.create_thread(
            name=f"User {context.author} - {context.author.id}",
            type=discord.ChannelType.public_thread,
            reason="Support Request",
        )
        await self.handle_ticket_db_side(context.author.id, thread_channel.id)

        if not starter_message:
            starter_message = "Hello i need help, i Haven't provided a reason quite yet."
            # place holder for now will use modals later

        await thread_channel.send(f"`{context.author}:` {starter_message}")
        await context.send("Created, now you can keep sending messages here to send it to remote channel.")
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

        if not self.main_channel:
            self.main_channel = self.bot.get_channel(996930071359148162)
            self.support_role = self.bot.get_guild(995422814230302821).get_role(996929816525811863)

        context = await self.bot.get_context(message)

        if isinstance(message.channel, discord.DMChannel):
            if context.prefix is None or self.bot.user.mentioned_in(message):
                if message.author.id != self.bot.user.id and context.valid is False:
                    await message.channel.send(
                        "Ticket Support is coming soon. For now Contact our Developers: Shadi#9492 or JDJG Inc. Official#3493"
                    )

        # edit later idk

        if message.guild and message.guild.id == 995422814230302821 and message.channel.id in self.ticket_cache:

            if self.support_role not in message.author.roles:
                return await message.reply(
                    "<a:yangsmh:800522615235805204> Sorry you can't use this as you aren't a support team member."
                )

            author = self.ticket_cache[message.channel.id]["author"]
            author = self.bot.get_user(author)
            await author.send(f"`{message.author}:` {message.content}")

        elif not message.guild and message.author.id in self.ticket_cache:
            thread = self.ticket_cache[message.author.id]["remote"]
            thread = self.bot.get_channel(thread)
            await thread.send(f"`{message.author}:` {message.content}")


async def setup(bot: JDBot):
    await bot.add_cog(Ticket(bot))
