from discord.ext import commands
import discord
import random
import asuna_api

class Extra(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command(brief="a way to look up minecraft usernames",help="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)")
  async def mchistory(self,ctx,*,args=None):
    
    if args is None:
      await ctx.send("Please pick a minecraft user.")

    if args:
      asuna = asuna_api.Client()
      minecraft_info=await asuna.mc_user(args)
      await asuna.close()
      embed=discord.Embed(title=f"Minecraft Username: {args}",color=random.randint(0, 16777215))
      embed.set_footer(text=f"Minecraft UUID: {minecraft_info.uuid}")
      embed.add_field(name="Orginal Name:",value=minecraft_info.name)
      y = 0
      for x in minecraft_info.history:
        if y > 0:
          embed.add_field(name=f"Username:\n{x['name']}",value=f"Date Changed:\n{x['changedToAt']}\n \nTime Changed: \n {x['timeChangedAt']}")

        y = y + 1
      embed.set_author(name=f"Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
      await ctx.send(embed=embed)

  @commands.command(help="This gives random history using Sp46's api.",brief="a command that uses SP46's api's random history command to give you random history responses")
  async def random_history(self,ctx,*,args=None):
    if args is None:
      args = 1
    asuna = asuna_api.Client()
    response = await asuna.random_history(args)
    await asuna.close()
    for x in response:
      await ctx.send(f":earth_africa: {x}")
  
def setup(client):
  client.add_cog(Extra(client))
