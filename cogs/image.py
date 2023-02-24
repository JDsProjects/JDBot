import asyncio
import functools
import io
import os
import random

import asuna_api
import asyncdagpi
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

    async def cog_load(self):
        self.jeyy_client = jeyyapi.JeyyAPIClient(session=self.bot.session)
        self.sr_client = sr_api.Client(session=self.bot.session)
        self.dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session=self.bot.session)
        self.asuna = asuna_api.Client(session=self.bot.session)

    @commands.command(brief="a command to slap someone", help="this sends a slap gif to the target user")
    async def slap(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        url = await self.asuna.get_gif("slap")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} slapped you! Ow...", icon_url=person.display_avatar.url)
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them... likely didn't make us able to dm them or they blocked us.")

    @commands.command(brief="a command to look up foxes", help="this known as wholesome fox to the asuna api")
    async def fox2(self, ctx):
        url = await self.asuna.get_gif("wholesome_foxes")
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{ctx.author} requested a wholesome fox picture", icon_url=ctx.author.display_avatar.url)

        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")
        await ctx.send(embed=embed)

    @commands.command(brief="another command to give you pat gifs", help="powered using the asuna api")
    async def pat2(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        url = await self.asuna.get_gif("pat")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} patted you! *pat pat pat*", icon_url=person.display_avatar.url)
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(brief="a command to give you pat gifs", help="using the sra api it gives you pat gifs")
    async def pat(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        image = await self.sr_client.get_gif("pat")
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} patted you", icon_url=person.display_avatar.url)
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(brief="a hug command to hug people", help="this the first command to hug.")
    async def hug(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        image = await self.sr_client.get_gif("hug")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} hugged you! Awwww...", icon_url=person.display_avatar.url)
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(
        brief="uses our headpat program to pat you", help="a command that uses jeyyapi to make a headpat of you."
    )
    async def headpat2(self, ctx, *, Member: utils.SuperConverter = commands.Author):
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
    async def hug2(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        url = await self.asuna.get_gif("hug")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} super hugged you!", icon_url=person.display_avatar.url)
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed DM'ing them...")

    @commands.command(
        brief="a kiss command",
        help="a command where you can target a user or pick yourself to get a kiss gif( I don't know why I have this)",
    )
    async def kiss(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        url = await self.asuna.get_gif("kiss")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} kissed you", icon_url=person.display_avatar.url)
        embed.set_image(url=url.url)
        embed.set_footer(text="Why did I make this command? powered using the asuna.ga api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(brief="a command to get a neko", help="using the asuna.ga api you will get these images")
    async def neko(self, ctx):
        url = await self.asuna.get_gif("neko")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{ctx.author} requested a neko picture", icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=url.url)
        embed.set_footer(text="powered using the asuna.ga api")
        await ctx.send(embed=embed)

    @commands.command(
        brief="a command to send wink gifs", wink="you select a user to send it to and it will send it to you lol"
    )
    async def wink(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        image = await self.sr_client.get_gif("wink")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{person} winked at you", icon_url=person.display_avatar.url)
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
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
        r = await self.bot.session.get("https://api.waifu.im/search/?is_nsfw=false&many=false&full=false")
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
    async def facepalm(self, ctx, *, Member: utils.SuperConverter = commands.Author):
        if Member.id == ctx.author.id:
            person = self.bot.user
            target = ctx.author

        if Member.id != ctx.author.id:
            person = ctx.author
            target = Member

        image = await self.sr_client.get_gif("face-palm")

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{target} you made {person} facepalm", icon_url=person.display_avatar.url)
        embed.set_image(url=image.url)
        embed.set_footer(text="powered by some random api")

        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=target.mention, embed=embed)

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                await target.send(content=target.mention, embed=embed)
            except discord.Forbidden:
                await ctx.author.send("Failed Dming them...")

    @commands.command(help="gives a random objection", aliases=["obj", "ob", "object"])
    async def objection(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/objection")
        res = await r.json()
        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{ctx.author} yelled OBJECTION!", icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=res["url"])
        embed.set_footer(text="Powered By Senarc Api!")
        await ctx.send(embed=embed)

    @commands.command(help="gives the truth about opinions(may offend)", aliases=["opinion"])
    async def opinional(self, ctx):
        r = await self.bot.session.get("https://api.senarc.net/misc/opinional")
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

    @commands.command(help="Headpat generator :D")
    async def headpat(self, ctx, Member: utils.SuperConverter = commands.Author):
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

    async def convert_svg(self, blob):
        rsvg = "rsvg-convert --width=250"
        proc = await asyncio.create_subprocess_shell(
            rsvg, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate(blob)

        if len(stderr) > 0:
            error = stderr.decode()
            raise Exception(error)

        return io.BytesIO(stdout)

    async def svg_convert(self, attachments):
        svgs = []

        for attachment in attachments:
            if attachment.content_type in ("image/svg+xml", "image/svg+xml; charset=utf-8"):
                svgs.append(attachment)

        return svgs

    @commands.command(brief="Converts svg images to png images")
    async def svgconvert(self, ctx, *, code: codeblock_converter = None):
        svgs = await self.svg_convert(ctx.message.attachments)

        if code:
            value = bytes(code.content, "utf-8")
            svg_code = io.BytesIO(value)
            svg_code.seek(0)

            svgs.append(svg_code)

        if not svgs:
            return await ctx.send("you need svg attachments")

        files = [self.convert_svg(await svg.read()) for svg in svgs if isinstance(svg, discord.Attachment)]
        files2 = [self.convert_svg(svg.read()) for svg in svgs if isinstance(svg, io.BytesIO)]

        files = files + files2

        done, _ = await asyncio.wait(files)

        print(done)

        files = [discord.File(file.result(), "converted.png") for file in done]

        await ctx.send(files=files)

    @commands.command()
    async def call_text(self, ctx, *, args=None):
        args = args or "Test"

        if len(args) > 500:
            return await ctx.send("Please try again with shorter text.")

        args = args or "You called No one :("

        image = await asyncio.to_thread(utils.call_text, args)

        url = await utils.cdn_upload(ctx.bot, image)
        image.close()

        embed = discord.Embed(title=f"Called Text", color=random.randint(0, 16777215), url=url)
        embed.set_image(url=url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

    @commands.command(brief="uses dagpi to make an image of you in jail")
    async def jail(self, ctx, *, Member: utils.SuperConverter = commands.Author):
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

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="Generates ace attronetry gifs")
    async def ace(self, ctx):
        view = utils.AceView(ctx, self.jeyy_client)
        await ctx.send(content="Please Pick a side to represent:", view=view)

    @commands.command(brief="half inverts an image using jeyy's api")
    async def half_invert(
        self,
        ctx,
        *assets: utils.image_union2,
    ):
        images = await utils.asset_converter(ctx, assets)

        jeyy_client = self.jeyy_client

        files = [jeyy_client.half_invert(image) for image in images]
        done, _ = await asyncio.wait(files)

        files = [file.result() for file in done]
        files = [discord.File(image, "half_inverted.gif") for image in files]

        await ctx.send(files=files)


async def setup(bot):
    await bot.add_cog(Image(bot))
