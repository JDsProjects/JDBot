import discord, re, os, aiohttp, aiosqlite, traceback, itertools, asyncpg

from discord.ext import commands

async def get_prefix(bot, message):
  extras = ["test*", "te*", "t*", "jdbot.", "jd.", "test.", "te."]

  comp = re.compile("^(" + "|".join(map(re.escape, extras)) + ").*", flags=re.I)
  match = comp.match(message.content)
  if match is not None:
    extras.append(match.group(1))

  if await bot.is_owner(message.author): 
    extras.append("")
    
  return commands.when_mentioned_or(*extras)(bot, message)

class JDBot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.special_access = {}

  async def start(self, *args, **kwargs):
    self.session = aiohttp.ClientSession()
    self.db = await aiosqlite.connect('sus_users.db')
    self.db2 = await asyncpg.create_pool(os.getenv("DB_key"))

    #loads up some bot variables

    self.testers = list(itertools.chain(* await self.db.execute_fetchall("SELECT * FROM testers_list;")))

    #does the DB connection and then assigns it a tester list(may be a lot bit shorter but it should work better.)

    self.blacklisted_users = dict(await self.db.execute_fetchall("SELECT * FROM BLACKLISTED_USERS;"))
    
    self.blacklisted_users.update(dict(await self.db.execute_fetchall("SELECT * FROM SUS_USERS;")))

    self.history = [h.get("response") for h in await self.db2.fetch("SELECT * FROM RANDOM_HISTORY")]
    
    await super().start(*args, **kwargs)

  async def close(self):
    await self.session.close()
    await self.db.close()
    await super().close()

  async def filter_commands(self, ctx, command_list):

    async def check(cmd, ctx):
      try:
        return await cmd.can_run(ctx)

      except:
        return False
        
    return [cmd for cmd in command_list if await check(cmd, ctx)]


intents = discord.Intents.all()

bot = JDBot(command_prefix = (get_prefix), intents = intents, chunk_guilds_at_startup = False, strip_after_prefix = True, allowed_mentions = discord.AllowedMentions(everyone = False, roles = False))

bot.launch_time = discord.utils.utcnow()

@bot.check
async def check_command_access(ctx):
  if ctx.author.id in bot.special_access:
    if ctx.command.name == bot.special_access.get(ctx.author.id):
      await ctx.command.reinvoke(ctx)
    del bot.special_access[ctx.author.id]
  
  return True

@bot.check
async def check_blacklist(ctx):
  return ctx.author.id not in bot.blacklisted_users

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    try:
      bot.load_extension(f'cogs.{filename[:-3]}')
    except commands.errors.ExtensionError:
      traceback.print_exc()

