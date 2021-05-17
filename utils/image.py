from PIL import ImageOps, Image
import discord
import io

def invert_func(bytes_returned):
  image = Image.open(io.BytesIO(bytes_returned))
  if image.mode == 'RGBA':
    r,g,b,a = image.split()
    rgb_image = Image.merge('RGB', (r,g,b))

    inverted_image = ImageOps.invert(rgb_image)

    r2,g2,b2 = inverted_image.split()

    final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))

    buffer = io.BytesIO()
    final_transparent_image.save(buffer,image.format)
    buffer.seek(0)
    file = discord.File(buffer,filename=f"inverted.{image.format}")
    return file

  else:
    try:
      inverted_image = ImageOps.invert(image)
    except NotImplementedError:
      buffer = io.BytesIO(bytes_returned)
      file = discord.File(buffer,filename=f"failed.{image.format}",save_all=True)
      return file
    buffer = io.BytesIO()
    inverted_image.save(buffer,image.format)
    buffer.seek(0)
    file = discord.File(buffer,filename=f"inverted.{image.format}")
    return file