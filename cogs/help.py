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
        if label == "Close":
            embede = discord.Embed(
                title=":books: Help System",
                description=f"Welcome To {self.bot.user.name} Help System",
            )
            embede.set_footer(text="Developed with ❤️ by Middlle")
            await interaction.response.edit_message(embed=embede, view=None)


class PaginationView(discord.ui.View):
    def __init__(self, embeds, options, bot):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
        self.bot = bot
        self.add_item(Dropdown(options, self.bot))
        self.add_item(Button(style=ButtonStyle.primary, label="◀", custom_id="previous"))
        self.add_item(Button(style=ButtonStyle.primary, label="▶", custom_id="next"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "previous":
            self.current_page = max(0, self.current_page - 1)
        elif interaction.data["custom_id"] == "next":
            self.current_page = min(len(self.embeds) - 1, self.current_page + 1)

        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        return True


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        embeds = []
        myoptions = []
        filtered_cogs = ["testingCOG", "Preferences", "Calculator", "Help"]

        for cog_name, cog in bot.cogs.items():
            if cog_name.lower() not in [fc.lower() for fc in filtered_cogs]:
                if filtered_commands := [
                    cmd for cmd in cog.get_commands() if isinstance(cmd, discord.app_commands.Command)
                ]:
                    name = cog.qualified_name
                    description = cog.description or "No description"
                    myoptions.append(SelectOption(label=name, value=name))

                    embed = HelpEmbed(title=f"{name} Commands", description=description)
                    for command in filtered_commands:
                        embed.add_field(
                            name=f"/{command.name}", value=command.description or "No description", inline=False
                        )
                    embeds.append(embed)

        myoptions.append(SelectOption(label="Close", value="Close"))
        view = PaginationView(embeds, myoptions, bot)

        await ctx.send(embed=embeds[0], view=view)

    async def send_command_help(self, command):
        ctx = self.context

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

        await ctx.send(embed=embed)


class Help(commands.Cog):
    "The Help Menu Cog"

    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @commands.hybrid_command(name="help", description="Shows the help menu")
    async def help(self, ctx: commands.Context, command: str = None):
        if command is None:
            await self.bot.help_command.send_bot_help(None)
        else:
            cmd = self.bot.get_command(command)
            if cmd:
                await self.bot.help_command.send_command_help(cmd)
            else:
                await ctx.send(f"No command called '{command}' found.", ephemeral=True)


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
        self.set_footer(text="Developed with ❤️ by Middlle")


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
        if isinstance(command, discord.app_commands.Command):
            emb.add_field(name=f"『`/{command.name}`』", value=command.description, inline=False)
    await interaction.response.edit_message(embed=emb)


async def setup(bot):
    await bot.add_cog(Help(bot))
