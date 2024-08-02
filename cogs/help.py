import discord
from discord import ButtonStyle, SelectOption
from discord.ext import commands
from discord.ui import Button, Select, View


class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        embeds = []
        myoptions = []

        for cog, commands in mapping.items():
            if filtered_commands := await self.filter_commands(commands):
                amount_commands = len(filtered_commands)
                name = cog.qualified_name if cog else "No Category"
                description = cog.description if cog else "Commands with no category"
                myoptions.append(SelectOption(label=name, value=name))

                embed = HelpEmbed(title=f"{name} Commands", description=description)
                for command in filtered_commands:
                    embed.add_field(name=command.name, value=command.help or "No help available", inline=False)
                embeds.append(embed)

        myoptions.append(SelectOption(label="Close", value="Close"))
        view = PaginatedHelpView(embeds)

        await ctx.send(embed=embeds[0], view=view)

    async def send_command_help(self, command):
        ctx = self.context
        signature = f"{self.context.clean_prefix}{command.qualified_name}"
        if command.signature:
            signature += f" {command.signature}"
        embed = HelpEmbed(
            title=signature, description=command.help or "No help found..."
        )

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        embed.add_field(name="Usable", value="Yes")

        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )

        await ctx.send(embed=embed)


class Dropdown(discord.ui.Select):
    def __init__(self, options, bot):
        self.bot = bot
        super().__init__(placeholder="Select a category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        label = self.values[0]
        for cog in self.bot.cogs:
            if label == cog:
                await get_help(self, interaction, CogToPassAlong=cog)
        if label == "Close":
            embede = discord.Embed(
                title=":books: Help System",
                description=f"Welcome To {self.bot.user.name} Help System",
            )
            embede.set_footer(text="Use the dropdown menu to select a category")
            await interaction.response.edit_message(embed=embede, view=None)


class DropdownView(discord.ui.View):
    def __init__(self, options, bot):
        super().__init__()
        self.bot = bot
        self.add_item(Dropdown(options, self.bot))


class PaginatedHelpView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="Previous", style=ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])

    @discord.ui.button(label="Next", style=ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])


class Help(commands.Cog):
    "The Help Menu Cog"

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
        self.set_footer(text="Use the buttons to navigate through pages")


async def get_help(self, interaction, CogToPassAlong):
    cog = self.bot.get_cog(CogToPassAlong)
    if not cog:
        return
    emb = discord.Embed(
        title=f"{CogToPassAlong} - Commands",
        description=cog.__doc__,
    )
    emb.set_author(name="Help System")
    for command in cog.get_commands():
        emb.add_field(name=f"『`{interaction.client.command_prefix}{command.name}`』", value=command.help, inline=False)
    await interaction.response.edit_message(embed=emb)


def setup(bot):
    bot.add_cog(Help(bot))
