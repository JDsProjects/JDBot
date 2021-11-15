import discord, random
import utils
from discord.ext import commands

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief = "Currently work in progress(WIP)")
  async def work(self, ctx):

    member = ctx.author
    add_money = 10
    cur = await self.bot.sus_users.cursor()

    await cur.execute("UPDATE economy SET wallet = wallet + (?) WHERE user_id = (?)", (add_money, member.id,))

    await self.bot.sus_users.commit()

    await cur.close()

  @commands.command(brief = "a command to send how much money you have", help = "using the JDBot database you can see how much money you have", aliases = ["bal"])
  async def balance(self, ctx, *, member: utils.BetterMemberConverter = None):

    member = member or ctx.author

    cur = await self.bot.sus_users.cursor()
    cursor = await cur.execute("SELECT * FROM economy WHERE user_id = (?)", (member.id,))
    economy = await cursor.fetchone()
    await cur.close()

    if not economy:
      view = utils.BasicButtons(ctx)
      msg = await ctx.send(f"{member} needs to join the database. You can do it now", view = view)

      await view.wait()
      
      if view.value is None:
        return await msg.edit("you didn't respond quickly enough")

      if not view.value:
        return await msg.edit("Not adding you to the database")

      if view.value:
        await ctx.send("adding you to the database for economy...")

        cur = await self.bot.sus_users.cursor()
        await cur.execute("INSERT INTO economy(user_id) VALUES (?)", (member.id,))
        await self.bot.sus_users.commit()

        cur = await self.bot.sus_users.cursor()
        cursor = await cur.execute("SELECT * FROM economy WHERE user_id = (?)", (member.id,))

        economy = await cursor.fetchone()
        await cur.close()
            

    data = tuple(economy)
    wallet = data[-1]
    bank = data[1]

    embed = discord.Embed(title=f"{member}'s Balance:", description = f"Wallet : {wallet} \nBank : {bank}", color = random.randint(0, 16777215))
    await ctx.send(embed = embed)
  

def setup(bot):
  bot.add_cog(Economy(bot))