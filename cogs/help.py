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
        for cog in self.bot.cogs:
            if label == cog:
                await get_help(self, interaction, CogToPassAlong=cog)
                return
        if label == "Close":
            embede = discord.Embed(
                title=":books: Help System",
                description=f"Welcome To {self.bot.user.name} Help System",
            )
            embede.set_footer(text="Use dropdown to select a category")
            await interaction.response.edit_message(embed=embede, view=None)


class DropdownView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        options = [
            SelectOption(label=cog, value=cog)
            for cog in bot.cogs
            if cog.lower()
            not in ["testingcog", "preferences", "calculator", "help", "workers", "jishaku", "listeners", "utils"]
        ]
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
                [
                    SelectOption(label=cog, value=cog)
                    for cog in bot.cogs
                    if cog.lower()
                    not in [
                        "testingcog",
                        "preferences",
                        "calculator",
                        "help",
                        "workers",
                        "jishaku",
                        "listeners",
                        "utils",
                    ]
                ]
                + [SelectOption(label="Close", value="Close")],
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


class Help(commands.HelpCommand):
    "The Help Menu Cog"

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def send_bot_help(self, mapping):
        embede = discord.Embed(
            title=":books: Help System",
            description=f"Welcome To {self.bot.user.name} Help System",
        )
        embede.set_footer(text="Use dropdown to select a category")
        view = DropdownView(self.bot)
        await self.context.send(embed=embede, view=view)

    async def send_command_help(self, command):
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

        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        await get_help(self, self.context, cog.qualified_name)


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
        self.set_footer(text="Use dropdown to select a category")


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
        if isinstance(command, discord.app_commands.Command):
            command_text = f"『`/{command.name}`』: {command.description}\n"
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
    if commands_text:
        embed.add_field(name="Commands", value=commands_text, inline=False)
    embeds.append(embed)

    if len(embeds) > 1:
        view = PaginationView(embeds, self.bot)
        await interaction.response.edit_message(embed=embeds[0], view=view)
    else:
        await interaction.response.edit_message(embed=embeds[0])


def setup(bot):
    bot.help_command = Help(bot)
