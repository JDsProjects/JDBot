from discord.ext import commands
import discord, random, typing
from difflib import SequenceMatcher

class Dice(commands.Cog):
  def __init__(self,client):
    self.client = client

  async def generate_embed(self,ctx,number):
    if number < 1:  
      return await ctx.send("NO")

    url_dict = {20 : "https://i.imgur.com/9dbBkqj.gif", 6:"https://i.imgur.com/6ul8ZGY.gif"}
    url = url_dict.get(number, "https://i.imgur.com/gaLM6AG.gif")

    embed = discord.Embed(title=f" Rolled a {random.randint(1,number)}", color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
    embed.set_footer(text = f"{ctx.author.id}")
    embed.set_thumbnail(url="https://i.imgur.com/AivZBWP.png")
    embed.set_author(name=f"d{number} Rolled by {ctx.author}:",icon_url=(ctx.author.avatar_url))
    embed.set_image(url=url)
    await ctx.send(embed=embed)

  @commands.command(brief="A command to roll random dnd dice.",aliases=["roll"])
  async def diceroll(self, ctx, * , number:typing.Optional[int]=None):
    if number : await self.generate_embed(ctx,int(number))
    else: await ctx.send("None that's bad.")

  @commands.command(brief="Gives random emojis(from guild and bot)",help="Please use wisely.",aliases=["e_spin","emoji_spin"])
  async def emoji_spinner(self,ctx):
    emoji_choosen = random.choice(self.client.emojis)

    if emoji_choosen.available is False: emoji_choosen = emoji_choosen.url
    
    if isinstance(ctx.channel, discord.TextChannel):
      if len(ctx.guild.emojis) > 0:
        emoji_choice=random.choice(ctx.guild.emojis)
        if emoji_choice.available is False: emoji_choice = emoji_choice.url
        await ctx.send(emoji_choice)

      await ctx.send(emoji_choosen)

    if isinstance(ctx.channel,discord.DMChannel): await ctx.send(emoji_choosen)
  
  @commands.command(brief="gives a random kawaii emoji.",aliases=["ka"])
  async def kawaii_random(self,ctx):
    kawaii_emotes= self.client.get_guild(773571474761973840)
    kawaii_emotes2 = self.client.get_guild(806669712410411068)
    kawaii_emotes3 = self.client.get_guild(692576207404793946)
    emoji_choosen = random.choice(kawaii_emotes.emojis+kawaii_emotes2.emojis+kawaii_emotes3.emojis)
    await ctx.send(emoji_choosen)

  @commands.command(brief="a magic 8ball command",aliases=["8ball"])
  async def _8ball(self,ctx,*,args=None):
    if args is None:
      await ctx.send("Please give us a value to work with.")
    if args:
      responses = ["As I see it, yes.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don’t count on it.","It is certain.","It is decidedly so.","Most likely.","My reply is no.","My sources say no.","Outlook not so good.","Outlook good.","Reply hazy, try again.","Signs point to yes.","Very doubtful.","Without a doubt.","Yes.","Yes – definitely.","You may rely on it."]
      await ctx.send(random.choice(responses))

  @commands.command(brief="gordon ramsay insults you(I don't own his likeness)",help="Please only use if you can handle insults :D (with some profanity)")
  async def insult2(self,ctx,*,args=None):
    ramsay_responses=["You are getting your kn*ckers in a twist! Calm down!", "WHAT ARE YOU? An idiot sandwich", "You fucking Donkey!", "How about a thank you, you miserable wee-bitch", "Hey, panini head, are you listening to me?", "For what we are about to eat, may the Lord make us truly not vomit", "Do you want a fucking medal?", "That fucking gremlin, everything you touch, you screw... there you go", "Your name is Elsa, isn't it? Because this shit is so fucking frozen", "This pork is so raw it's still singing Hakuna Matata", "Fuck off you bloody donut", "This crab is so raw it just offered me a krabby patty","The fucking bass is fucking RAW!","This chicken is so raw it's still asking why it crossed the road!","Hey excuse me madam, fuck me? How about fuck you.","Move It, Grandpa"]

    if args is None:
      await ctx.send(content=f"{ctx.author}, {random.choice(ramsay_responses)}")

    if args:
      await ctx.send(random.choice(ramsay_responses))

  @commands.command(brief="a command meant to flip coins",help="commands to flip coins, etc.")
  async def coin(self,ctx, *, args = None):
    if args:
      value = random.choice([True,False]) 
      if args.lower().startswith("h") and value: win = True
      elif args.lower().startswith("t") and not value:  win = True
      elif args.lower().startswith("h") and not value: win = False
      elif args.lower().startswith("t") and value: win = False    
      else: return await ctx.send("Please use heads or Tails as a value.")
      
      if(value): pic_name = "heads"
      else: pic_name ="Tails"

      url_dic = {"heads":"https://i.imgur.com/MzdU5Z7.png","Tails":"https://i.imgur.com/qTf1owU.png"}

      embed = discord.Embed(title="coin flip",color=random.randint(0, 16777215))
      embed.set_author(name=f"{ctx.author}",icon_url=(ctx.author.avatar_url))
      embed.add_field(name="The Coin Flipped: "+("heads" if value else "tails"),value=f"You guessed: {args}")
      embed.set_image(url=url_dic[pic_name])

      if win: embed.add_field(name="Result: ",value="You won")
      else: embed.add_field(name="Result: ",value="You lost")
      
      await ctx.send(embed=embed)

    if args is None: await ctx.send("example: \n```test*coin heads``` \nnot ```test*coin```")

  @commands.command(brief="a command to find the nearest emoji")
  async def emote(self,ctx,*,args=None):
    if args is None:
      await ctx.send("Please specify an emote")
    if args:
      emoji=discord.utils.get(self.client.emojis,name=args)
    
      emoji = emoji or "We haven't found anything"
      await ctx.send(emoji)

  @commands.command(help="a different method to find the nearest emoji")
  async def emote2(self,ctx,*,args=None):
    if args is None:
      await ctx.send("Please specify an emote")
    if args:
      emoji = sorted(self.client.emojis, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]

      emoji = emoji or "We haven't found anything"
      await ctx.send(emoji)
    
def setup(client):
  client.add_cog(Dice(client))