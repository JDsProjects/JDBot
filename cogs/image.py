import functools
import io
import random

import asuna_api
import cairosvg
import discord
import jeyyapi
import sr_api
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

import utils


class Image(commands.Cog):
    "A bunch of Image Manipulation and other related Image commands"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="a command to slap someone", help="this sends a slap gif to the target user")
    async def slap(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("slap")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} slapped you! Ow...", icon_url=(person.display_avatar.url))
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them... likely didn't make us able to dm them or they blocked us.")

    @commands.command(brief="a command to look up foxes", help="this known as wholesome fox to the asuna api")
    async def fox2(self, ctx):
        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("wholesome_foxes")
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(
            name=f"{ctx.author} requested a wholesome fox picture", icon_url=(ctx.author.display_avatar.url)
        )
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")
        await ctx.send(embed=embed)

    @commands.command(brief="another command to give you pat gifs", help="powered using the asuna api")
    async def pat2(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("pat")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} patted you! *pat pat pat*", icon_url=(person.display_avatar.url))
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(brief="a command to give you pat gifs", help="using the sra api it gives you pat gifs")
    async def pat(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        sr_client = sr_api.Client(session=self.bot.session)
        image = await sr_client.get_gif("pat")
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} patted you", icon_url=(person.display_avatar.url))
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(brief="a hug command to hug people", help="this the first command to hug.")
    async def hug(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        sr_client = sr_api.Client(session=self.bot.session)
        image = await sr_client.get_gif("hug")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} hugged you! Awwww...", icon_url=(person.display_avatar.url))
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(help="takes a .png attachment or your avatar and makes a triggered version.")
    async def triggered(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author
        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png"):
                    url = a.url
                    embeds.append(await utils.triggered_converter(url, ctx))

                    y += 1
                if not a.filename.endswith(".png"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url
            embeds.append(await utils.triggered_converter(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(
        brief="uses our headpat program to pat you", help="a command that uses jeyyapi to make a headpat of you."
    )
    async def headpat2(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author
        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png"):
                    url = a.url
                    embeds.append(await utils.headpat_converter(url, ctx))
                    y += 1
                if not a.filename.endswith(".png"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url
            embeds.append(await utils.headpat_converter(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(
        brief="a hug command to hug people", help="this actually the second hug command and is quite powerful."
    )
    async def hug2(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("hug")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} super hugged you!", icon_url=(person.display_avatar.url))
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(
        brief="a kiss command",
        help="a command where you can target a user or pick yourself to get a kiss gif( I don't know why I have this)",
    )
    async def kiss(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("kiss")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} kissed you", icon_url=(person.display_avatar.url))
        embed.set_image(url=url.url)
        embed.set_footer(text="Why did I make this command? powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(brief="a command to get a neko", help="using the asuna.ga api you will get these images")
    async def neko(self, ctx):
        asuna = asuna_api.Client(session=self.bot.session)
        url = await asuna.get_gif("neko")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{ctx.author} requested a neko picture", icon_url=(ctx.author.display_avatar.url))
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")
        await ctx.send(embed=embed)

    @commands.command(
        brief="a command to send wink gifs", wink="you select a user to send it to and it will send it to you lol"
    )
    async def wink(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        sr_client = sr_api.Client(session=self.bot.session)
        image = await sr_client.get_gif("wink")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} winked at you", icon_url=(person.display_avatar.url))
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(brief="Gives you a random waifu image.")
    async def waifu(self, ctx):
        r = await self.bot.session.get("https://api.waifu.pics/sfw/waifu")
        res = await r.json()
        embed = discord.Embed(color=random.randint(0, 16777215), timestamp=(ctx.message.created_at))
        embed.set_author(name=f"{ctx.author} Requested A Waifu")
        embed.set_image(url=res["url"])
        embed.set_footer(text="Powered by waifu.pics")
        await ctx.send(embed=embed)

    @commands.command(brief="Gives you a random waifu image.")
    async def waifu2(self, ctx):
        r = await self.bot.session.get("https://api.waifu.im/random/?is_nsfw=false&many=false&full=false")
        res = await r.json()
        image = res["images"][0]
        embed = discord.Embed(
            color=random.randint(0, 16777215), timestamp=(ctx.message.created_at), url=image["preview_url"]
        )
        embed.set_author(name=f"{ctx.author} Requested A Waifu")
        embed.set_image(url=image["url"])
        embed.set_footer(text="Powered by waifu.im")
        await ctx.send(embed=embed)

    @commands.command(brief="Gives you a random bonk picture")
    async def bonk(self, ctx):
        r = await self.bot.session.get("https://api.waifu.pics/sfw/bonk")
        res = await r.json()
        embed = discord.Embed(color=random.randint(0, 16777215), timestamp=(ctx.message.created_at))
        embed.set_author(name=f"{ctx.author} Requested A Bonk")
        embed.set_image(url=res["url"])
        embed.set_footer(text="Powered by waifu.pics")
        await ctx.send(embed=embed)

    @commands.command(
        brief="a command to send facepalm gifs", help="using some random api it sends you a facepalm gif lol"
    )
    async def facepalm(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        sr_client = sr_api.Client(session=self.bot.session)
        image = await sr_client.get_gif("face-palm")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{target} you made {person} facepalm", icon_url=person.display_avatar.url)
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            if target.dm_channel is None:
                await target.create_dm()

            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(help="gives a random objection", aliases=["obj", "ob", "object"])
    async def objection(self, ctx):
        r = await self.bot.session.get("https://api.senarc.org/misc/objection")
        res = await r.json()
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{ctx.author} yelled OBJECTION!", icon_url=(ctx.author.display_avatar.url))
        embed.set_image(url=res["url"])
        embed.set_footer(text="Powered By Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(help="gives the truth about opinions(may offend)", aliases=["opinion"])
    async def opinional(self, ctx):
        r = await self.bot.session.get("https://api.senarc.org/misc/opinional")
        res = await r.json()
        embed = discord.Embed(title="Truth about opinions(may offend some people):", color=random.randint(0, 16777215))
        embed.set_image(url=res["url"])
        embed.set_footer(text="Powered by Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(brief="a command to send I hate spam.")
    async def spam(self, ctx):
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_image(url="https://i.imgur.com/1LckTTu.gif")
        await ctx.send(content="I hate spam.", embed=embed)

    @commands.command(brief="gives you the milkman gif", help="you summoned the milkman oh no")
    async def milk(self, ctx):
        embed = discord.Embed(title="You have summoned the milkman", color=random.randint(0, 16777215))
        embed.set_image(url="https://i.imgur.com/JdyaI1Y.gif")
        embed.set_footer(text="his milk is delicious")
        await ctx.send(embed=embed)

    @commands.command(help="inverts any valid image within the sr_api")
    async def invert2(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author
        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png") or a.filename.endswith(".jpg"):
                    url = a.url
                    embeds.append(await utils.invert_converter(url, ctx))
                    y += 1

                if not a.filename.endswith(".png") or not a.filename.endswith(".jpg"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url
            embeds.append(await utils.invert_converter(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(help="Headpat generator :D")
    async def headpat(self, ctx, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author
        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png") or a.filename.endswith(".jpg"):
                    url = a.proxy_url

                    embeds.append(await utils.headpat_converter2(url, ctx))
                    y += 1
                if not a.filename.endswith(".png") or not a.filename.endswith(".jpg"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url

            embeds.append(await utils.headpat_converter2(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    def convert_svg(self, svg_image):
        converted_bytes = cairosvg.svg2png(bytestring=svg_image, scale=6.0)
        buffer = io.BytesIO(converted_bytes)
        buffer.seek(0)
        file = discord.File(buffer, filename="converted.png")
        return file

    @commands.command(brief="Converts svg images to png images")
    async def svgconvert(self, ctx, *, code: codeblock_converter = None):
        if ctx.message.attachments:
            for a in ctx.message.attachments:
                try:
                    convert_time = functools.partial(self.convert_svg, await a.read())
                    file = await self.bot.loop.run_in_executor(None, convert_time)
                    await ctx.send(file=file)

                except Exception as e:
                    await ctx.send(f"couldn't convert that :( due to error: {e}")

        if code:
            try:
                convert_time = functools.partial(self.convert_svg, code.content)
                file = await self.bot.loop.run_in_executor(None, convert_time)
                await ctx.send(file=file)

            except Exception as e:
                await ctx.send(f"couldn't convert that :( due to error: {e}")

        if not code and not ctx.message.attachments:
            await ctx.send("you need svg attachments")

    @commands.command(brief="uses dagpi to make an image of you in jail")
    async def jail(self, ctx, *, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author
        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png"):
                    url = a.url

                    embeds.append(await utils.jail_converter(url, ctx))
                    y += 1
                if not a.filename.endswith(".png"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url
            embeds.append(await utils.jail_converter(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, disable_after=True)
        await menu.send()

    @commands.command(brief="inverts any valid image with jeyyapi")
    async def invert(self, ctx, Member: utils.BetterMemberConverter = None):
        Member = Member or ctx.author

        y = 0
        embeds = []

        if ctx.message.attachments:
            for a in ctx.message.attachments:
                if a.filename.endswith(".png") or a.filename.endswith(".jpg"):
                    url = a.url
                    embeds.append(await utils.invert_converter2(url, ctx))
                    y += 1

                if not a.filename.endswith(".png") or not a.filename.endswith(".jpg"):
                    pass

        if not ctx.message.attachments or y == 0:
            url = (Member.display_avatar.with_format("png")).url
            embeds.append(await utils.invert_converter2(url, ctx))

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="Generates ace attronetry gifs")
    async def ace(self, ctx):
        jeyy_client = jeyyapi.JeyyAPIClient(session=self.bot.session)
        view = utils.AceView(ctx, jeyy_client)
        await ctx.send(content="Please Pick a side to represent:", view=view)


async def setup(bot):
    await bot.add_cog(Image(bot))
