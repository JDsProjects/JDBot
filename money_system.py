import DatabaseConfig
import ClientConfig

bank = DatabaseConfig.db.money_system

job_db = DatabaseConfig.db.job_listing

def check_user_exists(userid):
  default_document = {"user_id":userid,"balance":{"bank":0,"wallet":0}}
  try:
    bank.insert_one(default_document)
  except:
    return 1

def display_account(userid):
  check_user_exists(userid)
  doc = bank.find_one({"user_id":userid})
  print("Userid: "+str(userid))
  print("Balance:")
  print("\tBank: "+str(doc["balance"]["bank"]))
  print("\tWallet: "+str(doc["balance"]["wallet"]))


def get_document(userid):
  check_user_exists(userid)
  return bank.find_one({"user_id":userid})



def add_money(userid, money, _type=0):
  doc = get_document(userid)
  if(_type==0):
    doc["balance"]["wallet"] = doc["balance"]["wallet"] + money
  if(_type==1):
    doc["balance"]["bank"] = doc["balance"]["bank"] + money
  if(_type==3):
    doc["balance"]["bank"] = doc["balance"]["bank"] + money
  bank.delete_one({"user_id":userid})
  bank.insert_one(doc)


def add_job(name, num):

  try:
    job_db.insert_one({"name":name,"total":num})
    return 1
  except:
    return 0

def delete_job(name):
  try:
    job_db.delete_one({"name":name})
    return 1
  except:
    return 0

def use_job(name):
  doc = "N"
  try:
    doc = job_db.find_one({"name":name})
  except:
    print("ERROR: JOB NOT FOUND")
  if(doc=="N"):
    pass



def decode_job(id):
  job_list =["a","b","c"]
  for num in range(len(job_list)):
    return job_list[num]