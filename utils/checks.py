def check(ctx):
  def inner(m):
    return m.author == ctx.author
  return inner

def Membercheck(ctx):
  def inner(m):
    return m.author == ctx.guild.me
  return inner