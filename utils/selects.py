import discord, typing

class SpaceInfo(discord.ui.Select):
  def __init__(self):

    options = [
        discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),
        discord.SelectOption(label='Green', description='Your favourite colour is green', emoji='🟩'),
        discord.SelectOption(label='Blue', description='Your favourite colour is blue', emoji='🟦')
    ]

    
    super().__init__(placeholder = 'Choose your favourite colour...', min_values = 1, max_values = 1, options=options)

  async def callback(self, interaction: discord.Interaction):

      await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')
      print(self.values[0])

class gameChoice(discord.ui.View):
  def __init__(self, authorized_user: typing.Union[discord.User, discord.Member] = None, **kwargs):
    super().__init__(**kwargs)

    self.authorized_user = authorized_user
        
    self.add_item(SpaceInfo())

  def __authorized__(self, interaction: discord.Interaction) -> bool:
    if self.authorized_user and self.authorized_user.id != interaction.user.id:
      return False

    return True

  async def interaction_check(self, interaction: discord.Interaction):
    
    if not self.__authorized__(interaction):
      return await interaction.response.send_message(content = f"You Can't Use that Select, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    return True

  