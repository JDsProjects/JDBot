import asyncio
import collections
import difflib
import itertools
import os
import random
import re
import time
import traceback
import typing

import discord
from better_profanity import profanity
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import utils


class Test(commands.Cog):
    """A cog to have people test new commands, or wip ones"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="this command will error by sending no content")
    async def te(self, ctx):
        await ctx.send("this command will likely error...")
        await ctx.send("")

    @commands.command(brief="WIP command to verify")
    async def verify(self, ctx):
        await ctx.send("WIP will make this soon..")

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.testers

    @commands.command(
        brief="a command to email you(work in progress)",
        help="This command will email your email, it will automatically delete in guilds, but not in DMs(as it's not necessary",
    )
    async def email(self, ctx, *args):
        print(args)
        await ctx.send("WIP")
        # will use modals on final
        # :)

    @commands.command(brief="WIP thing for birthday set up lol")
    async def birthday_setup(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="sleep time")
    async def set_sleeptime(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="wakeup time")
    async def set_wakeuptime(self, ctx):
        await ctx.send("WIP")

    @commands.command(brief="gets tweets from a username")
    async def get_tweet(self, ctx, amount: typing.Optional[int] = None, username=None):
        amount = amount or 10

        if not username:
            return await ctx.send("You Need to pick a username.")

        if amount > 30:
            return await ctx.send("You can only get 30 tweets at a time.")

        try:
            username = await self.bot.tweet_client.get_user(username=username, user_fields=["profile_image_url"])

        except Exception as e:
            traceback.print_exc()
            return await ctx.send(f"Exception occured at {e}")

        if username.data is None:
            return await ctx.send("Couldn't find that user.")

        username_id = username.data.id
        profile_url = f"https://twitter.com/i/user/{username_id}"
        # appreantly this works

        image = username.data.profile_image_url

        try:
            # time to do things later

            response = await self.bot.tweet_client.get_users_tweets(
                username_id,
                max_results=amount,
                user_auth=True,
                expansions=["attachments.media_keys"],
                tweet_fields=["possibly_sensitive", "attachments", "created_at"],
                media_fields=["media_key", "type", "url", "preview_image_url", "variants"],
            )
            # not sure if I have everything i need but i need to see what data it can give me
            # tweet_fields may take entities in the future(entities are only needed for video urls and gifs)

        except Exception as e:
            traceback.print_exc()
            return await ctx.send(f"Exception occured at {e}")

        wrapped_response = utils.TweetWrapper(response)

        wrapped_tweets = wrapped_response.tweets

        if not wrapped_tweets:
            return await ctx.send("Couldn't find any tweets.")

        # not sure why this can be None but it can be

        filtered_tweets = list(filter(lambda t: t.possibly_sensitive == False, wrapped_tweets))

        menu = utils.TweetsPaginator(
            ctx=ctx,
            delete_after=True,
            tweets=filtered_tweets,  # type: ignore
            author_icon=image,
            author_url=profile_url,
            author_name=username.data,
        )

        view = utils.TweetsDestinationHandler(ctx=ctx, pagintor=menu)

        view.message = await ctx.send("Please pick a way tweets are sent to you\nMethods are below:", view=view)

        # when fully completed move to extra.py(not the old Twitter Cog.), will also use modals, maybe

    @commands.command(brief="adds a text to Go Go Gadget or Wowzers Username")
    async def gadget(self, ctx, *, text=None):
        if not text:
            return await ctx.send("You need to give text for me to process")

        if profanity.contains_profanity(text):
            response = f"Wowsers! \n{ctx.author} your gadget is really inapporiate"

            if profanity.contains_profanity(response):
                response = f"Wowzers! \nYour name is really inapporiate"

        else:
            response = f"Go Go Gadget {text}"

        if len(response) > 140:
            response = "Wowzers! \nYour name is too long"

            # doesn't check if it's from the actual user response or the name itself

        # unknown on actual size limit, but 140 should work as a placeholder

        embed = discord.Embed(title="Inspector Gadget is here!", color=13420741)
        embed.set_image(url="attachment://gadget.png")
        embed.set_footer(text=f"Requested by {ctx.author}")

        # may need a better color that is a inspector gadget color

        image = await asyncio.to_thread(utils.gadget, response)
        file = discord.File(image, filename="gadget.png")
        image.close()

        await ctx.send(embed=embed, file=file)

    def test(self, image):
        import io

        f = io.BytesIO(image)
        f.seek(0)

        return f

    @commands.command(brief="checks attachment stuff")
    async def attachment(
        self,
        ctx,
        *assets: utils.image_union2,
    ):
        images = await utils.asset_converter(ctx, assets)

        files = [asyncio.to_thread(self.test, await image.read()) for image in images]
        done, _ = await asyncio.wait(files)

        files = [discord.File(file.result(), "image.png") for file in done]

        await ctx.send(files=files)

        # use a copy of this soon with my own invert version

    @commands.command(brief="invert images")
    async def invert(
        self,
        ctx,
        *assets: utils.image_union2,
    ):
        images = await utils.asset_converter(ctx, assets)

        files = [asyncio.to_thread(utils.invert, await image.read()) for image in images]

        time_before = time.perf_counter()
        done, _ = await asyncio.wait(files)

        files = [file.result() for file in done]
        time_after = time.perf_counter()

        await ctx.send(content=f"Invert ran in {int((time_after - time_before)*1000)} ms", files=files)

    @commands.command(brief="invert images using wand")
    async def invert2(
        self,
        ctx,
        *assets: utils.image_union2,
    ):
        images = await utils.asset_converter(ctx, assets)

        files = [asyncio.to_thread(utils.invert2, await image.read()) for image in images]

        time_before = time.perf_counter()
        done, _ = await asyncio.wait(files)

        files = [file.result() for file in done]
        time_after = time.perf_counter()

        await ctx.send(content=f"Invert2 ran in {int((time_after - time_before)*1000)} ms", files=files)

    @commands.command(brief="makes images look really crusty and old")
    async def crust(
        self,
        ctx,
        *assets: utils.image_union2,
    ):
        images = await utils.asset_converter(ctx, assets)

        files = [asyncio.to_thread(utils.crusty, await image.read()) for image in images]

        time_before = time.perf_counter()
        done, _ = await asyncio.wait(files)

        files = [file.result() for file in done]
        time_after = time.perf_counter()

        await ctx.send(content=f"crusty ran in {int((time_after - time_before)*1000)} ms", files=files)

    @commands.cooldown(1, 15, BucketType.user)
    @commands.command(brief="gets an image to have sam laugh at")
    async def laugh(
        self,
        ctx,
        assets: commands.Greedy[utils.image_union],
        *,
        flag: typing.Optional[typing.Literal["--style 2"]],
    ):
        images = await utils.asset_converter(ctx, assets)

        epic = None

        if flag:
            epic = utils.laugh

        else:
            epic = utils.laugh2

        files = [asyncio.to_thread(epic, await image.read()) for image in images]
        done, _ = await asyncio.wait(files)

        files = [file.result() for file in done]
        files = [discord.File(image, f"laugh.{image_type}") for image, image_type in files]

        await ctx.send(files=files)

    @commands.command(help="takes a .png attachment or your avatar and makes a triggered version.")
    async def triggered(self, ctx, *assets: utils.image_union2):
        await ctx.send("Wip right now")
        # menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        # await menu.send()

        # will be updating the old one soon

    @commands.command(brief="add emoji to your guild lol")
    async def emoji_add(self, ctx):
        await ctx.send("WIP")
        # look at the JDJG Bot orginal

    @commands.command(brief="scans statuses/activities to see if there is any bad ones.")
    @commands.has_permissions(manage_messages=True)
    async def scan_status(self, ctx):
        def scan(word):
            if profanity.contains_profanity(word):
                return {"type": "Profanity"}
            regex = re.compile(r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")
            if regex.search(word):
                return {"type": "Server Invite"}

            regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-\_@\.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
            if regex.search(word):
                return {"type": "External Link"}
            else:
                return None

        pages = []
        i = 0
        fi = 1
        count = [mem.activity for mem in ctx.guild.members if mem.activity is not None]
        count = len([scan(act.name) for act in count if scan(act.name) is not None])
        chunck = "**Total Members With A Bad Status: {}**\n\n".format(count)
        for member in ctx.guild.members:
            act = member.activity
            if act is not None:
                sc = scan(act.name)
                if sc is not None:
                    chunck += f"{fi}) **{member}** ({member.mention}) - **Reason**: {sc['type']}\n"
                    if i == 10:
                        pages.append(chunck)
                        chunck = "**Total Members With A Bad Status: {}**\n\n".format(count)
                        i = 0
                    i += 1
                    fi += 1

        pages.append(chunck)

        menu = utils.ScanStatusEmbed(pages, ctx=ctx, delete_after=True)
        await menu.send()

    @commands.command(brief="sets logs for a guild", name="logging")
    async def _logging(self, ctx):
        await ctx.send("logging wip.")

    # look at global_chat stuff for global_chat features, rank for well rank, add an update system too, add cc_ over. nick too, as well as kick and ban, ofc unban and other guild ban moderation stuff. Port over emoji_check but public and make that do it's best to upload less than 256 kB, try to and ofc an os emulation mode, as well as update mode, and nick.

    # Unrelated to Urban:
    # https://discordpy.readthedocs.io/en/master/api.html?highlight=interaction#discord.InteractionResponse.send_message
    # https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild.query_members

    # spyco data table in my sql database

    @commands.command(brief="a test of a new paginator :)")
    async def test_pagination(self, ctx):
        buttons = {
            "STOP": utils.PaginatorButton(emoji="<:stop:959853381885775902>", style=discord.ButtonStyle.secondary),
            "RIGHT": utils.PaginatorButton(emoji="<:next:959851091506364486>", style=discord.ButtonStyle.secondary),
            "LEFT": utils.PaginatorButton(emoji="<:back:959851091284095017>", style=discord.ButtonStyle.secondary),
            "LAST": utils.PaginatorButton(emoji="<:last:959851091330220042>", style=discord.ButtonStyle.secondary),
            "FIRST": utils.PaginatorButton(emoji="<:start:959851091502190674>", style=discord.ButtonStyle.secondary),
        }
        pages = [discord.Embed(title="eh")] * 10
        menu = utils.Paginator(pages, ctx=ctx, buttons=buttons, delete_after=True)
        await menu.send()

    @commands.command()
    async def tags(self, ctx):
        await ctx.send("WIP")

        # more tag stuff soon just got to figure out my queries
        # some of this should just be tag stuff (as in a group, tags should just be the list type)

    @commands.command()
    async def reminders(self, ctx):
        await ctx.send("WIP")
        # soon to be a reminders like thing like R.danny's ofc with my own code

    @commands.command(brief="Notes so you can refer back to them for important stuff")
    async def notes(self, ctx):
        await ctx.send("WIP")
        # Note this is not like todo, todo is for small things, notes is for big things

    @app_commands.command(description="Makes a command to convert temperature")
    async def convert_temperature(
        self,
        interaction: discord.Interaction,
        system: utils.Temperature,
        temperature: int,
    ):
        temps = utils.Temperature.convert_to(system, temperature)

        await interaction.response.send_message(
            f"temperature :\nCelsius : {temps.celsius} \nFahrenheit: {temps.fahrenheit}  \nKelvin : {temps.kelvin}"
        )

    @convert_temperature.error
    async def convert_temperature_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"{error}! Please Send to this to my developer", ephemeral=True)
        print(interaction.command)
        traceback.print_exc()


class Slash(commands.Cog):
    """A Testing Category for Slash Commands"""

    def __init__(self, bot):
        self.bot = bot


class CommandFinder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = discord.app_commands.ContextMenu(
            name="Find Nearest Command",
            callback=self.find_command,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def find_command(self, interaction: discord.Interaction, message: discord.Message) -> None:
        context = await self.bot.get_context(message)
        await interaction.response.defer(ephemeral=True)

        if (context.valid) == False and context.prefix != None and context.command is None and context.prefix != "":
            args = context.invoked_with

            all_commands = list(self.bot.walk_commands())
            command_names = [f"{x}" for x in await utils.filter_commands(context, all_commands)]

            matches = difflib.get_close_matches(args, command_names)

            if not matches:
                await interaction.followup.send(f"I found nothing, sorry.", ephemeral=True)

            elif matches:
                await interaction.followup.send(f"Did you mean... `{matches[0]}`?", ephemeral=True)

        elif context.command and context.valid:
            await interaction.followup.send(f"Found `{context.command.name}`", ephemeral=True)

        else:
            await interaction.followup.send("This message isn't a command, sorry.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Test(bot))
    await bot.add_cog(Slash(bot))
    await bot.add_cog(CommandFinder(bot))
