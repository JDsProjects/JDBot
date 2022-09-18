import textwrap
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("assets/fonts/verdana_edited.ttf", 35)
# should be able to place it here


def call_text(text) -> discord.File:

    text = textwrap.fill(text, 33)
    f = BytesIO()

    with Image.open("assets/images/calling_template.jpg") as image:

        draw = ImageDraw.Draw(image)
        draw.text((5, 5), text, font=font, fill="black")

    image.save(f, "PNG")
    f.seek(0)
    file = discord.File(f, "test.png")
    return file
