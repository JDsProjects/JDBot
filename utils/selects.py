import discord

class SpaceInfo(discord.ui.Select):
  def __init__(self):

    options = [
        discord.SelectOption(label = 'Red', description = 'Your favourite colour is red', emoji = '🟥'),
        discord.SelectOption(label = 'Green', description='Your favourite colour is green', emoji = '🟩'),
        discord.SelectOption(label = 'Blue', description='Your favourite colour is blue', emoji = '🟦')
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

class RtfmSelects(discord.ui.Select):
  def __init__(self, options):
    
    super().__init__(placeholder = "Chose a library to lookup from.", min_values = 1, max_values = 1, options = options)

  async def callback(self, interaction: discord.Interaction):
    self.view.value = self.values[0]
    self.view.clear_items()
    await interaction.message.delete()
    self.view.stop()

class RtfmChoice(discord.ui.View):
  def __init__(self, ctx, libraries, **kwargs):
    super().__init__(**kwargs)
    
    self.value = [o("name") for o in libraries][0]
    self.ctx = ctx
    
    self.add_item(RtfmSelects([discord.SelectOption(label = o['name'], value = o["link"], emoji = "🔍") for o in libraries]))

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True