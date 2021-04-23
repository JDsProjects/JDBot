import discord,  re, os, discord_slash, aiohttp
from discord.ext import commands

async def get_prefix(client,message):
  extras = ["test*","te*"]
  comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
  match = comp.match(message.content)
  if match is not None:
    extras.append(match.group(1))
  return commands.when_mentioned_or(*extras)(client, message)

intents = discord.Intents.all()
intents.members = False
intents.presences = False

class JDBot(commands.Bot):
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

  async def start(self,*args, **kwargs):
    self.aiohttp_session=aiohttp.ClientSession()
    await super().start(*args, **kwargs)

  async def close(self):
    await self.aiohttp_session.close()
    await super().close()

client = JDBot(command_prefix=(get_prefix),intents=intents)
slash = discord_slash.SlashCommand(client,override_type = True,sync_commands=True)

client.load_extension('jishaku')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      client.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.NoEntryPointError as e:
      print(e)