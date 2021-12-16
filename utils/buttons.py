import discord, asyncio

class BasicButtons(discord.ui.View):
  def __init__(self, ctx, **kwargs):
    super().__init__(**kwargs)
    self.ctx = ctx
    self.value: str = None

  @discord.ui.button(label = "Accept", style = discord.ButtonStyle.success, emoji = "✅")
  async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = True
    self.stop()

  @discord.ui.button(label="Deny", style = discord.ButtonStyle.danger , emoji = "❌")
  async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = False
    self.stop()

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True

class dm_or_ephemeral(discord.ui.View):
  def __init__(self, ctx, paginator_objects : list = None, channel : discord.DMChannel = None, **kwargs):
    super().__init__(**kwargs)
    self.ctx = ctx
    self.channel = channel
    self.paginator_objects = paginator_objects
    self.value: str = None

  @discord.ui.button(label = "Secret Message(Ephemeral)", style = discord.ButtonStyle.success, emoji = "🕵️")
  async def secretMessage(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await self.message.edit(content = "Will be sending you the mutual guilds empherally", view = self)
    
    await interaction.response.send_message("WIP, coming soon :tm:")
    
    #view = await interaction.response.send_message(f"Here are mutual guilds for you to see {self.ctx.author.mention}", view = view, ephemeral = True)
    #tbh i don't know yet.

  @discord.ui.button(label = "Secret Message(DM)", style = discord.ButtonStyle.success, emoji = "📥")
  async def dmMessage(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await self.message.edit(content = "Well be Dming you the Mutual Guilds", view = self)
    await interaction.response.send_message("WIP, coming soon :tm:")

    #do something by sending the menu paginator to the channel provided

  @discord.ui.button(label="Deny", style = discord.ButtonStyle.danger , emoji = "❌")
  async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await self.message.edit(content = "not sending the mutual guilds to you", view = self)
    

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't Use that button, {self.ctx.author.mention} is the author of this message.", ephemeral = True)

    return True

class nitroButtons(discord.ui.View):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.value: str = None

  @discord.ui.button(label = "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Claim⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", custom_id = "fun (nitro)", style = discord.ButtonStyle.success)
  async def nitroButton(self, button: discord.ui.Button, interaction: discord.Interaction):
    
    await interaction.response.send_message(content = "Oh no it was a fake", ephemeral = True)
    await asyncio.sleep(2)

    await interaction.edit_original_message(content = "Prepare to get rickrolled...(it's a good song anyway)")
    await asyncio.sleep(2)

    await interaction.edit_original_message(content = "https://i.imgur.com/NQinKJB.gif")

    button.disabled = True
    button.style = discord.ButtonStyle.secondary
    button.label = "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Claimed⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
    
    embed = discord.Embed(title = "You received a gift, but...", description = "The gift link has either expired or has been\nrevoked.", color = 3092790)
    embed.set_thumbnail(url = "https://i.imgur.com/w9aiD6F.png")

    await interaction.message.edit(view = self, embed = embed)

  async def on_timeout(self):
    self.children[0].disabled = True
    self.children[0].style = discord.ButtonStyle.secondary
    self.children[0].label = "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Claimed⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"

    embed = discord.Embed(title = "You received a gift, but...", description = "The gift link has either expired or has been\nrevoked.", color = 3092790)
    embed.set_thumbnail(url = "https://i.imgur.com/w9aiD6F.png")
    
    await self.message.edit(view = self, embed = embed)
  
class RpsGame(discord.ui.View):
  def __init__(self, ctx, **kwargs):
    super().__init__(**kwargs)
    self.ctx = ctx
    self.value: str = None

  @discord.ui.button(label = "Rock", style = discord.ButtonStyle.success, emoji = "🪨")
  async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.value = 1
    self.stop()

  @discord.ui.button(label="Paper", style = discord.ButtonStyle.success , emoji = "📰")
  async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.value = 2
    self.stop()

  @discord.ui.button(label="Scissors", style = discord.ButtonStyle.success , emoji = "✂️")
  async def scissors(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.value = 3
    self.stop()
  
  async def on_timeout(self):
    for item in self.children:
      item.disabled = True

    await self.message.edit(view = self)

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.", ephemeral = True)

    return True

class CoinFlip(discord.ui.View):
  def __init__(self, ctx, **kwargs):
    super().__init__(**kwargs)
    self.ctx = ctx
    self.value: str = None

  @discord.ui.button(label = "Heads", style = discord.ButtonStyle.success, emoji = "<:coin:693942559999000628>")
  async def Heads(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = "Heads"
    self.stop()

  @discord.ui.button(label = "Tails", style = discord.ButtonStyle.success , emoji = "🪙")
  async def tails(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = "Tails"
    self.stop()

  async def on_timeout(self):
    for item in self.children:
      item.disabled = True

    await self.message.edit(view = self)

  async def interaction_check(self, interaction: discord.Interaction):
    
    if self.ctx.author.id != interaction.user.id:
      return await interaction.response.send_message(content = f"You Can't play this game, {self.ctx.author.mention} is the user playing this game.", ephemeral = True)

    return True