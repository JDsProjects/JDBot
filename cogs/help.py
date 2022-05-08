import itertools

import discord
from discord.ext import commands

import utils


class JDBotHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        menu = utils.SendHelp(self.paginator.pages, ctx=self.context, delete_after=True)

        await menu.send()

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()

        if note:
            self.paginator.add_line(note, empty=True)

        no_category = f"\u200b{self.no_category}"

        def get_category(command, *, no_category=no_category):
            cog = command.cog
            return f"__**{cog.qualified_name}:**__ \n{cog.description}" if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, Commands in to_iterate:
            self.paginator.add_line(category)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()

    def add_command_formatting(self, command):

        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)

        else:
            self.paginator.add_line(discord.utils.escape_markdown(signature), empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)

            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)

                self.paginator.add_line()

    def add_subcommand_formatting(self, command):
        if len(command.name) < 15:
            empty_space = 15 - len(command.name)
            signature = f"`{command.name}{' '*empty_space}:` {command.short_doc if len(command.short_doc) < 58 else f'{command.short_doc[0:58]}...'}"

        else:
            signature = f"`{command.name[0:14]}...` {command.short_doc if len(command.short_doc) < 58 else f'{command.short_doc[0:58]}...'}"

        self.paginator.add_line(signature)

    async def send_group_help(self, group):
        self.add_command_formatting(group)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)

        if filtered:
            note = self.get_opening_note()

            if note:
                self.paginator.add_line(note, empty=True)

            self.paginator.add_line("**%s**" % self.commands_heading)

            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()

            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

            await self.send_pages()


class Help(commands.Cog):
    "The Help Menu Cog"

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        self.bot.help_command = JDBotHelp()
        self.bot.help_command.cog = self


async def cog_unload(self):
    self.help_command = self._original_help_command


async def setup(bot):
    await bot.add_cog(Help(bot))
