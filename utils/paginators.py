import discord

#class MutualGuildsEmbed(Paginator):
  #def format_page(self, item):
    #embed = discord.Embed(title = "Mutual Servers:", description = item , color = random.randint(0, 16777215))
    
    #return embed

class dm_or_ephemeral(discord.ui.View):
  def __init__(self, ctx, items : list = None, channel : discord.DMChannel = None, **kwargs):
    super().__init__(**kwargs)
    self.ctx = ctx
    self.channel = channel
    self.items = items

  @discord.ui.button(label = "Secret Message(Ephemeral)", style = discord.ButtonStyle.success, emoji = "🕵️")
  async def secretMessage(self, button: discord.ui.Button, interaction: discord.Interaction):

    self.clear_items()
    await self.message.edit(content = "Will be sending you the mutual guilds empherally", view = self)

    #view = MutualGuildsEmbed(self.ctx)
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