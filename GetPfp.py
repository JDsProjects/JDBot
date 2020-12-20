import ClientConfig
def GetServerPfp(message):
  contents = message.content.split(" ")
  id_bit = 0
 
  try:

    id_bit = int(contents[1])
 
  except:

    id_bit = int(message.guild.id)
  
  guild_fetched=ClientConfig.client.get_guild(id_bit)

  server_icon=guild_fetched.icon_url

  return server_icon


async def get_username(message):
  args = message.content.replace(message.content.split(" ")[0]+" ","")
  if(len(message.content.split(" "))==1):
    return message.author.id
  try:
    test = int(args)
  except:
    test = -1
  if(test!=-1):
    return 0
  users = ClientConfig.client.users
  for us in users:
    try:
      if (us.name == args):  
        return us.id
    except:
      banana = 1
  return 0

async def GetUserPfp(message):
  args = message.content.replace(message.content.split(" ")[0]+" ","")
  print(args)
  id_bit = 0
  if(len(str(message.author.id))!=len(args)):
    id_bit = await get_username(message)
  else:
    try:
      id_bit = int(args)
    except:
      id_bit  = await get_username(message)

  #try:
  user = await ClientConfig.client.fetch_user(id_bit)
  return user
  #except:
    #return "NULL"

def DownloadAllPfp(message):
  for obj in message.guild.members:
    print(obj.avatar_url)
