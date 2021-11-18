import discord, random, aiogtts
import io

async def google_tts(text):
  mp3_fp = io.BytesIO()
  tts=aiogtts.aiogTTS()
  await tts.write_to_fp(text,mp3_fp,lang='en')
  mp3_fp.seek(0)
  file = discord.File(mp3_fp,"tts.mp3")
  return file

async def latin_google_tts(text):
  mp3_fp = io.BytesIO()
  tts=aiogtts.aiogTTS()
  await tts.write_to_fp(text,mp3_fp,lang='la')
  mp3_fp.seek(0)
  file = discord.File(mp3_fp,"latin_tts.mp3")
  return file

def reference(message):

  reference = message.reference
  if reference and isinstance(reference.resolved, discord.Message):
    return reference.resolved.to_reference()

  return None

def profile_converter(name):
  
  names_to_emojis = {
    "staff" : "<:staff:314068430787706880>",
    "partner" : "<:partnernew:754032603081998336>",
    "hypesquad" : "<:hypesquad:314068430854684672>",
    "bug_hunter" : "<:bughunter:585765206769139723>",
    "hypesquad_bravery" : "<:bravery:585763004218343426>",
    "hypesquad_brilliance" : "<:brilliance:585763004495298575>",
    "hypesquad_balance" : "<:balance:585763004574859273>",
    "early_supporter" : "<:supporter:585763690868113455> ",
    "system" : "<:system:863129934611349555><:system2:863129934633631774>",
    "bug_hunter_level_2" : "<:goldbughunter:853274684337946648>",
    "verified_bot" : "<:verified_bot:863128487610548304>",
    "verified_bot_developer" : "<:verifiedbotdev:853277205264859156>",
    "early_verified_bot_developer" : "<:verifiedbotdev:853277205264859156>",
    "discord_certified_moderator" : "<:certifiedmod:853274382339670046>",
    "bot" : "<:bot:863128982136684614>"
  }
  
  return names_to_emojis.get(name)


def bit_generator():
  return hex(random.randint(0, 255))[2:]

def cc_generate():
 return f"""
 8107EC20 {bit_generator()}{bit_generator()} 
 8107EC22 {bit_generator()}00
 8107EC28 {bit_generator()}{bit_generator()}
 8107EC2A {bit_generator()}00
 8107EC38 {bit_generator()}{bit_generator()}
 8107EC3A {bit_generator()}00
 8107EC40 {bit_generator()}{bit_generator()}
 8107EC42 {bit_generator()}00
 8107EC50 {bit_generator()}{bit_generator()}
 8107EC52 {bit_generator()}00
 8107EC58 {bit_generator()}{bit_generator()}
 8107EC5A {bit_generator()}00
 8107EC68 {bit_generator()}{bit_generator()}
 8107EC6A {bit_generator()}00
 8107EC70 {bit_generator()}{bit_generator()}
 8107EC72 {bit_generator()}00
 8107EC80 {bit_generator()}{bit_generator()}
 8107EC82 {bit_generator()}00
 8107EC88 {bit_generator()}{bit_generator()}
 8107EC8A {bit_generator()}00
 8107EC98 {bit_generator()}{bit_generator()}
 8107EC9A {bit_generator()}00
 8107ECA0 {bit_generator()}{bit_generator()}
 8107ECA2 {bit_generator()}00""".upper()

async def post(bot, code):
  async with bot.session.post("https://bin.charles-bot.com/documents", data = code) as resp:
      data = await resp.json()
      url = f"https://bin.charles-bot.com/{data['key']}"
      return url

#thanks Dutchy for this :D