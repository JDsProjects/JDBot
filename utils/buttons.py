import discord, typing, asyncio

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

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = True
    self.stop()

  @discord.ui.button(label="Deny", style = discord.ButtonStyle.danger , emoji = "❌")
  async def denied(self, button: discord.ui.Button, interaction: discord.Interaction):
    if not self.__authorized__(button, interaction):
      return await interaction.response.send_message(content = f"You Can't Use that button, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    self.clear_items()
    await interaction.response.edit_message(view = self)
    self.value = False
    self.stop()

class dm_or_ephemeral(discord.ui.View):
  def __init__(self, authorized_user: typing.Union[discord.User, discord.Member] = None, paginator_objects : list = None , **kwargs):
    super().__init__(**kwargs)
    self.authorized_user = authorized_user
    self.paginator_objects = paginator_objects
    self.value: str = None
  
  def __authorized__(self, button: discord.ui.Button, interaction: discord.Interaction) -> bool:
    if self.authorized_user and self.authorized_user.id != interaction.user.id:
      return False

    return True

  @discord.ui.button(label = "Secret Message", style = discord.ButtonStyle.success, emoji = "🕵️")
  async def secretMessage(self, button: discord.ui.Button, interaction: discord.Interaction):
    if not self.__authorized__(button, interaction):

      return await interaction.response.send_message(content = f"You Can't Use that button, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    self.clear_items()
    await interaction.response.edit_message(view = self)

    #view = 
    #await interaction.response.send_message(f"Here are mutual guilds for you to see {self.authorized_user.mention}", view = view, ephemeral = True)
    #tbh i don't know yet.

  @discord.ui.button(label = "Secret Message", style = discord.ButtonStyle.success, emoji = "📥")
  async def dmMessage(self, button: discord.ui.Button, interaction: discord.Interaction):
    if not self.__authorized__(button, interaction):

      return await interaction.response.send_message(content = f"You Can't Use that button, {self.authorized_user.mention} is the author of this message.", ephemeral = True)

    self.clear_items()
    await interaction.response.edit_message(view = self)


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
  
