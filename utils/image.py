import textwrap
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont

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
