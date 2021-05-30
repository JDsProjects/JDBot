from discord.ext import commands
import discord, random, asuna_api, math, aiohttp, io, chardet, aiogtts, mystbin, alexflipnote, os, typing

class Extra(commands.Cog):
  def __init__(self,client):
    self.client = client

  @commands.command(brief="a way to look up minecraft usernames",help="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)")
  async def mchistory(self,ctx,*,args=None):
    
    if args is None:
      await ctx.send("Please pick a minecraft user.")

    if args:
      asuna = asuna_api.Client(self.client.session)
      minecraft_info=await asuna.mc_user(args)
      embed=discord.Embed(title=f"Minecraft Username: {args}",color=random.randint(0, 16777215))
      embed.set_footer(text=f"Minecraft UUID: {minecraft_info.uuid}")
      embed.add_field(name="Orginal Name:",value=minecraft_info.name)
      for y, x in enumerate(minecraft_info.history):
        if y > 0:
          embed.add_field(name=f"Username:\n{x['name']}",value=f"Date Changed:\n{x['changedToAt']}\n \nTime Changed: \n {x['timeChangedAt']}")

      embed.set_author(name=f"Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
      await ctx.send(embed=embed)

  @commands.command(help="This gives random history using Sp46's api.",brief="a command that uses SP46's api's random history command to give you random history responses")
  async def random_history(self,ctx,*,args=None):
    if args is None:
      args = 1
    asuna = asuna_api.Client(self.client.session)
    response = await asuna.random_history(args)
    for x in response:
      await ctx.send(f":earth_africa: {x}")

  @commands.command(brief="gives you the digits of pi that Python knows")
  async def pi(self,ctx):
    await ctx.send(math.pi)

  @commands.command(brief="reverses text")
  async def reverse(self,ctx,*,args=None):
    if args:
      await ctx.send(args[::-1])
    if args is None:
      await ctx.send("Try sending actual to reverse")

  @commands.command(brief="Oh no Dad Jokes, AHHHHHH!")
  async def dadjoke(self,ctx):
    response=await self.client.session.get("https://icanhazdadjoke.com/",headers={"Accept": "application/json"})
    joke=await response.json()
    embed = discord.Embed(title="Random Dad Joke:",color=random.randint(0, 16777215))
    embed.set_author(name=f"Dad Joke Requested by {ctx.author}",icon_url=(ctx.author.avatar_url))
    embed.add_field(name="Dad Joke:",value=joke["joke"])
    embed.set_footer(text=f"View here:\n https://icanhazdadjoke.com/j/{joke['id']}")
    await ctx.send(embed=embed)

  @commands.command(brief="gets a panel from the xkcd comic",aliases=["astrojoke","astro_joke"])
  async def xkcd(self,ctx):
    response=await self.client.session.get("https://xkcd.com/info.0.json")
    info=await response.json()

    num = random.randint(1,info["num"])
    comic = await self.client.session.get(f"https://xkcd.com/{num}/info.0.json")
    data=await comic.json()
    title = data["title"]
    embed=discord.Embed(title=f"Title: {title}",color=random.randint(0, 16777215))
    embed.set_image(url=data["img"])
    embed.set_footer(text=f"Made on {data['month']}/{data['day']}/{data['year']}")
    await ctx.send(embed=embed)

  @commands.command()
  async def http_cat(self, ctx, * , args : typing.Optional[typing.Union[int,str]] = None ):
    if args is None: code = "404"

    if args:
      if isinstance(args,int):
        if args > 99 and args < 600: code = args
        else: code = "404"
      
      else:
        await ctx.send("Not a valid arg using 404")
        code = "404"
    
    response = await self.client.session.get(f"https://http.cat/{code}")
    if response.status:
      image = f"https://http.cat/{code}.jpg"

    embed=discord.Embed(title=f"Status Code: {code}",color=random.randint(0, 16777215))
    embed.set_author(name=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
    embed.set_image(url=image)
    embed.set_footer(text="Powered by http.cat")
    await ctx.send(embed=embed)

  @commands.command(help="Gives advice from JDJG api.",aliases=["ad"])
  async def advice(self,ctx):
    r=await self.client.session.get('https://jdjgapi.nom.mu/api/advice')
    res = await r.json()
    embed = discord.Embed(title = "Here is some advice for you!",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this helped!")
    embed.set_footer(text="Powered by JDJG Api!")
    try:
      await ctx.send(embed=embed)
    except:
      await ctx.send("was too long...")

  @commands.command(help="gives random compliment")
  async def compliment(self,ctx):
    r=await self.client.session.get('https://jdjgapi.nom.mu/api/compliment')
    res = await r.json()
    embed = discord.Embed(title = "Here is a compliment:",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this helped your day!")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives an insult")
  async def insult(self,ctx):
    r=await self.client.session.get('https://jdjgapi.nom.mu/api/insult')
    res = await r.json()
    embed = discord.Embed(title = "Here is a insult:",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this Helped?")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives response to slur")
  async def noslur(self,ctx):
    r=await self.client.session.get('https://jdjgapi.nom.mu/api/noslur')
    res = await r.json()
    embed = discord.Embed(title = "Don't Swear",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "WHY MUST YOU SWEAR?")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives random message",aliases=["rm"])
  async def random_message(self,ctx):
    r=await self.client.session.get('https://jdjgapi.nom.mu/api/randomMessage')
    res = await r.json()
    embed = discord.Embed(title = "Random Message:",color=random.randint(0, 16777215))
    embed.add_field(name="Here:",value=res["text"])
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  async def google_tts(self,ctx,text):
    await ctx.send("if you have a lot of text it may take a bit")
    mp3_fp = io.BytesIO()
    tts=aiogtts.aiogTTS()
    await tts.write_to_fp(text,mp3_fp,lang='en')
    mp3_fp.seek(0)
    file = discord.File(mp3_fp,"tts.mp3")
    await ctx.send(file=file)

  @commands.command(help="a command to talk to Google TTS",brief="using the power of the GTTS module you can now do tts")
  async def tts(self,ctx,*,args=None):
    if args:
      await self.google_tts(ctx,args)
    
    if ctx.message.attachments:
      for x in ctx.message.attachments:
        file=await x.read()
        if len(file) > 0:
          encoding=chardet.detect(file)["encoding"]
          if encoding:
            text = file.decode(encoding)
            await self.google_tts(ctx,text)
          if encoding is None:
            await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439")
        if len(file ) < 1:
          await ctx.send("this doesn't contain any bytes.")
          

    if args is None and len(ctx.message.attachments) < 1:
      await ctx.send("You didn't specify any value.")

  @commands.command(help="learn about a secret custom xbox controller",brief="this will give you a message of JDJG's classic wanted xbox design.")
  async def secret_controller(self,ctx):
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name="Secret Xbox Image:")
    embed.add_field(name="Body:",value="Zest Orange")
    embed.add_field(name="Back:",value="Zest Orange")
    embed.add_field(name="Bumpers:",value="Zest Orange")
    embed.add_field(name="Triggers:",value="Zest Orange")
    embed.add_field(name="D-pad:",value="Electric Green")
    embed.add_field(name="Thumbsticks:",value="Electric Green")
    embed.add_field(name="ABXY:",value="Colors on Black")
    embed.add_field(name="View & Menu:",value="White on Black")
    embed.add_field(name="Engraving(not suggested):",value="JDJG Inc.")
    embed.add_field(name="Disclaimer:",value="I do not work at microsoft,or suggest you buy this I just wanted a place to represent a controller that I designed a while back.")
    embed.set_image(url="https://i.imgur.com/QCh4M2W.png")
    embed.set_footer(text="This is Xbox's custom controller design that I picked for myself.\nXbox is owned by Microsoft. I don't own the image")
    await ctx.send(embed=embed)

  @commands.command(brief="repeats what you say",help="a command that repeats what you say the orginal message is deleted")
  async def say(self,ctx,*,args=None):
    if args is None:
      args = "You didn't give us any text to use."

    args=discord.utils.escape_markdown(args,as_needed=False,ignore_links=False)
    try:
      await ctx.message.delete()

    except discord.errors.Forbidden:
      pass

    await ctx.send(args,allowed_mentions=discord.AllowedMentions.none())

  @commands.command(brief="a command to backup text",help="please don't upload any private files that aren't meant to be seen")
  async def text_backup(self,ctx):
    if not ctx.message.attachments:
      return
    for x in ctx.message.attachments:
      file=await x.read()
      if len(file) > 0:
        encoding=chardet.detect(file)["encoding"]
        if encoding:
          text = file.decode(encoding)
          mystbin_client = mystbin.Client(session=self.client.session)
          paste = await mystbin_client.post(text)
          await ctx.send(content=f"Added text file to mystbin: \n{paste.url}")
        if encoding is None:
          await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439 or it wasn't a text file.")
      if len(file ) < 1:
        await ctx.send("this doesn't contain any bytes.")
          
          
  @commands.group(name="apply",invoke_without_command=True)
  async def apply(self,ctx):
    await ctx.send("this command is meant to apply")

  @apply.command(brief="a command to apply for our Bloopers.",help="a command to apply for our bloopers.")
  async def bloopers(self,ctx,*,args=None):
    if args is None:
      await ctx.send("You didn't give us any info.")
    if args:
      if isinstance(ctx.message.channel, discord.TextChannel):
        await ctx.message.delete()

      for x in [708167737381486614,168422909482762240]:
        apply_user = self.client.get_user(x)
      
      if (apply_user.dm_channel is None):
        await apply_user.create_dm()
      
      embed_message = discord.Embed(title=args,color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
      embed_message.set_author(name=f"Application from {ctx.author}",icon_url=(ctx.author.avatar_url))
      embed_message.set_footer(text = f"{ctx.author.id}")
      embed_message.set_thumbnail(url="https://i.imgur.com/PfWlEd5.png")
      await apply_user.send(embed=embed_message)

  @commands.command()
  async def caw(self,ctx):
    alex_api = alexflipnote.Client(os.environ["alex_apikey"],session=self.client.session)
    url=await alex_api.birb()
    await ctx.send(url)

  @commands.command(aliases=["joke"])
  async def jokeapi(self, ctx):
    jokeapi_grab=await self.client.session.get("https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single")
    response_dict=await jokeapi_grab.json()
    embed=discord.Embed(title=f"{response_dict['joke']}",color=random.randint(0, 16777215))
    embed.set_author(name=f"{response_dict['category']} Joke:")
    embed.add_field(name="Language:",value=f"{response_dict['lang']}")
    embed.add_field(name=f"Joke ID:",value=f"{response_dict['id']}")
    embed.add_field(name="Type:",value=f"{response_dict['type']}")
    embed.set_footer(text=f"Joke Requested By {ctx.author} \nPowered by jokeapi.dev")
    await ctx.send(embed=embed)

  @jokeapi.error
  async def jokeapi_error(self,ctx,error):
    await ctx.send(error)
  
def setup(client):
  client.add_cog(Extra(client))
