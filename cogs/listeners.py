from discord.ext import commands
import discord, random, os

class Events(commands.Cog):
  def __init__(self,client):
    self.client = client
  
  @commands.Cog.listener()
  async def on_guild_join(self,guild):
    channels = [channel for channel in guild.channels]
    roles = roles= [role for role in guild.roles]
    embed = discord.Embed(title="Bot just joined: "+str(guild.name), color=random.randint(0,16777215))
    embed.set_thumbnail(url = guild.icon_url)
    embed.add_field(name='Server Name:',value=f'{guild.name}')
    embed.add_field(name='Server ID:',value=f'{guild.id}')
    embed.add_field(name='Server region:',value=f'{guild.region}')
    embed.add_field(name='Server Creation Date:',value=f'{guild.created_at}')
    embed.add_field(name='Server Owner:',value=f'{guild.owner}')
    embed.add_field(name='Server Owner ID:',value=f'{guild.owner_id}')
    embed.add_field(name='Member Count:',value=f'{guild.member_count}')
    embed.add_field(name='Amount of Channels:',value=f"{len(channels)}")
    embed.add_field(name='Amount of Roles:',value=f"{len(roles)}")
    await self.client.get_channel(738912143679946783).send(embed=embed)

  @commands.Cog.listener()
  async def on_guild_remove(self,guild):
    channels = [channel for channel in guild.channels]
    roles = roles= [role for role in guild.roles]
    embed = discord.Embed(title="Bot just left: "+str(guild.name), color=random.randint(0,16777215))
    embed.set_thumbnail(url = guild.icon_url)
    embed.add_field(name='Server Name:',value=f'{guild.name}')
    embed.add_field(name='Server ID:',value=f'{guild.id}')
    embed.add_field(name='Server region:',value=f'{guild.region}')
    embed.add_field(name='Server Creation Date:',value=f'{guild.created_at}')
    embed.add_field(name='Server Owner:',value=f'{guild.owner}')
    embed.add_field(name='Server Owner ID:',value=f'{guild.owner_id}')
    try:
      embed.add_field(name='Member Count:',value=f'{guild.member_count}')
    except:
      pass
    embed.add_field(name='Amount of Channels:',value=f"{len(channels)}")
    embed.add_field(name='Amount of Roles:',value=f"{len(roles)}")
    await self.client.get_channel(738912143679946783).send(embed=embed)

  @commands.Cog.listener()
  async def on_ready(self):
    print("Bot is Ready")
    print(f"Logged in as {self.client.user}")
    print(f"Id: {self.client.user.id}")

  @commands.Cog.listener()
  async def on_message(self,message):
    test=await self.client.get_context(message)
    
    if isinstance(message.channel, discord.DMChannel):
      if test.prefix is None or self.client.user.mentioned_in(message):
        if message.author.id != self.client.user.id and test.valid is False:
          await message.channel.send("Ticket Support is coming soon. For now Contact our Developers: Shadi#9492 or JDJG Inc. Official#3493")

    if (test.valid) == False and test.prefix != None and test.command is None:
      
      time_used=(message.created_at).strftime('%m/%d/%Y %H:%M:%S')
      embed_message = discord.Embed(title=f" {test.prefix}{test.invoked_with}", description=time_used,color=random.randint(0, 16777215))
      embed_message.set_author(name=f"{message.author} tried to excute invalid command:",icon_url=(message.author.avatar_url))
      embed_message.set_footer(text = f"{message.author.id}")
      embed_message.set_thumbnail(url="https://i.imgur.com/bW6ergl.png")
      await self.client.get_channel(738912143679946783).send(embed=embed_message)
  
  @commands.Cog.listener()
  async def on_error(event,*args,**kwargs):
    import traceback
    more_information=os.sys.exc_info()
    error_wanted=traceback.format_exc()
    traceback.print_exc()
    
    #print(more_information[0])

def setup(client):
  client.add_cog(Events(client))