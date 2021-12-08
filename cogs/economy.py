import discord, random
import utils
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.menus.views import ViewMenuPages

def groupby(iterable : list, number : int):
  resp = []
  while True:
    resp.append(iterable[:number])
    iterable = iterable[number:]
    if not iterable:
      break
  return resp

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def cog_command_error(self, ctx, error):
    if ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()

  @commands.cooldown(1, 20, BucketType.user)
  @commands.command(brief = "you can pick a job and then work it in this work command")
  async def work(self, ctx):

    member = ctx.author
    add_money = 10
    cur = await self.bot.db.cursor()

    await cur.execute("UPDATE economy SET wallet = wallet + (?) WHERE user_id = (?)", (add_money, member.id,))

    await self.bot.db.commit()

    await cur.close()

    await ctx.send("You worked the basic job.(more jobs coming soon)")

  @commands.cooldown(1, 15, BucketType.user)
  @commands.command(brief = "a command to send how much money you have", help = "using the JDBot database you can see how much money you have", aliases = ["bal"])
  async def balance(self, ctx, *, member: utils.BetterMemberConverter = None):

    member = member or ctx.author

    cur = await self.bot.db.cursor()
    cursor = await cur.execute("SELECT * FROM economy WHERE user_id = (?)", (member.id,))
    economy = await cursor.fetchone()
    await cur.close()

    if not economy:
      view = utils.BasicButtons(ctx)

      if ctx.author.id != member.id:
        return await ctx.send(f"You aren't {member}. \nOnly they can join the database. You must ask them to join if you want them to be in there")

      msg = await ctx.send(f"{member}, needs to join the database to run this. You can do it now", view = view)

      await view.wait()
      
      if view.value is None:
        return await msg.edit("you didn't respond quickly enough")

      if not view.value:
        return await msg.edit("Not adding you to the database")

      if view.value:
        await ctx.send("adding you to the database for economy...")

        cur = await self.bot.db.cursor()
        await cur.execute("INSERT INTO economy(user_id) VALUES (?)", (member.id,))
        await self.bot.db.commit()

        cur = await self.bot.db.cursor()
        cursor = await cur.execute("SELECT * FROM economy WHERE user_id = (?)", (member.id,))

        economy = await cursor.fetchone()
        await cur.close()
    

    data = tuple(economy)
    wallet = data[-1]
    bank = data[1]

    embed = discord.Embed(title = f"{member}'s Balance:", color = random.randint(0, 16777215))
    embed.add_field(name = "Wallet:", value = f"${wallet}", inline = True)
    embed.add_field(name = "Bank:", value = f"${bank}", inline = True)
    embed.add_field(name = "Total:", value = f"${wallet+bank}", inline = True)
    embed.add_field(name = "Currency:", value = "<:JDJGBucks:779516001782988810>", inline = True)
    embed.set_footer(text = "Do not for any reason, trade JDJGbucks, sell or otherwise use real money or any other money to give others JDJGBucks or receive.")
    await ctx.send(embed = embed)
  
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "a leaderboard command goes from highest to lowest", aliases = ["lb"])
  async def leaderboard(self, ctx):
    data = await self.bot.db.execute_fetchall("SELECT * FROM economy ORDER BY WALLET + BANK DESC")
    ndata = []
    
    for user_id, bank, wallet in data:
      ndata.append([await self.bot.try_user(user_id), bank, wallet])
    
    ndata = groupby(ndata, 5) # 5 is what i think is best
    # for now i'll take first item at index and i will embed it, so you can see what i mean
    
    e = discord.Embed("Leaderboard")
    
    for i in ndata:
      e.add_field(name = f"**{i[0]}:**", value = f"```yaml\nBANK: {i[1]}\nWALLET: {i[2]}```")
      break # i will only take first as you have lots of datas, other items are upto u to handle
    
    await ctx.send(embed=e)

def setup(bot):
  bot.add_cog(Economy(bot))
