from discord.ext import commands
import discord, typing, random
import utils
from discord.ext.commands.cooldowns import BucketType
import collections, itertools

class Test(commands.Cog):
  """A cog to have people test new commands, or wip ones"""
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ticket_make(self, ctx):
    await ctx.send("WIP, will make ticket soon.. Please Contact the owner with the support command")

  @commands.command(brief="this command will error by sending no content")
  async def te(self, ctx):
    await ctx.send("this command will likely error...")
    await ctx.send("")

  @commands.command(brief = "WIP command to verify")
  async def verify(self, ctx):
    await ctx.send("WIP will make this soon..")

  async def cog_check(self, ctx):
    return ctx.author.id in self.bot.testers
  
  @commands.command(brief = "a command to email you(work in progress)", help = "This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary")
  async def email(self, ctx, *args):
    print(args)
    await ctx.send("WIP")

  @commands.command(brief="make a unique prefix for this guild(other prefixes still work)")
  async def setprefix(self, ctx, *, arg = None):
    await ctx.send("WIP")

  @commands.command(brief = "WIP thing for birthday set up lol")
  async def birthday_setup(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief ="sleep time")
  async def set_sleeptime(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief = "wakeup time")
  async def set_wakeuptime(self, ctx):
    await ctx.send("WIP")

  @commands.command(brief = "gets tweets from a username")
  async def tweet(self, ctx, amount : typing.Optional[int] = None, username = None):

    amount = amount or 10

    if not username:
      return await ctx.send("You Need to pick a username.")

    await ctx.send("WIP")

  @commands.command(brief = "add emoji to your guild lol")
  async def emoji_add(self, ctx):
    await ctx.send("WIP")
    #look at the JDJG Bot orginal

  @commands.command(brief = "scans statuses to see if there is any bad ones.")
  async def scan_status(self, ctx):
    await ctx.send("will scan statuses in a guild to see if there is a bad one.")

  @commands.command(brief = "sets logs for a guild", name = "logging")
  async def _logging(self, ctx):
    await ctx.send("logging wip.")

  #look at global_chat stuff for global_chat features, rank for well rank, add an update system too, add cc_ over. nick too, as well as kick and ban, ofc unban and other guild ban moderation stuff. Port over emoji_check but public and make that do it's best to upload less than 256 kB, try to and ofc an os emulation mode, as well as update mode, and nick.
  
  #make the bot be able to lock commands to owners only, for testing purposes or not respond to commands.

  #Unrelated to Urban:
  #https://discordpy.readthedocs.io/en/master/api.html?highlight=interaction#discord.InteractionResponse.send_message
  #https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild.query_members

  #guild_prefixes table in my sql database
  #spyco data table in my sql database

  class TodoEmbed(utils.Paginator):
    def format_page(self, item):
      embed = discord.Embed(description = item , color = random.randint(0, 16777215), timestamp = self.ctx.message.created_at)

      embed.set_author(name = f"Todo Requested By {self.ctx.author}:", icon_url = self.ctx.author.display_avatar.url)
      return embed

  @commands.group(brief = "list of commands of plans of stuff to do in the future", invoke_without_command = True)
  async def todo(self, ctx):

    await ctx.send_help(ctx.command)

  @todo.command(brief = "lists stuff in todo")
  async def list(self, ctx):
    
    values = await self.bot.db.fetch("SELECT * FROM todo WHERE user_id = $1 ORDER BY added_time ASC", ctx.author.id)

    if not values:
      
      embed = discord.Embed(description = "No items in your Todo List", color = 1246983, timestamp = ctx.message.created_at)
      embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.display_avatar.url)
      
      return await ctx.send(embed = embed)
      
    pag = commands.Paginator(max_size = 4098)
    
    for index, todo_entry in enumerate(values):
      pag.add_line(f"[{index+1}]({todo_entry['jump_url']}). {discord.utils.format_dt(todo_entry['added_time'], 'R')} {todo_entry['text']}")

    pages = [page.strip("`") for page in pag.pages]

    menu = self.TodoEmbed(pages, ctx = ctx, delete_message_after = True)

    await menu.send(ctx.channel)

  @todo.command(brief = "adds items to todo")
  async def add(self, ctx, *, text : commands.clean_content = None):

    if not text:
      return await ctx.send("Please tell me what to add")
    
    value = await self.bot.db.fetchrow("SELECT * FROM todo WHERE user_id = $1 AND TEXT = $2", ctx.author.id, text)

    if value:
      embed = discord.Embed(description = f"[ADDED HERE]({value['jump_url']}) : {discord.utils.format_dt(value['added_time'], 'R')}", color = random.randint(0, 16777215), timestamp = ctx.message.created_at)
      embed.add_field(name = "Text:", value = f"{value['text']}")
      embed.set_footer(text = "Repeated Text", icon_url = "https://i.imgur.com/nPAONbK.png")
      return await ctx.send(content = "That was already added here:", embed = embed)
      
    await self.bot.db.execute("INSERT INTO todo (user_id, text, jump_url, added_time) VALUES ($1, $2, $3, $4)", ctx.author.id, text[0:4000], ctx.message.jump_url, ctx.message.created_at)

    await ctx.send("ADDED")
    #show what was added, or at least the text

  @todo.command(brief = "edits items in todo")
  async def edit(self, ctx):
    await ctx.send("WIP")

  @todo.command(brief = "removes items in todo")
  async def remove(self, ctx):
    await ctx.send("WIP")

  @todo.command(brief = "removes all your items in todo")
  async def clear(self, ctx):
    await ctx.send("WIP")

  #add support for https://discordpy.readthedocs.io/en/master/api.html#discord.Member.mobile_status 
 #https://discordpy.readthedocs.io/en/master/api.html#discord.Member.desktop_status 
   #https://discordpy.readthedocs.io/en/master/api.html#discord.Member.web_status
  #do something with this: https://discordpy.readthedocs.io/en/master/api.html#discord.Member.status


class Slash(commands.Cog):
  """A Testing Category for Slash Commands"""
  def __init__(self, bot):
    self.bot = bot

def setup(bot):
  bot.add_cog(Test(bot))
  bot.add_cog(Slash(bot))