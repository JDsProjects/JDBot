import textwrap
import typing
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence
from wand.image import Image as WImage

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


PADDING_PX = 10


def wrap_text(text: str, max_linesize: int = 20):
    text_size = len(text)
    line_count = text_size // max_linesize or 1
    return textwrap.fill(text, (text_size + 2) // line_count)


def gadget(text: str) -> BytesIO:
    text = wrap_text(text.upper())

    f = BytesIO()
    with Image.open("assets/images/gadget.png") as image:
        with Image.new("RGBA", (600, 800), "white") as canv:
            draw = ImageDraw.Draw(canv)
            image = image.resize((600, 600))

            font = ImageFont.truetype("assets/fonts/verdana_edited.ttf", 1)
            width = draw.textlength(text, font=font)

            left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font, font_size=font.size)

            width = right - left
            height = top - bottom

            while width < (600 - (PADDING_PX * 4)):
                font = ImageFont.truetype("assets/fonts/verdana_edited.ttf", font.size + 1)
                if font.size > 100:
                    break

                leftw, toph, rightw, bottomh = draw.multiline_textbbox((0, 0), text, font=font, font_size=font.size)

                neww = rightw - leftw
                newh = toph - bottomh

                if width < (600 - (PADDING_PX * 2)):
                    width = neww
                    height = newh
                    continue
                break

            font_height = height + (PADDING_PX * 2)
            with Image.new("RGBA", (600, font_height + image.height), "white") as new_canv:
                new_draw = ImageDraw.Draw(new_canv)
                x = (600 - PADDING_PX - width) / 2
                y = PADDING_PX / 2
                print(width, height, font_height, font.size, x, y)
                new_draw.text((x, y), text, align="center", font=font, fill="black")
                new_canv.paste(image, (0, font_height))
                new_canv.save(f, "PNG")

    f.seek(0)
    return f


def invert(image) -> discord.File:
    wrapped_image = BytesIO(image)
    f = BytesIO()

    frames = []
    frame_durations = []

    with Image.open(wrapped_image) as img:
        for frame in ImageSequence.Iterator(img):
            frame_durations.append(frame.info.get("duration", 50))

            with Image.new("RGBA", frame.size) as canv:
                og_image = frame.convert("RGBA")
                image = og_image.convert("RGB")
                new_image = ImageOps.invert(image)
                new_image = new_image.convert("RGBA")

                # pillow can not handle alpha channel so this is unfortunately needed to make it work properly

                canv.paste(new_image, mask=og_image)

            frames.append(canv)

    if len(frames) < 2:
        frames[0].save(f, format="PNG")
        f.seek(0)
        file = discord.File(f, "inv.png")

    else:
        frames[0].save(
            f, format="GIF", append_images=frames[1:], save_all=True, duration=frame_durations, disposal=2, loop=0
        )
        f.seek(0)
        file = discord.File(f, "inv.gif")

    return file


def invert2(image) -> discord.File:
    wrapped_image = BytesIO(image)

    with WImage(file=wrapped_image) as img:
        img.iterator_first()
        img.negate()

        while img.iterator_next():
            img.negate()

        ext = "gif" if len(img.sequence) > 1 else "png"

        img.format = ext
        data = BytesIO(img.make_blob())
        return discord.File(data, f"inverted.{ext}")


ASSET_SIZE = 220
ASSET_SIZE2 = 300
OFFSET = 10


def laugh_frame(LAUGH_IMAGE: Image.Image, asset: Image.Image) -> Image.Image:
    base = LAUGH_IMAGE.copy()
    base = base.convert("RGBA")
    asset = asset.convert("RGBA")
    asset = asset.resize((ASSET_SIZE, ASSET_SIZE), Image.BICUBIC)
    base.paste(asset, (OFFSET, base.height - (ASSET_SIZE - OFFSET)), asset)
    return base


def laugh(raw_asset: bytes) -> tuple[BytesIO, typing.Literal["gif", "png"]]:
    buff = BytesIO()

    with Image.open("assets/images/laugh.png").convert("RGBA") as template:
        with Image.open(BytesIO(raw_asset)) as asset:
            gif = getattr(asset, "is_animated", False)
            if gif:
                frames = []
                for frame in ImageSequence.Iterator(asset):
                    new_frame = laugh_frame(template, frame.convert("RGBA"))
                    new_frame.info["duration"] = frame.info.get("duration", 0)
                    frames.append(new_frame)

                frames[0].save(buff, format="GIF", save_all=True, append_images=frames[1:], loop=0)
            else:
                laugh_frame(template, asset).save(buff, format="PNG")

    gif = "gif" if gif else "png"

    buff.seek(0)
    return buff, gif


def laugh_frame2(BASE, LAUGH_IMAGE: Image.Image, asset: Image.Image) -> Image.Image:
    base = BASE.copy()
    base = base.convert("RGBA")
    asset = asset.convert("RGBA")
    asset = asset.resize((ASSET_SIZE2, ASSET_SIZE2), Image.BICUBIC)
    base.paste(asset, (OFFSET, base.height - (ASSET_SIZE2 + OFFSET)), asset)
    base.paste(LAUGH_IMAGE, (0, 0), LAUGH_IMAGE)
    return base


def laugh2(raw_asset: bytes) -> tuple[BytesIO, typing.Literal["gif", "png"]]:
    buff = BytesIO()

    with Image.open("assets/images/laugh2.png").convert("RGBA") as template:
        with Image.new("RGBA", (template.width, template.height), "white") as canvas:
            with Image.open(BytesIO(raw_asset)) as asset:
                gif = getattr(asset, "is_animated", False)
                if gif:
                    frames = []
                    for frame in ImageSequence.Iterator(asset):
                        new_frame = laugh_frame2(canvas, template, frame.convert("RGBA"))
                        new_frame.info["duration"] = frame.info.get("duration", 0)
                        frames.append(new_frame)

                    frames[0].save(buff, format="GIF", save_all=True, append_images=frames[1:], loop=0)
                else:
                    laugh_frame2(canvas, template, asset).save(buff, format="PNG")

    gif = "gif" if gif else "png"

    buff.seek(0)
    return buff, gif


def crusty(raw_assets: bytes) -> discord.File:
    f = BytesIO()

    with WImage(blob=raw_assets) as img:
        if img.format in ("GIF",):
            img.coalesce()
            img.iterator_reset()

        for d in (35, 2000):
            img.resize(d, d)

        img.save(file=f)
        ext = img.format

    f.seek(0)
    return discord.File(f, f"crusty.{ext}")
