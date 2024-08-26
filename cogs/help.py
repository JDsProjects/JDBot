"""
The Help Menu Cog provides a help system for the Discord bot, allowing users to access information about the bot's commands and features.

The `Dropdown` class is a custom Discord UI Select component that allows users to select a category of commands to view help for. The `DropdownView` class is a custom Discord UI View that contains the `Dropdown` component.

The `PaginationView` class is a custom Discord UI View that allows users to navigate through multiple pages of help information, with a dropdown to select a category and buttons to move to the previous or next page.

The `Help` class is a custom Discord help command that provides the main functionality of the help system, including sending the initial help menu, sending help information for individual commands, and sending help information for specific cogs (command categories).

The `HelpEmbed` class is a custom Discord Embed class that is used to format the help information in an embedded message.

The `get_help` function is a helper function that is used to generate the help information for a specific cog.
"""

import discord
from discord.ext import commands
from discord import ButtonStyle, SelectOption
from discord.ui import Button, Select, View


class Dropdown(discord.ui.Select):
    def __init__(self, options, bot):
        self.bot = bot
        super().__init__(placeholder="Select a category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        label = self.values[0]
        if label == "Close":
            await interaction.response.edit_message(embed=discord.Embed(title="Help Closed"), view=None)
            return

        for cog in self.bot.cogs:
            if label == cog:
                await get_help(self, interaction, CogToPassAlong=cog)
                return


class DropdownView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        options = [SelectOption(label=cog, value=cog) for cog in bot.cogs]
        options.append(SelectOption(label="Close", value="Close"))
        self.add_item(Dropdown(options, self.bot))


class PaginationView(discord.ui.View):
    def __init__(self, embeds, bot):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
        self.bot = bot

        self.add_item(
            Dropdown(
                [SelectOption(label=cog, value=cog) for cog in bot.cogs] + [SelectOption(label="Close", value="Close")],
                self.bot,
            )
        )

        self.add_item(Button(style=ButtonStyle.primary, label="◀", custom_id="previous"))
        self.add_item(Button(style=ButtonStyle.primary, label="▶", custom_id="next"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "previous":
            self.current_page = max(0, self.current_page - 1)
        elif interaction.data["custom_id"] == "next":
            self.current_page = min(len(self.embeds) - 1, self.current_page + 1)

        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        return True


class Help(commands.Cog):
    "The Help Menu Cog"

    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = MyHelp()


class MyHelp(commands.HelpCommand):
    "The Help Menu Cog"

    def __init__(self):
        super().__init__(command_attrs={"help": "The help command for the bot"})

    async def send(self, **kwargs):
        """a short cut to sending to get_destination"""
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title=":books: Help System",
            description=f"Welcome To {self.context.bot.user.name} Help System",
        )
        embed.set_footer(text="Use dropdown to select category")
        view = DropdownView(self.context.bot)
        await self.send(embed=embed, view=view)

    async def send_command_help(self, command):
        try:
            signature = f"/{command.name}"
            if isinstance(command, discord.app_commands.Command):
                signature += f" {' '.join([f'<{param.name}>' for param in command.parameters])}"

            embed = HelpEmbed(title=signature, description=command.description or "No help found...")
            if cog := command.cog:
                embed.add_field(name="Category", value=cog.qualified_name)

            embed.add_field(name="Usable", value="Yes")

            if command._buckets and (cooldown := command._buckets._cooldown):
                embed.add_field(
                    name="Cooldown",
                    value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
                )

            await self.send(embed=embed)
        except Exception as e:
            await self.send(f"An error occurred while processing the command help: {e}")

    async def send_cog_help(self, cog):
        try:
            await get_help(self, self.context, cog.qualified_name)
        except Exception as e:
            await self.send(f"An error occurred while processing the cog help: {e}")


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
        self.set_footer(text="Use dropdown to select category")


async def get_help(self, interaction, CogToPassAlong):
    cog = self.bot.get_cog(CogToPassAlong)
    if not cog:
        return

    embeds = []
    embed = discord.Embed(
        title=f"{CogToPassAlong} - Commands",
        description=cog.__doc__,
    )
    embed.set_author(name="Help System")
    commands_text = ""
    for command in cog.get_commands():
        if isinstance(command, (discord.app_commands.Command, commands.Command)):
            command_text = (
                f"『`/{command.name}`』: {command.description or command.help or 'No description available'}\n"
            )
            if len(commands_text) + len(command_text) > 1024:
                embed.add_field(name="Commands", value=commands_text, inline=False)
                embeds.append(embed)
                embed = discord.Embed(
                    title=f"{CogToPassAlong} - Commands (Continued)",
                    description=cog.__doc__,
                )
                embed.set_author(name="Help System")
                commands_text = command_text
            else:
                commands_text += command_text
        elif isinstance(command, (discord.app_commands.Group, commands.Group)):
            command_text = (
                f"『`/{command.name}`』: {command.description or command.help or 'No description available'}\n"
            )
            if len(commands_text) + len(command_text) > 1024:
                embed.add_field(name="Commands", value=commands_text, inline=False)
                embeds.append(embed)
                embed = discord.Embed(
                    title=f"{CogToPassAlong} - Commands (Continued)",
                    description=cog.__doc__,
                )
                embed.set_author(name="Help System")
                commands_text = command_text
            else:
                commands_text += command_text
            for subcommand in command.commands:
                subcommand_text = f"  『`/{command.name} {subcommand.name}`』: {subcommand.description or subcommand.help or 'No description available'}\n"
                if len(commands_text) + len(subcommand_text) > 1024:
                    embed.add_field(name="Commands", value=commands_text, inline=False)
                    embeds.append(embed)
                    embed = discord.Embed(
                        title=f"{CogToPassAlong} - Commands (Continued)",
                        description=cog.__doc__,
                    )
                    embed.set_author(name="Help System")
                    commands_text = subcommand_text
                else:
                    commands_text += subcommand_text

    if commands_text:
        embed.add_field(name="Commands", value=commands_text, inline=False)

    embeds.append(embed)

    if len(embeds) > 1:
        view = PaginationView(embeds, self.bot)
        await interaction.response.edit_message(embed=embeds[0], view=view)
    else:
        await interaction.response.edit_message(embed=embeds[0])


async def setup(bot):
    await bot.add_cog(Help(bot))
