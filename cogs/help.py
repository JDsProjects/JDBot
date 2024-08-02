import discord
from discord import ButtonStyle, SelectOption
from discord.ext import commands
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
            embede.set_footer(text="Use the dropdown menu to select a category")
            await interaction.response.edit_message(embed=embede, view=None)


class DropdownView(discord.ui.View):
    def __init__(self, options, bot):
        super().__init__()
        self.bot = bot
        self.add_item(Dropdown(options, self.bot))


class Help(commands.Cog):
    "The Help Menu Cog"

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Shows the help menu")
    async def help(self, ctx: commands.Context, command: str = None):
        if command is None:
            await self.send_bot_help(ctx)
        else:
            await self.send_command_help(ctx, command)

    async def send_bot_help(self, ctx: commands.Context):
        embed = HelpEmbed(description=f"Welcome To {self.bot.user.name} Help System")
        usable = 0
        myoptions = []

        filtered_cogs = ["testingCOG", "Preferences", "Calculator", "Help"]

        for cog_name, cog in self.bot.cogs.items():
            print(cog_name)
            if cog_name.lower() not in [fc.lower() for fc in filtered_cogs]:
                print(filtered_cogs)
                if filtered_commands := [cmd for cmd in cog.get_commands()]:
                    amount_commands = len(filtered_commands)
                    usable += amount_commands
                    name = cog.qualified_name
                    description = cog.description or "No description"
                    myoptions.append(SelectOption(label=name, value=name))

        myoptions.append(SelectOption(label="Close", value="Close"))
        view = DropdownView(myoptions, self.bot)

        await ctx.send(embed=embed, view=view)

    async def send_command_help(self, ctx: commands.Context, command_name: str):
        command = self.bot.get_command(command_name)
        if not command:
            await ctx.send(f"No command called '{command_name}' found.", ephemeral=True)
            return

        signature = f"{ctx.prefix}{command.name}"
        if command.signature:
            signature += f" {command.signature}"
        embed = HelpEmbed(title=signature, description=command.help or "No help found...")

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        embed.add_field(name="Usable", value="Yes")

        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )

        await ctx.send(embed=embed)


class HelpEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
        self.title = ":books: Help System"

        self.set_footer(text="Use dropdown menu to select a category")


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
