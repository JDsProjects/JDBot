# Modal Classes
import discord


class CodeBlockModal(discord.ui.Modal, title="Pep8 Project Formatter:"):
    code = discord.ui.TextInput(
        label="Code Block:", placeholder="Please Put your code here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Code Block Submitted and Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run the pep8 formatter again.", view=self.view)
        self.stop()


class CodeBlockView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.value: str = None
        self.value2: str = None
        self.ctx = ctx
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅", custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = True

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger, emoji="✖️", custom_id="Deny")
    async def denied(self, interaction: discord.Interaction, button: discord.ui.Button):
        for i in self.children:
            if i.custom_id == "accept" or i.custom_id == "Deny":
                i.disabled = True

        await interaction.response.edit_message(view=self)
        self.value2 = False

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="<:click:264897397337882624>", row=1)
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CodeBlockModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.code
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class MailModal(discord.ui.Modal, title="Mail:"):
    message = discord.ui.TextInput(
        label="Message:", placeholder="Please Put Your Message Here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run mail again.", view=self.view)
        self.stop()


class MailView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.value: str = None
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MailModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.message
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class ChatBotModal(discord.ui.Modal, title="ChatBot(Travitia API):"):
    args = discord.ui.TextInput(
        label="Message:",
        placeholder="Please Put Your Message Here:",
        style=discord.TextStyle.paragraph,
        min_length=3,
        max_length=60,
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.args
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        response = await self.view.ask(args, self.view.ctx.author.id)
        await self.view.message.edit(content=f"{response}", view=self.view)

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run chatbot again.", view=self.view)


class ChatBotModal2(discord.ui.Modal, title="ChatBot (Some Random Api):"):
    args = discord.ui.TextInput(
        label="Message:",
        placeholder="Please Put Your Message Here:",
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        args = self.args
        self.view.message = await interaction.followup.send(
            "Message Received(you will receive your chatbot response in a moment", ephemeral=True
        )
        # response = await self.view.ask2(args)
        # await self.view.message.edit(content=f"{response}", view=self.view)

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run chatbot again.", view=self.view)


class ChatBotView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChatBotModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Submit 2", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit_alt(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChatBotModal2(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await self.message.edit(view=None)
        await modal.wait()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.success, emoji="✖️")
    async def Close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Closing ChatBot", view=None)


class ReportModal(discord.ui.Modal, title="Report:"):
    report = discord.ui.TextInput(
        label="Report Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run report again.", view=self.view)
        self.stop()


class ReportView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.value: str = None
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReportModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.report
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AddBotModal(discord.ui.Modal, title="Reason:"):
    reason = discord.ui.TextInput(
        label="Addbot Reason:", placeholder="Please Put Your Reason here:", style=discord.TextStyle.paragraph
    )

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Message Received.", ephemeral=True)
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run addbot again.", view=self.view)
        self.stop()


class AddBotView(discord.ui.View):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.value: str = None
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.success, emoji="📥")
    async def Submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddBotModal(self, timeout=180.0)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.value = modal.reason
        button.disabled = True
        await self.message.edit(view=self)
        self.stop()


class AceModal(discord.ui.Modal):
    name = discord.ui.TextInput(label="Name", style=discord.TextStyle.short)
    text = discord.ui.TextInput(label="Text", style=discord.TextStyle.paragraph, max_length=240)

    def __init__(self, view, **kwargs):
        self.view = view
        super().__init__(**kwargs)

        default = f"{self.view.ctx.author}"
        self.name.default = default
        self.name.placeholder = default

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.message.delete()
        name = self.name
        text = self.text
        buf = await self.view.jeyy_client.ace(name, self.side, text)
        buf.seek(0)
        file = discord.File(buf, "out.gif")
        await self.view.ctx.message.reply(
            content="Take That! (Thank you Jeyy for providing your api):",
            file=file,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.stop()

    async def on_timeout(self):
        for i in self.view.children:
            i.disabled = True
        await self.view.message.edit(content="You May want to run ace again.", view=self.view)


class AceView(discord.ui.View):
    def __init__(self, ctx, jeyy_client, **kwargs):
        self.ctx = ctx
        self.jeyy_client = jeyy_client
        self.value: str = None
        super().__init__(**kwargs)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            return await interaction.response.send_message(
                content=f"You Can't Use that Button, {self.ctx.author.mention} is the author of this message.",
                ephemeral=True,
            )

        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(content="Looks like the view timed out try again", view=self)
        self.stop()

    @discord.ui.button(label="Attorney", style=discord.ButtonStyle.success, emoji="<a:think:626236311539286016>")
    async def Attorney(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AceModal(self, title="Attorney Text:", timeout=180.0)
        modal.side = button.label.lower()
        await interaction.response.send_modal(modal)
        self.stop()

    @discord.ui.button(
        label="Prosecutor", style=discord.ButtonStyle.danger, emoji="<a:edgeworthZoom:703531746699903046>"
    )
    async def Prosecutor(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AceModal(self, title="Prosecutor Text:", timeout=180.0)
        modal.side = button.label.lower()
        await interaction.response.send_modal(modal)
        self.stop()
