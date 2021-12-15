import discord

class JobSelects(discord.ui.Select):
  def __init__(self, options):
    
    super().__init__(placeholder = "Chose a Job to do.", min_values = 1, max_values = 1, options = options)

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
    
    self.add_item(JobSelects([discord.SelectOption(label = o['job_name'], emoji = "🧑‍💼") for o in jobs]))

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True

  async def on_timeout(self):
    for item in self.children:
      item.disabled = True

    await self.message.edit(content = "Here's the default...", view = self)

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
    
    self.value = [o.get("link") for o in libraries][0]
    self.ctx = ctx
    
    self.add_item(RtfmSelects([discord.SelectOption(label = o['name'], value = o["link"], emoji = "🔍") for o in libraries]))

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that Select, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True

  async def on_timeout(self):
    for item in self.children:
      item.disabled = True

    await self.message.edit(content = "Here's the default...", view = self)