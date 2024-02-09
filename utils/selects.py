import discord
import mathjspy

# A bunch of Select Classes and views for them(below me).


class RtfmSelects(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Chose a library to lookup from.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class RtfmChoice(discord.ui.View):
    def __init__(self, ctx, libraries, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("link") for o in libraries][0]
        self.ctx = ctx

        self.add_item(
            RtfmSelects([discord.SelectOption(label=o["name"], value=o["link"], emoji="🔍") for o in libraries])
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


class JobSelects(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Chose a Job to do.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class JobChoice(discord.ui.View):
    def __init__(self, ctx, jobs, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("job_name") for o in jobs][0]
        self.ctx = ctx

        self.add_item(JobSelects([discord.SelectOption(label=o["job_name"], emoji="🧑‍💼") for o in jobs]))

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


class SubRedditSelects(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Chose a Subreddit.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]
        self.view.clear_items()
        await interaction.message.delete()
        self.view.stop()


class SubredditChoice(discord.ui.View):
    def __init__(self, ctx, subreddits, **kwargs):
        super().__init__(**kwargs)

        self.value = [o.get("name") for o in subreddits][0]
        self.ctx = ctx

        self.add_item(
            SubRedditSelects(
                [discord.SelectOption(label=o["name"], emoji="<:reddit:309459767758290944>") for o in subreddits]
            )
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Here's the default...", view=self)


# These are Calculator Functions
def get_highest(iterable):
    resp = 0
    for i in iterable:
        if i > resp:
            resp = i
    return resp


def get_last_operator(response: str):
    try:
        plus = response.rindex("+")
    except ValueError:
        plus = None
    try:
        minus = response.rindex("-")
    except ValueError:
        minus = None
    try:
        mul = response.rindex("*")
    except ValueError:
        mul = None
    try:
        div = response.rindex("/")
    except ValueError:
        div = None
    valid = [n for n in [plus, minus, mul, div] if n != None]
    indx = get_highest(valid)
    return response[indx:]


async def default_execution_function(view, label, interaction: discord.Interaction):
    view.expression += str(label)
    await interaction.response.edit_message(content=view.expression)


async def operator_handler(view, label, interaction: discord.Interaction):
    if not view.expression or not view.expression[0].isdigit():
        return await interaction.response.send_message("You cannot use operators at start.", ephemeral=True)
    if not view.expression[-1].isdigit():
        return await interaction.response.send_message("You cannot add operator after operator.", ephemeral=True)
    view.expression += label
    await interaction.response.edit_message(content=view.expression)


async def give_result_operator(view, label, interaction: discord.Interaction):
    parser = view.parser
    if not view.expression:
        return await interaction.response.send_message("You didn't tell me anything to evaluate.", ephemeral=True)
    if view.expression.replace(".", "").isdigit() and view.last_expr:
        view.expression += view.last_expr
    else:
        view.last_expr = get_last_operator(view.expression)
    result = str(float(parser.eval(view.expression)))
    if "e" in result:
        result = result.split("e")[0]
    view.expression = result
    await interaction.response.edit_message(content=result)


async def stop_button(view, label, interaction: discord.Interaction):
    for i in view.children:
        i.disabled = True
    await interaction.response.edit_message(view=view)
    view.stop()


async def go_back(view, label, interaction: discord.Interaction):
    if not view.expression:
        return
    view.expression = view.expression[:-1]
    await interaction.response.edit_message(content=view.expression)


# These are Calculator Buttons
class CalcButton(discord.ui.Button):
    def __init__(
        self, label: str, row: int, execution_function=default_execution_function, style=discord.ButtonStyle.blurple
    ):
        super().__init__(label=f"{label}", row=row, style=style)
        self.__func = execution_function

    async def callback(self, interaction: discord.Interaction):
        await self.__func(self.view, self.label, interaction)


# Actual Calculator Buttons
class CalcView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.parser = mathjspy.MathJS()
        self.expression = ""
        self.last_expr = ""
        numb = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        for row in range(len(numb)):
            for i in numb[row]:
                self.add_item(CalcButton(i, row))
        self.add_item(CalcButton("=", 3, give_result_operator, discord.ButtonStyle.gray))
        self.add_item(CalcButton("<==", 3, go_back))
        for label, row in [["+", 0], ["-", 1], ["*", 2], ["/", 3]]:
            self.add_item(CalcButton(label, row, operator_handler, discord.ButtonStyle.green))
        self.add_item(CalcButton(f'{"Stop":⠀^20}', 4, stop_button, discord.ButtonStyle.red))
        self.add_item(CalcButton(".", 4, style=discord.ButtonStyle.green))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                f"This button can only be accessed by {self.ctx.author.name}.", ephemeral=True
            )
            return False
        else:
            return True

    async def on_timeout(self):
        for i in self.children:
            i.disabled = True
        await self.message.edit(content="If you want your calculator to work you need to make a new one.", view=self)
        self.stop()
