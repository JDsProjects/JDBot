import discord
import random
import utils
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Economy(commands.Cog):
    "Commands dealing with the Bot's Economy"

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 20, BucketType.user)
    @commands.command(brief="you can pick a job and then work it in this work command")
    async def work(self, ctx):

        jobs = await self.bot.db.fetch("SELECT * FROM jobs")

        view = utils.JobChoice(ctx, jobs, timeout=15.0)

        await ctx.send("Please Pick a job to do:", view=view)
        await view.wait()

        job = await self.bot.db.fetchrow("SELECT * FROM jobs WHERE job_name = $1", view.value)

        add_money = job.get("amount_paid")

        await self.bot.db.execute(
            "UPDATE economy SET wallet = wallet + ($1) WHERE user_id = ($2)", add_money, ctx.author.id
        )

        await ctx.send(f"You worked as a {job.get('job_name')} and got ${add_money} for working.")

    @commands.cooldown(1, 15, BucketType.user)
    @commands.command(
        brief="a command to send how much money you have",
        help="using the JDBot database you can see how much money you have",
        aliases=["bal"],
    )
    async def balance(self, ctx, *, member: utils.BetterMemberConverter = None):

        member = member or ctx.author

        economy = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = ($1)", member.id)

        if not economy:
            view = utils.BasicButtons(ctx)

            if ctx.author.id != member.id:
                return await ctx.send(
                    f"You aren't {member}. \nOnly they can join the database. You must ask them to join if you want them to be in there"
                )

            msg = await ctx.send(f"{member}, needs to join the database to run this. You can do it now", view=view)

            await view.wait()

            if view.value is None:
                return await msg.edit("you didn't respond quickly enough")

            if not view.value:
                return await msg.edit("Not adding you to the database")

            if view.value:
                await ctx.send("adding you to the database for economy...")

                await self.bot.db.execute("INSERT INTO economy VALUES($1)", member.id)

                economy = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)

        wallet = economy.wallet
        bank = economy.bank

        embed = discord.Embed(title=f"{member}'s Balance:", color=random.randint(0, 16777215))
        embed.add_field(name="Wallet:", value=f"${wallet:,}")
        embed.add_field(name="Bank:", value=f"${bank:,}")
        embed.add_field(name="Total:", value=f"${wallet+bank:,}")
        embed.add_field(name="Currency:", value="<:jmoney:919431869928464404>")
        embed.set_footer(
            text="Do not for any reason, trade JDJGbucks, sell or otherwise use real money or any other money to give others JDJGBucks or receive."
        )
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(brief="a leaderboard command goes from highest to lowest", aliases=["lb"])
    async def leaderboard(self, ctx):

        data = await self.bot.db.fetch("SELECT * FROM economy ORDER BY wallet + BANK DESC")

        ndata = []
        for n in data:
            place = [n.get("user_id") for n in data].index(n.get("user_id"))
            user = await self.bot.try_user(n.get("user_id"))

            ndata.append([f"{place + 1}. {user}", n.get("bank"), n.get("wallet")])

        ndata = utils.groupby(ndata, 5)

        menu = utils.LeaderboardEmbed(ndata, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="Removes You From Economy")
    async def leave_economy(self, ctx):

        economy = await self.bot.db.fetchrow("SELECT * FROM economy WHERE user_id = ($1)", ctx.author.id)

        if not economy:
            return await ctx.send("You can't just leave economy if you never joined .....")

        view = utils.BasicButtons(ctx)

        msg = await ctx.send(f"Are you sure you want to leave the database?", view=view)

        await view.wait()

        if view.value is None:
            return await msg.edit("you didn't respond quickly enough")

        if not view.value:
            return await msg.edit("Not removing you from the database")

        if view.value:

            wallet = economy.get("wallet")
            bank = economy.get("bank")

            embed = discord.Embed(title=f"{ctx.author}'s Balance:", color=random.randint(0, 16777215))
            embed.add_field(name="Wallet:", value=f"${wallet:,}")
            embed.add_field(name="Bank:", value=f"${bank:,}")
            embed.add_field(name="Total:", value=f"${wallet+bank:,}")
            embed.add_field(name="Currency:", value="<:jmoney:919431869928464404>")
            embed.set_footer(
                text="Do not for any reason, trade JDJGbucks, sell or otherwise use real money or any other money to give others JDJGBucks or receive."
            )

            await msg.edit(
                "removing you from the database for economy and archiving the economy data to our channel(so we can have you join back if you want, if you want it to fully removed, you can ask JDJG Inc. Official#3493, but once it's gone from the channel, it's gone for good) and in the guild right there...",
                embed=embed,
            )

        await self.bot.get_channel(855217084710912050).send(
            content=f"Backup of {ctx.author}'s Economy Data!", embed=embed
        )

        await self.bot.db.execute("DELETE FROM economy WHERE user_id = $1", ctx.author.id)


async def setup(bot):
    await bot.add_cog(Economy(bot))
