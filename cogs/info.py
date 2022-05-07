from discord.ext import commands
import re
import discord
import random
import typing
import emoji
import unicodedata
import textwrap
import contextlib
import io
import asyncio
import async_tio
import itertools
import os
import base64
import secrets
import utils
from difflib import SequenceMatcher
from discord.ext.commands.cooldowns import BucketType
from jishaku.codeblocks import codeblock_converter
import functools


class Info(commands.Cog):
    "Gives you Information about data you are allowed to access"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="gives you info about a guild",
        aliases=[
            "server_info",
            "guild_fetch",
            "guild_info",
            "fetch_guild",
            "guildinfo",
        ],
    )
    async def serverinfo(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
        guild = guild or ctx.guild

        if guild is None:
            await ctx.send("Guild wanted has not been found")

        if guild:
            await utils.guildinfo(ctx, guild)

    @commands.command(
        aliases=["user_info", "user-info", "ui", "whois"],
        brief="a command that gives information on users",
        help="this can work with mentions, ids, usernames, and even full names.",
    )
    async def userinfo(self, ctx, *, user: utils.BetterUserconverter = None):

        user = user or ctx.author

        embed = discord.Embed(title=f"{user}", color=random.randint(0, 16777215), timestamp=ctx.message.created_at)

        embed.set_image(url=user.display_avatar.url)

        view = utils.UserInfoSuper(ctx, user)

        await ctx.send(
            "Pick a way for Mutual Guilds to be sent to you or not if you really don't the mutualguilds",
            embed=embed,
            view=view,
        )

    @commands.command(brief="uploads your emojis into a Senarc Bin link")
    async def look_at(self, ctx):
        if isinstance(ctx.message.channel, discord.TextChannel):
            message_emojis = ""
            for x in ctx.guild.emojis:
                message_emojis = message_emojis + " " + str(x) + "\n"

            paste = await utils.post(self.bot, message_emojis)
            await ctx.send(paste)

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("We can't use that in DMS as it takes emoji regex and puts it into a paste.")

    @commands.command(help="gives the id of the current guild or DM if you are in one.")
    async def guild_get(self, ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.send(content=ctx.guild.id)

        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(ctx.channel.id)

    @commands.command(brief="a command to tell you the channel id", aliases=["GetChannelId"])
    async def this(self, ctx):
        await ctx.send(ctx.channel.id)

    @commands.command(brief="Gives you mention info don't abuse(doesn't mention tho)")
    async def mention(self, ctx, *, user: utils.BetterUserconverter = None):
        user = user or ctx.author

        await ctx.send(
            f"Discord Mention: {user.mention} \nRaw Mention:  {discord.utils.escape_mentions(user.mention)}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(help="fetch invite details")
    async def fetch_invite(self, ctx, *invites: typing.Union[discord.Invite, str]):
        if invites:

            menu = utils.InviteInfoEmbed(invites, ctx=ctx, delete_after=True)
            await menu.send()
        if not invites:
            await ctx.send("Please get actual invites to attempt grab")
            ctx.command.reset_cooldown(ctx)

        if len(invites) > 50:
            await ctx.send(
                "Reporting using more than 50 invites in this command. This is to prevent ratelimits with the api."
            )

            jdjg = await self.bot.try_user(168422909482762240)
            await self.bot.get_channel(855217084710912050).send(
                f"{jdjg.mention}.\n{ctx.author} causes a ratelimit issue with {len(invites)} invites"
            )

    @commands.command(brief="gives info about a file")
    async def file(self, ctx):

        if not ctx.message.attachments:
            await ctx.send(ctx.message.attachments)
            await ctx.send("no file submitted")

        if ctx.message.attachments:
            embed = discord.Embed(title="Attachment info", color=random.randint(0, 16777215))
            for a in ctx.message.attachments:
                embed.add_field(name=f"ID: {a.id}", value=f"[{a.filename}]({a.url})")
                embed.set_footer(text="Check on the url/urls to get a direct download to the url.")
            await ctx.send(embed=embed, content="\nThat's good")

    @commands.command(
        brief="a command to get the avatar of a user",
        help="using the userinfo technology it now powers avatar grabbing.",
        aliases=["pfp", "av"],
    )
    async def avatar(self, ctx, *, user: utils.BetterUserconverter = None):
        user = user or ctx.author

        embed = discord.Embed(color=random.randint(0, 16777215))
        embed.set_author(name=f"{user.name}'s avatar:", icon_url=user.display_avatar.url)

        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(brief="this is a way to get the nearest channel.")
    async def find_channel(self, ctx, *, args=None):
        if args is None:
            await ctx.send("Please specify a channel")

        if args:
            if isinstance(ctx.channel, discord.TextChannel):
                channel = discord.utils.get(ctx.guild.channels, name=args)
                if channel:
                    await ctx.send(channel.mention)
                if channel is None:
                    await ctx.send("Unforantely we haven't found anything")

            if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("You can't use it in a DM.")

    @commands.command(brief="a command to get the closest user.")
    async def closest_user(self, ctx, *, args=None):
        if args is None:
            return await ctx.send("please specify a user")

        if args and not self.bot.users:
            return await ctx.send("There are no users cached :(")

        if args:
            userNearest = discord.utils.get(self.bot.users, name=args)
            user_nick = discord.utils.get(self.bot.users, display_name=args)

            if userNearest is None:
                userNearest = sorted(self.bot.users, key=lambda x: SequenceMatcher(None, x.name, args).ratio())[-1]

            if user_nick is None:
                user_nick = sorted(self.bot.users, key=lambda x: SequenceMatcher(None, x.display_name, args).ratio())[
                    -1
                ]

        if isinstance(ctx.channel, discord.TextChannel):
            member_list = [x for x in ctx.guild.members if x.nick]

            nearest_server_nick = sorted(member_list, key=lambda x: SequenceMatcher(None, x.nick, args).ratio())[-1]

        if isinstance(ctx.channel, discord.DMChannel):

            nearest_server_nick = "You unfortunately don't get the last value(a nickname) as it's a DM."

        await ctx.send(f"Username : {userNearest} \nDisplay name : {user_nick} \nNickname: {nearest_server_nick}")

    @commands.command(help="gives info on default emoji and custom emojis", name="emoji")
    async def emoji_info(self, ctx, *emojis: typing.Union[utils.EmojiConverter, str]):
        if emojis:

            menu = utils.EmojiInfoEmbed(emojis, ctx=ctx, delete_after=True)
            await menu.send()

        if not emojis:
            await ctx.send("Looks like there was no emojis.")

    @commands.command(brief="gives info on emoji_id and emoji image.")
    async def emoji_id(
        self,
        ctx,
        *,
        emoji: typing.Optional[typing.Union[discord.PartialEmoji, discord.Message, utils.EmojiBasic]] = None,
    ):

        if isinstance(emoji, discord.Message):
            emoji_message = emoji.content
            emoji = None

            with contextlib.suppress(commands.CommandError, commands.BadArgument):
                emoji = await utils.EmojiBasic.convert(
                    ctx, emoji_message
                ) or await commands.PartialEmojiConverter().convert(ctx, emoji_message)

        if emoji:
            embed = discord.Embed(description=f" Emoji ID: {emoji.id}", color=random.randint(0, 16777215))
            embed.set_image(url=emoji.url)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Not a valid emoji id.")

    @commands.command()
    async def fetch_content(self, ctx, *, args=None):
        if args is None:
            await ctx.send("please send actual text")

        if args:
            args = discord.utils.escape_mentions(args)
            args = discord.utils.escape_markdown(args, as_needed=False, ignore_links=False)

        for x in ctx.message.mentions:
            args = args.replace(x.mention, f"\{x.mention}")

        emojis = emoji.emoji_lis(args)
        emojis_return = [d["emoji"] for d in emojis]

        for x in emojis_return:
            args = args.replace(x, f"\{x}")

        for x in re.findall(r":\w*:\d*", args):
            args = args.replace(x, f"\{x}")

        await ctx.send(f"{args}", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(brief="gives info about a role.", aliases=["roleinfo"])
    async def role_info(self, ctx, *, role: typing.Optional[discord.Role] = None):

        if role:
            await utils.roleinfo(ctx, role)

        if not role:
            await ctx.send(f"The role you wanted was not found.")


class DevTools(commands.Cog):
    "Helpful commands for developers in general"

    def __init__(self, bot):
        self.bot = bot

    async def rtfm_lookup(self, url=None, *, args=None):

        if not args:
            return url

        else:

            # replace the url and grabbing when frostii ports rtfm to senarc.
            res = await self.bot.session.get(
                "https://repi.openrobot.xyz/search_docs",
                params={"query": args, "documentation": url},
                headers={"Authorization": os.environ["frostiweeb_api"]},
            )

            results = await res.json()

            if not results:
                return f"Could not find anything with {args}."

            else:
                return results

    async def rtfm_send(self, ctx, results):

        if isinstance(results, str):
            await ctx.send(results, allowed_mentions=discord.AllowedMentions.none())

        else:
            embed = discord.Embed(color=random.randint(0, 16777215))

            results = dict(itertools.islice(results.items(), 10))
            embed.description = "\n".join(f"[`{result}`]({results.get(result)})" for result in results)

            reference = utils.reference(ctx.message)
            await ctx.send(embed=embed, reference=reference)

    @commands.command(
        aliases=["rtd", "rtfs", "rtdm"],
        invoke_without_command=True,
        brief="a rtfm command that allows you to lookup at any library we support looking up(using selects)",
    )
    async def rtfm(self, ctx, *, args=None):

        rtfm_dictionary = await self.bot.db.fetch("SELECT * FROM RTFM_DICTIONARY")

        view = utils.RtfmChoice(ctx, rtfm_dictionary, timeout=15.0)

        await ctx.send(content="Please Pick a library you want to parse", view=view)

        await view.wait()

        await ctx.trigger_typing()

        results = await self.rtfm_lookup(url=view.value, args=args)

        await self.rtfm_send(ctx, results)

    def charinfo_converter(self, string):
        digit = f"{ord(string):x}"
        name = unicodedata.name(string, "The unicode was not found")
        return f"`\\U{digit:>08}`: {name} - {string} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"

    @commands.command(brief="Gives you data about charinfo (based on R.danny's command)")
    async def charinfo(self, ctx, *, args=None):

        if not args:
            return await ctx.send("That doesn't help out all :(")

        values = "\n".join(map(self.charinfo_converter, set(args)))

        content = textwrap.wrap(values, width=2000)

        menu = utils.charinfoMenu(content, ctx=ctx, delete_after=True)

        await menu.send()

    @commands.command(brief="a command to view the rtfm DB")
    async def rtfm_view(self, ctx):

        rtfm_dictionary = dict(await self.bot.db.fetch("SELECT * FROM RTFM_DICTIONARY"))

        pag = commands.Paginator(prefix="", suffix="")
        for g in rtfm_dictionary:
            pag.add_line(f"{g} : {rtfm_dictionary.get(g)}")

        menu = utils.RtfmEmbed(pag.pages, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="a command to autoformat your python code to pep8")
    async def pep8(self, ctx):

        modal = utils.CodeBlockView(ctx, timeout=180.0)
        message = await ctx.send(
            "Please Submit the Code Block\nDo you want to use black's line formatter at 120 (i.e. black - l120 .), or just use the default? (i.e black .):",
            view=modal,
        )
        await modal.wait()

        if not modal.value:
            return await ctx.reply("You need to give it code to work with it.", mention_author=False)

        code = codeblock_converter(argument=f"{modal.value}")

        if modal.value2 is None or modal.value2 is False:
            await message.edit(content="Default it is.", view=None)

        if modal.value2 is True:
            await message.edit(content="Speacil Formatting at 120 lines it is.")

        code_conversion = functools.partial(utils.formatter, code.content, bool(modal.value2))
        try:
            code = await self.bot.loop.run_in_executor(None, code_conversion)

        except Exception as e:
            return await message.edit(content=f"Error Ocurred with {e}")

        embed = discord.Embed(
            title="Reformatted with Black",
            description=f"code returned: \n```python\n{code}```",
            color=random.randint(0, 16777215),
        )
        embed.set_footer(text="Make sure you use python code, otherwise it will not work properly.")
        await message.edit(embed=embed)

    @commands.command(brief="grabs your pfp's image")
    async def pfp_grab(self, ctx):

        if_animated = ctx.author.display_avatar.is_animated()

        save_type = ".gif" if if_animated else ".png"

        file = await ctx.author.display_avatar.to_file(filename=f"pfp{save_type}")
        try:
            await ctx.send(content="here's your avatar:", file=file)

        except:
            await ctx.send("it looks like it couldn't send the pfp due to the file size.")

    @commands.command(brief="Gives info on pypi packages")
    async def pypi(self, ctx, *, args=None):
        # https://pypi.org/simple/

        if args:
            pypi_response = await self.bot.session.get(f"https://pypi.org/pypi/{args}/json")
            if pypi_response.ok:

                pypi_response = await pypi_response.json()

                pypi_data = pypi_response["info"]

                embed = discord.Embed(
                    title=f"{pypi_data.get('name') or 'None provided'} {pypi_data.get('version') or 'None provided'}",
                    url=f"{pypi_data.get('release_url') or 'None provided'}",
                    description=f"{pypi_data.get('summary') or 'None provided'}",
                    color=random.randint(0, 16777215),
                )

                embed.set_thumbnail(url="https://i.imgur.com/oP0e7jK.png")

                embed.add_field(
                    name="**Author Info**",
                    value=f"**Author Name:** {pypi_data.get('author') or 'None provided'}\n**Author Email:** {pypi_data.get('author_email') or 'None provided'}",
                    inline=False,
                )
                embed.add_field(
                    name="**Package Info**",
                    value=f"**Download URL**: {pypi_data.get('download_url') or 'None provided'}\n**Documentation URL:** {pypi_data.get('docs_url') or 'None provided'}\n**Home Page:** {pypi_data.get('home_page') or 'None provided'}\n**Keywords:** {pypi_data.get('keywords')  or 'None provided'}\n**License:** {pypi_data.get('license')  or 'None provided'}",
                    inline=False,
                )

                await ctx.send(embed=embed)

            else:
                await ctx.send(
                    f"Could not find package **{args}** on pypi.", allowed_mentions=discord.AllowedMentions.none()
                )

        else:
            await ctx.send("Please look for a library to get the info of.")

    @commands.command(brief="make a quick bot invite with 0 perms")
    async def invite_bot(self, ctx, *, user: typing.Optional[discord.User] = None):
        user = user or ctx.author

        if not user.bot:
            return await ctx.send("That's not a legit bot")

        invite = discord.utils.oauth_url(client_id=user.id, scopes=("bot",))
        slash_invite = discord.utils.oauth_url(client_id=user.id)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label=f"{user.name}'s Normal Invite", url=invite, style=discord.ButtonStyle.link)
        )
        view.add_item(
            discord.ui.Button(
                label=f"{user.name}'s Invite With Slash Commands", url=slash_invite, style=discord.ButtonStyle.link
            )
        )

        await ctx.send(f"Invite with slash commands and the bot scope or only with a bot scope:", view=view)

    @commands.command(brief="gets you a guild's icon", aliases=["guild_icon"])
    async def server_icon(self, ctx, *, guild: typing.Optional[discord.Guild] = None):
        guild = guild or ctx.guild

        if not guild:
            return await ctx.send("no guild to get the icon of.")

        await ctx.send(f"{guild.icon.url if guild.icon else 'No Url for This Guild, I am sorry dude :('}")

    @commands.command(brief="some old fooz command..")
    async def fooz(self, ctx, *, args=None):
        if not args:
            await ctx.send("success")

        if args:
            await ctx.send("didn't use it properly :(")

    @commands.command(brief="puts the message time as a timestamp")
    async def message_time(self, ctx):

        embed = discord.Embed(title="Message Time", color=random.randint(0, 16777215), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"{ctx.message.id}")

        await ctx.send(content=f"Only here cause JDJG Bot has it and why not have it here now.", embed=embed)

    @commands.command(brief="converts info about colors for you.", invoke_without_command=True)
    async def color(self, ctx, *, color: utils.ColorConverter = None):

        if not color:
            return await ctx.send("you need to give me a color to use.")

        await ctx.send(f"Hexadecimal: {color} \nValue : {color.value} \nRGB: {color.to_rgb()}")

    @commands.command(brief="a command that tells a user creation time.")
    async def created_at(self, ctx, *, user: utils.BetterUserconverter = None):
        user = user or ctx.author

        creation_info = f"{discord.utils.format_dt(user.created_at, style = 'd')}\n{discord.utils.format_dt(user.created_at, style = 'T')}"

        await ctx.send(
            f"\nName : {user}\nMention : {user.mention} was created:\n{creation_info}\nRaw Version: ```{creation_info}```",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(brief="a command that makes a fake user id based on the current time.")
    async def fake_user_id(self, ctx):

        await ctx.send(f"User id: {utils.generate_snowflake()}")

    @commands.command(brief="gives information on snowflakes")
    async def snowflake_info(self, ctx, *, snowflake: typing.Optional[utils.ObjectPlus] = None):

        if not snowflake:
            await ctx.send(
                "you either returned nothing or an invalid snowflake now going to the current time for information."
            )

        # change objectplus convert back to the before(discord.Object), same thing with utls.ObjectPlus, if edpy adds my pull request into the master.

        generated_time = await utils.ObjectPlusConverter().convert(ctx, argument=f"{int(utils.generate_snowflake())}")

        snowflake = snowflake or generated_time

        embed = discord.Embed(title="❄️ SnowFlake Info:", color=5793266)

        embed.add_field(
            name="Created At:",
            value=f"{discord.utils.format_dt(snowflake.created_at, style = 'd')}\n{discord.utils.format_dt(snowflake.created_at, style = 'T')}",
        )

        embed.add_field(name="Worker ID:", value=f"{snowflake.worker_id}")

        embed.add_field(name="Process ID:", value=f"{snowflake.process_id}")

        embed.add_field(name="Increment:", value=f"{snowflake.increment_id}")

        embed.set_footer(text=f"Snowflake ID: {snowflake.id}")

        await ctx.send(embed=embed)

    @commands.command(brief="Generates a fake token from the current time")
    async def fake_token(self, ctx):

        object = discord.Object(utils.generate_snowflake())

        first_encoded = base64.b64encode(f"{object.id}".encode())
        first_bit = first_encoded.decode()

        timestamp = int(object.created_at.timestamp() - 129384000)
        d = timestamp.to_bytes(4, "big")
        second_bit_encoded = base64.standard_b64encode(d)
        second_bit = second_bit_encoded.decode().rstrip("==")

        last_bit = secrets.token_urlsafe(20)

        embed = discord.Embed(
            title=f"Newly Generated Fake Token",
            description=f"ID: ``{object.id}``\nCreated at : \n{discord.utils.format_dt(object.created_at, style = 'd')}\n{discord.utils.format_dt(object.created_at, style = 'T')}",
        )
        embed.add_field(name="Generated Token:", value=f"``{first_bit}.{second_bit}.{last_bit}``")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send("We generated a fake token :clap::", embed=embed)

    @commands.cooldown(1, 60, BucketType.user)
    @commands.command(brief="makes a request to add a bot to the test guild")
    async def addbot(self, ctx, *, user: typing.Optional[discord.User] = None):

        user = user or ctx.author

        if not user.bot:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Please Use A **Bot** ID, not a **User** ID.")

        modal = utils.AddBotView(ctx, timeout=180.0)
        message = await ctx.send("Please Tell us the reason you want to add your bot to the Test Guild:", view=modal)
        await modal.wait()

        if modal.value is None:
            ctx.command.reset_cooldown(ctx)
            return await message.edit(content="Provide a reason why you want your bot added to your guild")

        guild = self.bot.get_guild(438848185008390158)
        member = await self.bot.try_member(guild, ctx.author.id)
        if member is None:

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label=f"Test Guild Invite",
                    url="https://discord.gg/hKn8qgCDzK",
                    style=discord.ButtonStyle.link,
                    row=1,
                )
            )
            return await message.edit(
                content="Make sure to join the guild linked soon... then rerun the command. If you are in the guild contact the owner(the owner is listed in the owner command)",
                view=view,
            )

        embed = discord.Embed(
            title="Bot Request",
            colour=discord.Colour.blurple(),
            description=f"reason: \n{modal.value}\n\n[Invite URL]({discord.utils.oauth_url(client_id = user.id, scopes=('bot',))})",
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Author", value=f"{ctx.author} (ID: {ctx.author.id})", inline=False)
        embed.add_field(name="Bot", value=f"{user} (ID: {user.id})", inline=False)

        embed.set_footer(text=ctx.author.id)
        embed.set_author(name=user.id, icon_url=user.display_avatar.with_format("png"))

        jdjg = self.bot.get_user(168422909482762240)
        benitz = self.bot.get_user(529499034495483926)

        await self.bot.get_channel(816807453215424573).send(content=f"{jdjg.mention} {benitz.mention}", embed=embed)

        await ctx.reply(
            f"It appears adding your bot worked. \nIf you leave your bot will be kicked, unless you have an alt there, a friend, etc. \n(It will be kicked to prevent raiding and taking up guild space if you leave). \nYour bot will be checked out. {jdjg} will then determine if your bot is good to add to the guild. Make sure to open your Dms to JDJG, so he can dm you about the bot being added. \nIf you don't add him, your bot will be denied."
        )

    @commands.command(
        brief="a command that takes a url and sees if it's an image (requires embed permissions at the moment)."
    )
    async def image_check(self, ctx):

        await ctx.send(
            "Please wait for discord to edit your message, if it does error about not a valid image, please send a screenshot of your usage and the bot's message."
        )
        await asyncio.sleep(5)

        images = list(filter(lambda e: e.type == "image", ctx.message.embeds))

        if not images or not ctx.message.embeds:
            return await ctx.send(
                "you need to pass a url with an image, if you did, then please run again. This is a discord issue, and I do not want to wait for discord to change its message."
            )

        await ctx.send(f"You have {len(images)} / {len(ctx.message.embeds)} links that are valid images.")

    @commands.command(brief="Gives info on npm packages")
    async def npm(self, ctx, *, args=None):

        if args:
            npm_response = await self.bot.session.get(f"https://registry.npmjs.com/{args}")

            if npm_response.ok:
                npm_response = await npm_response.json()

                data = utils.get_required_npm(npm_response)
                await ctx.send(embed=utils.npm_create_embed(data))

            else:
                await ctx.send(
                    f"Could not find package **{args}** on npm.", allowed_mentions=discord.AllowedMentions.none()
                )

        else:
            await ctx.send("Please look for a library to get the info of.")

    @commands.cooldown(1, 30, BucketType.user)
    @commands.command(
        brief="runs some code in a sandbox(based on Soos's Run command)", aliases=["eval", "run", "sandbox"]
    )
    async def console(self, ctx, *, code: codeblock_converter = None):

        if not code:
            return await ctx.send("You need to give me some code to use, otherwise I can not determine what it is.")

        if not code.language:
            return await ctx.send("You Must provide a language to use")

        if not code.content:
            return await ctx.send("No code provided")

        tio = await async_tio.Tio(session=self.bot.session)

        output = await tio.execute(f"{code.content}", language=f"{code.language}")

        text_returned = (
            f"```{code.language}\n{output}```"
            if len(f"{output}") < 200
            else await utils.post(self.bot, code=f"{output}")
        )

        embed = discord.Embed(
            title=f"Your code exited with code {output.exit_status}", description=f"{text_returned}", color=242424
        )

        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)

        embed.set_footer(text="Powered by Tio.run")

        await ctx.send(content="I executed your code in a sandbox", embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
    await bot.add_cog(DevTools(bot))
