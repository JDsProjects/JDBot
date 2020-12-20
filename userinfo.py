import ClientConfig
import GetPfp
async def user_grab(message):
  client_used = ClientConfig.client
  try:
    tmp = await GetPfp.get_username(message)
    user_person = client_used.get_user(tmp)
    if(int(tmp)==0):
      raise Exception("Not User")
  except:
    try:
      user_person = message.mentions[0]
    except:
      user_person = client_used.get_user(int(message.content.split(" ")[1].replace(" ","")))
      if user_person is None:
        user_person=await client_used.fetch_user(int(message.content.split(" ")[1].replace(" ","")))
      if user_person is None:
        user_person = message.author
  return user_person