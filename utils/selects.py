import discord

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


class gameChoice(discord.ui.View):
  def __init__(self, ctx, **kwargs):
    super().__init__(**kwargs)

    self.ctx = ctx
        
    self.add_item(SpaceInfo())

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True

  