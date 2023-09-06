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
import functools
import os
import time
import traceback

import discord
from discord.ext import commands


class Ticket(commands.Cog):
    "Ticket Stuff"

    def __init__(self, bot: JDBot):
        self.bot = bot
        self.pool: Pool = self.bot.db
        self.ticket_cache: dict[int, TicketCacheData] = {}
        self.main_channel: discord.TextChannel = None  # filled in create_ticket
        self.support_role: discord.Role = None  # filled in create_ticket
        self.support_guild: discord.Guild = None  # filled in create_ticket
        self.please_help: discord.Role = None  # filled in create_ticket

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
            await context.send("Your ticket was sucessfully closed!")
            await self.thread_webhook.send("The user closed the ticket.", thread=remote, username="Ticket Manager")

        else:
            if not context.channel.id in self.ticket_cache:
                return await context.send("This is not a ticket channel.")
            cache = self.ticket_cache[context.channel.id]
            author = self.bot.get_user(cache["author"])
            remote = self.bot.get_channel(cache["remote"])

            await context.send("The ticket was sucessfully closed!")
            await author.send("The Support Team has closed your ticket.")

        # add a couple more checks here to see if the author is the one who ran it.
        # with general checks about requiring the author to run it or the support team.

        if not self.support_guild:
            self.support_guild = self.bot.get_guild(1019027330779332660)

        guild = self.support_guild

        role = guild.get_role(1147198431811600444)

        member = guild.get_member(context.author.id)

        if not member:

            try:
                await remote.remove_user(member)
                await member.remove_roles(role)

            except:
                await context.send("Removing you from the ticket channel failed.")
                traceback.print_exc()

        del self.ticket_cache[remote.id]
        del self.ticket_cache[context.author.id]
        await self.pool.execute(
            "DELETE FROM TICKETS WHERE author_id = $1 AND remote_id = $2", context.author.id, remote.id
        )

        await remote.edit(archived=True, reason="Thread closed")

    @commands.command(brief="Creates a ticket for support", aliases=["ticket_make", "ticket"])
    @commands.dm_only()
    async def create_ticket(self, context: JDBotContext, *, starter_message: Optional[str] = None):
        if not self.main_channel:
            self.main_channel = self.bot.get_channel(1147198182493794304)
            self.support_role = self.bot.get_guild(1019027330779332660).get_role(1042608916233736192)
            self.support_guild = self.bot.get_guild(1019027330779332660)
            self.please_help = self.bot.get_guild(1019027330779332660).get_role(1147198431811600444)

        if context.author.id in self.ticket_cache:
            return await context.send("You cannot create another ticket whilst another ticket is unresponded to.")
        ticket_channel = self.main_channel
        thread_channel = await ticket_channel.create_thread(
            name=f"User {context.author} - {context.author.id}",
            type=discord.ChannelType.private_thread,
            reason="Support Request",
            invitable=False,
        )
        await self.handle_ticket_db_side(context.author.id, thread_channel.id)

        if not starter_message:
            starter_message = "This user requested help, but without a reason."
            # placeholder for now will use modals later

        message = await self.thread_webhook.send(
            f"{starter_message}",
            thread=thread_channel,
            username=f"{context.author}",
            avatar_url=context.author.display_avatar.url,
            wait=True,
        )

        # a bit longer but should work well

        message = await thread_channel.fetch_message(message.id)

        await message.pin(reason="Makes it easier to find the starter message.")

        await context.send("Created, now you can keep sending messages here to send it to remote channel.")

        guild = self.support_guild

        member = guild.get_member(context.author.id)

        if member:
            support_receivers = self.please_help

            if not support_receivers in member.roles:
                await member.add_roles(support_receivers)

            await thread_channel.add_user(member)

            await context.send(f"You have been added to {thread_channel.mention}")

        await self.contact_webhook.send(f"<@168422909482762240> New support ticket \n{thread_channel.mention}.")

    @create_ticket.error
    async def create_ticker_error(self, context: JDBotContext, exception: Exception):
        error = getattr(exception, "original", exception)

        if isinstance(error, commands.PrivateMessageOnly):
            return await context.send("You have to run this command in DM.")
        else:
            await context.send(error)
            traceback.print_exc()

    @functools.cached_property
    def thread_webhook(self) -> discord.Webhook:
        webhook_url = os.environ["thread_webhook"]
        return discord.Webhook.from_url(webhook_url, session=self.bot.session)

    @functools.cached_property
    def contact_webhook(self) -> discord.Webhook:
        webhook_url = os.environ["support_webhook"]
        return discord.Webhook.from_url(webhook_url, session=self.bot.session)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not self.main_channel:
            self.main_channel = self.bot.get_channel(1147198182493794304)
            self.support_role = self.bot.get_guild(1019027330779332660).get_role(1042608916233736192)
            self.support_guild = self.bot.get_guild(1019027330779332660)

        context = await self.bot.get_context(message)

        if isinstance(message.channel, discord.DMChannel):
            if context.prefix is None or self.bot.user.mentioned_in(message):
                if message.author.id != self.bot.user.id and context.valid is False:
                    if not message.author.id in self.ticket_cache:
                        await message.channel.send(
                            "run ``te*help Ticket`` to learn more. For now Contact our Developers: silentserenity or jdjg"
                        )

                    else:
                        await message.add_reaction("<:bigger_yes_emoji:917747437400125470>")

        if context.prefix is None or self.bot.user.mentioned_in(message):
            if message.author.id != self.bot.user.id and context.valid is False:
                if (
                    message.guild
                    and message.guild.id == 1019027330779332660
                    and message.channel.id in self.ticket_cache
                ):
                    author = self.ticket_cache[message.channel.id]["author"]
                    author = self.bot.get_user(author)

                    if self.support_role not in message.author.roles and author != message.author:
                        return await message.reply(
                            "<a:yangsmh:800522615235805204> Sorry you can't use this as you aren't a support team member."
                        )

                    if message.author == author and not self.support_role in message.author.roles:
                        return
                        # don't need to respond then

                    await author.send(f"`{message.author}:` {message.content}")
                    # respond normally if they aren't in the thread.

                elif not message.guild and message.author.id in self.ticket_cache:
                    thread = self.ticket_cache[message.author.id]["remote"]
                    thread = self.bot.get_channel(thread)

                    await self.thread_webhook.send(
                        f"{message.content}",
                        thread=thread,
                        username=f"{message.author}",
                        avatar_url=message.author.display_avatar.url,
                    )


async def setup(bot: JDBot):
    await bot.add_cog(Ticket(bot))
