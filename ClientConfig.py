import discord,  re, os, discord_slash, aiohttp, contextlib, aiosqlite3
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
    self.special_access = {}
    
    #speacil values that will be used for config(will swap to something else.)
    #self.log_channel=738912143679946783

  async def start(self,*args, **kwargs):
    self.session=aiohttp.ClientSession()
    self.sus_users = await aiosqlite3.connect('sus_users.db')
    await super().start(*args, **kwargs)

  async def close(self):
    await self.session.close()
    await self.sus_users.close()
    await super().close()

  async def getch_member(self,guild,member_id):
    member = None
    with contextlib.suppress(discord.Forbidden, discord.HTTPException):
      member = guild.get_member(member_id) or await guild.fetch_member(member_id)
    return member

client = JDBot(command_prefix=(get_prefix),intents=intents,chunk_guilds_at_startup=False)
bot = client

@bot.check
async def check_command_access(ctx):
  if ctx.author.id in bot.special_access:
    if ctx.command.name == bot.special_access.get(ctx.author.id):
      await ctx.command.reinvoke(ctx)
    del bot.special_access[ctx.author.id]
  return True

slash = discord_slash.SlashCommand(client,override_type = True,sync_commands=True)

client.load_extension('jishaku')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      client.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.NoEntryPointError as e:
      print(e)