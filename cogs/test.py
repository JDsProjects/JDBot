import asyncio
import collections
import difflib
import itertools
import os
import random
import re
import traceback
import typing

import discord
from better_profanity import profanity
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

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure) and not ctx.author.id in self.bot.testers:
            return await ctx.send("You are not a tester you can apply with ``te*apply_tester``")

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
            await ctx.send("work in progress")
            # time to do things later

            tweets = await self.bot.tweet_client.get_users_tweets(
                username_id,
                max_results=amount,
                user_auth=True,
                expansions=["attachments.media_keys"],
                tweet_fields=["possibly_sensitive", "attachments", "created_at"],
                media_fields=["media_key", "type", "url", "preview_image_url"],
            )
            # not sure if I have everything i need but i need to see what data it can give me
            # tweet_fields may take entities in the future(entities are only needed for video urls and gifs)

        except Exception as e:
            traceback.print_exc()
            return await ctx.send(f"Exception occured at {e}")

        # print(tweets)

        tweet_list = tweets.data

        if not tweet_list:
            return await ctx.send("Couldn't find any tweets.")

        # not sure why this can be None but it can be

        filtered_tweets = list(filter(lambda t: t.possibly_sensitive == False, tweet_list))

        embeds = []

        media = tweets.includes["media"]
        # Twitter likes to make things complicated, so this include the full media object here,
        # while the tweet only has the media key

        for tweet in filtered_tweets:

            tweet_url = f"https://twitter.com/twitter/statuses/{tweet.id}"

            embed = discord.Embed(
                title=f"Tweet!", description=f"{tweet.text}", url=tweet_url, color=0x1DA1F2, timestamp=tweet.created_at
            )
            embed.set_author(name=f"{username.data}", icon_url=image, url=profile_url)
            embed.set_footer(text=f"Requested by {ctx.author}\nJDJG does not own any of the content of the tweets")

            embed.set_thumbnail(url="https://i.imgur.com/zpLkfHo.png")

            # I don't know how to manage the twitter attachments, it may be nsfwish as well
            # hopefully i have all i need to handle twitter's attachments
            print(tweet.attachments)
            # work in progress

            embeds.append(embed)

        menu = utils.Paginator(embeds, ctx=ctx, delete_after=True)
        await menu.send()

        # speacil tool for pagination(with normal, empherall, and dm)

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

        # unknown on actual size limit, but 140 should work as a placeholder

        embed = discord.Embed(title="Inspector Gadget is here!", color=13420741)
        embed.set_image(url="attachment://gadget.png")
        embed.set_footer(text=f"Requested by {ctx.author}")

        # may need a better color that is a inspector gadget color

        image = await asyncio.to_thread(utils.gadget, response)
        file = discord.File(image, filename="gadget.png")
        image.close()

        await ctx.send(embed=embed, file=file)

    @commands.command(brief="gets an image to have sam laugh at")
    async def laugh(self, ctx):
        await ctx.send("WIP")

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
            if re.search(regex, word):
                return {"type": "Server Invite"}

            regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-\_@\.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
            if re.search(regex, word):
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
