import textwrap
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

font = ImageFont.truetype("assets/fonts/verdana_edited.ttf", 35)
# should be able to place it here


def call_text(text) -> BytesIO:

    text = textwrap.fill(text, 33)
    f = BytesIO()

    with Image.open("assets/images/calling_template.jpg") as image:

        draw = ImageDraw.Draw(image)
        draw.text((5, 5), text, font=font, fill="black")

        image.save(f, "PNG")

    f.seek(0)
    return f


def gadget(text) -> BytesIO:

    text = textwrap.fill(text, 30)
    f = BytesIO()

    with Image.new("RGBA", (600, 800), "white") as canv:
        with Image.open("assets/images/gadget.png") as image:

            resized = image.resize((600, 600))
            canv.paste(resized, (0, 200))

            draw = ImageDraw.Draw(canv)
            draw.text((5, 5), text, font=font, fill="black")

            canv.save(f, "PNG")

    f.seek(0)
    return f


def invert(image) -> discord.File:

    wrapped_image = BytesIO(image)
    f = BytesIO()

    frames = []
    durations = []

    with Image.open(wrapped_image) as img:
        for frame in ImageSequence.Iterator(img):
            durations.append(frame.info.get("duration", 50))
            frame = frame.convert("RGB")
            inverted = ImageOps.invert(frame)
            frames.append(inverted)

    if len(frames) < 2:
        frames[0].save(f, format="PNG")
        f.seek(0)
        file = discord.File(f, "inv.png")

    else:
        frames[0].save(f, format="GIF", append_images=frames[1:], save_all=True, duration=durations, disposal=2)
        f.seek(0)
        file = discord.File(f, "inv.gif")

    return file


ASSET_SIZE = 220
OFFSET = 10



def laugh_frame(asset: Image.Image) -> Image.Image:
    with Image.open("laugh.png").convert("RGBA") as LAUGH_IMAGE:
        base = LAUGH_IMAGE.copy()
        asset = asset.resize((ASSET_SIZE, ASSET_SIZE), Image.BICUBIC)
        base.paste(asset, (OFFSET, base.height - (ASSET_SIZE - OFFSET)), asset)
    return base


def laugh(raw_asset: bytes) -> BytesIO:
    buff = BytesIO()

    with Image.open(BytesIO(raw_asset)) as asset:
        gif = False
        if gif := asset.is_animated:
            frames = []
            for frame in ImageSequence.Iterator(asset):
                new_frame = laugh_frame(frame.convert("RGBA"))
                new_frame.info["duration"] = frame.info.get("duration", 0)
                frames.append(new_frame)

            frames[0].save(buff, format="GIF", save_all=True, append_images=frames[1:], loop=0)
        else:
            laugh_frame(asset).save(buff, format="PNG")

    gif = "gif" if gif else "png"

    buff.seek(0)
    return buff, gif