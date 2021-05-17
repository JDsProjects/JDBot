from utils import BetterMemberConverter, BetterUserconverter
import money_system
from discord.ext import commands


class Work(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Currently work in progress")
    async def work(self, ctx, *, args=None):
        Member = ctx.author.id
        if args is None:
            money_system.add_money(Member, 10, 0)

    @commands.command(
        brief="a command to send how much money you have(work in progress)",
        help="using the JDBot database you can see how much money you have",
    )
    async def balance(self, ctx, *, Member: BetterMemberConverter = None):
        if Member is None:
            Member = ctx.author
        money_system.display_account(Member.id)


def setup(client):
    client.add_cog(Work(client))
