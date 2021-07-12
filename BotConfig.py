import discord,  re, os, aiohttp, contextlib, aiosqlite, traceback, datetime, itertools
from discord.ext import commands

async def get_prefix(bot, message):
  extras = ["test*","te*", "t*"]
  comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
  match = comp.match(message.content)
  if match is not None:
    extras.append(match.group(1))
  return commands.when_mentioned_or(*extras)(bot, message)

intents = discord.Intents.all()
intents.members = False
intents.presences = False

class JDBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.special_access = {}

  async def start(self,*args, **kwargs):
    self.session=aiohttp.ClientSession()
    self.sus_users = await aiosqlite.connect('sus_users.db')
      #loads up some bot variables    

    
    conn = await self.sus_users.cursor()
    grab=await conn.execute("SELECT * FROM testers_list")
    self.testers = list(itertools.chain(*await grab.fetchall()))
    await conn.close()
    
    #does the DB connection and then assigns it a tester list
    await super().start(*args, **kwargs)

  async def close(self):
    await self.session.close()
    await self.sus_users.close()
    await super().close()

  async def getch_member(self, guild, member_id):
    member = None
    with contextlib.suppress(discord.Forbidden, discord.HTTPException):
      member = guild.get_member(member_id) or await guild.fetch_member(member_id)
    return member

  async def getch_user(self, user_id):
    user = None

    with contextlib.suppress(discord.NotFound, discord.HTTPException):
      user = self.get_user(user_id) or await self.fetch_user(user_id)
    return user


  async def filter_commands(self, ctx, command_list):

    async def check(cmd, ctx):
      try:
        return await cmd.can_run(ctx)

      except:
        return False
        
    return [cmd for cmd in command_list if await check(cmd, ctx)]

bot = JDBot(command_prefix = (get_prefix), intents = intents, chunk_guilds_at_startup = False, strip_after_prefix = True)

bot.launch_time = datetime.datetime.utcnow()

@bot.check
async def check_command_access(ctx):
  if ctx.author.id in bot.special_access:
    if ctx.command.name == bot.special_access.get(ctx.author.id):
      await ctx.command.reinvoke(ctx)
    del bot.special_access[ctx.author.id]
  
  return True

bot.load_extension('jishaku')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.ExtensionError:
      traceback.print_exc()

