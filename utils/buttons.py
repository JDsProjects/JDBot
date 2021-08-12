import discord, typing

class BasicButtons(discord.ui.View):
  def __init__(self, authorized_user: typing.Union[discord.User, discord.Member] = None, **kwargs):
    super().__init__(**kwargs)
    self.authorized_user = authorized_user
    self.value: str = None
  
  def __authorized__(self, button: discord.ui.Button, interaction: discord.Interaction) -> bool:
    if self.authorized_user and self.authorized_user.id != interaction.user.id:
      return False

    return True

  @discord.ui.button(label = "Accept", style = discord.ButtonStyle.success, emoji = "✅")
  async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
    if not self.__authorized__(button, interaction):

      return await interaction.response.send_message(content = f"You Can't Use that button, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    self.value = True
    self.stop()

  @discord.ui.button(label="Deny", style = discord.ButtonStyle.danger , emoji = "❌")
  async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):
    if not self.__authorized__(button, interaction):
      return await interaction.response.send_message(content = f"You Can't Use that button, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    self.value = False
    self.stop()


  