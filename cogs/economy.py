import money_system, utils
from discord.ext import commands

import DatabaseConfig
bank = DatabaseConfig.db.money_system
job_db = DatabaseConfig.db.job_listing

async def check_user_exists(userid):
  default_document = {"user_id":userid,"balance":{"bank":0,"wallet":0}}
  try:
    await bank.insert_one(default_document)
  except:
    return 1

async def display_account(userid):
  await check_user_exists(userid)
  doc = await bank.find_one({"user_id":userid})
  print("Userid: "+str(userid))
  print("Balance:")
  print("\tBank: "+str(doc["balance"]["bank"]))
  print("\tWallet: "+str(doc["balance"]["wallet"]))

async def get_document(userid):
  await check_user_exists(userid)
  return await bank.find_one({"user_id":userid})

async def add_money(userid, money, _type=0):
  doc = await get_document(userid)
  if(_type==0):
    doc["balance"]["wallet"] = doc["balance"]["wallet"] + money
  if(_type==1):
    doc["balance"]["bank"] = doc["balance"]["bank"] + money
  if(_type==3):
    doc["balance"]["bank"] = doc["balance"]["bank"] + money
  await bank.delete_one({"user_id":userid})
  await bank.insert_one(doc)


async def add_job(name, num):
  try:
    await job_db.insert_one({"name":name,"total":num})
    return 1
  except:
    return 0

async def delete_job(name):
  try:
    await job_db.delete_one({"name":name})
    return 1
  except:
    return 0

async def use_job(name):
  doc = "N"
  try:
     doc = await job_db.find_one({"name":name})
  except:
    print("ERROR: JOB NOT FOUND")
  if(doc=="N"):
    pass

def decode_job(id):
  job_list =["a","b","c"]
  for num in range(len(job_list)):
    return job_list[num]

class Economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="Currently work in progress(WIP)")
  async def work(self,ctx,*,args=None):
    Member = ctx.author.id
    if args is None:
      await add_money(Member,10,0)

  @commands.command(brief="a command to send how much money you have(work in progress)",help="using the JDBot database you can see how much money you have")
  async def balance(self,ctx,*, Member: utils.BetterMemberConverter = None):
    if Member is None:
      Member = ctx.author
    await display_account(Member.id)

def setup(bot):
  bot.add_cog(Economy(bot))