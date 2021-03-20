from discord.ext import commands
import discord
import os
import itertools

testers_list =  [652910142534320148,524916724223705108,168422909482762240,742214686144987150,813445268624244778,700210850513944576,717822288375971900,218481166142013450],703674286711373914

class Test(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def random_number(self,ctx,*numbers):
    tmp = []
    for x in numbers:
      tmp.append(x)
    numbers = tmp
    for x in numbers:
      if x.isdigit() is False:
        numbers.remove(x)
    print(numbers)
    if len(numbers) > 1:
      pass
    
  @commands.command(brief="this command will error by sending no content")
  async def te(self,ctx):
    await ctx.send("")

  async def cog_check(self, ctx):
    return ctx.author.id in testers_list

def setup(client):
  client.add_cog(Test(client))