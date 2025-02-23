import collections
import io
import os
import random

import aiohttp
import asyncdagpi
import discord
import filetype
import somerandomapi


async def roleinfo(ctx, role):
    role_members = collections.Counter([u.bot for u in role.members])
    role_bots = role_members[True]
    role_users = role_members[False]

    if role.tags:
        role_bot_id = role.tags.bot_id

    if not role.tags:
        role_bot_id = None

    role_time = f"{discord.utils.format_dt(role.created_at, style = 'd')}{discord.utils.format_dt(role.created_at, style = 'T')}"

    embed = discord.Embed(title=f"{role} Info:", color=random.randint(0, 16777215))
    embed.add_field(name="Mention:", value=f"{role.mention}")
    embed.add_field(name="ID:", value=f"{role.id}")
    embed.add_field(name="Created at:", value=f"{role_time}")

    embed.add_field(name="Member Count:", value=f"Bot Count : {role_bots} \nUser Count : {role_users}")

    embed.add_field(name="Position Info:", value=f"Position : {role.position} \nHoisted : {role.hoist}")

    embed.add_field(
        name="Managed Info:",
        value=f"Managed : {role.managed} \nBot : {role.is_bot_managed()} \nBot ID : {role_bot_id} \nDefault : {role.is_default()} \nBooster Role : {role.is_premium_subscriber()} \nIntegrated : {role.is_integration()} \nMentionable : {role.mentionable} ",
    )

    embed.add_field(name="Permissions:", value=f"{role.permissions.value}")
    embed.add_field(name="Color:", value=f"{role.colour}")

    embed.set_thumbnail(url="https://i.imgur.com/liABFL4.png")

    embed.set_footer(text=f"Guild: {role.guild}")

    await ctx.send(embed=embed)


async def cdn_upload(bot, image_bytes):

    if isinstance(image_bytes, bytes):
        image_copy = io.BytesIO(image_bytes)

    else:
        image_copy = io.BytesIO(image_bytes.getvalue())

    form = aiohttp.FormData()
    form.add_field("file", image_bytes, content_type="application/octet-stream")
    # debate about the content_type exists, but it seems to be fine, so I will leave for now.
    resp = await bot.session.post(
        "https://cdn.jdjgbot.xyz/upload", data=form, headers={"Authorization": os.environ["cdn_key"]}
    )
    returned_data = await resp.json()

    image_copy.seek(0)

    kind = filetype.guess(image_copy)

    ext = kind.extension if kind else "gif"

    url = f"https://cdn.jdjgbot.xyz/image/{returned_data.get('keys')[0]}.{ext}?opengraph_pass=true"
    # I have to do this opengraph pass thing because the cdn is a bit weird and doesn't like it if I don't
    # because opengraph is enabled, I have to do this.

    bot.images.append(returned_data.get("keys")[0])

    return url


async def triggered_converter(url, ctx):
    sr_client = ctx.bot.sr_client
    image = await sr_client.canvas.overlay(str(url), somerandomapi.CanvasOverlay.TRIGGERED)

    url = await cdn_upload(ctx.bot, await image.read())

    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"Triggered gif requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
    embed.set_image(url=url)
    embed.set_footer(text="powered by some random api")
    return embed


async def headpat_converter(url, ctx, jeyy_client):
    embed = discord.Embed(color=random.randint(0, 16777215))

    try:
        client = jeyy_client
        image = await client.patpat(url)

    except Exception as e:
        print(e)
        await ctx.send("the api failed on us. Please contact the Bot owner if this is a perstient issue.")

        embed.set_author(name=f"Image requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
        embed.set_image(url=url)
        embed.set_footer(text="An Unexcepted Error Occured")
        return embed

    url = await cdn_upload(ctx.bot, image)
    # I am aware of the cdn issues, will be fixed soon
    # cdn stuff will change too cause the creator of imoog is making a better python version.
    embed.set_author(name=f"Headpat gif requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
    embed.set_image(url=url)
    embed.set_footer(text="powered by some jeyyapi")

    return embed


def create_channel_permission(ctx):
    return ctx.author.guild_permissions.manage_channels


def clear_permission(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        return ctx.author.guild_permissions.manage_messages

    if isinstance(ctx.channel, discord.DMChannel):
        return False


async def headpat_converter2(url, ctx):
    dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session=ctx.bot.session)
    image = await dagpi_client.image_process(asyncdagpi.ImageFeatures.petpet(), str(url))

    url = await cdn_upload(ctx.bot, image.image)
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"Headpat gif requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
    embed.set_image(url=url)
    embed.set_footer(text="powered by dagpi")
    return embed


async def jail_converter(url, ctx):
    dagpi_client = asyncdagpi.Client(os.environ["dagpi_key"], session=ctx.bot.session)
    image = await dagpi_client.image_process(asyncdagpi.ImageFeatures.jail(), str(url))
    url = await cdn_upload(ctx.bot, image.image)
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name=f"Jail Image requested by {ctx.author}", icon_url=(ctx.author.display_avatar.url))
    embed.set_image(url=url)
    embed.set_footer(text="powered by dagpi")

    return embed
