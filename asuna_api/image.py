import io
from asuna_api.http import HTTPClient

# heavily inspired by https://github.com/Rapptz/discord.py/blob/master/discord/asset.py
#code from https://github.com/iDutchy/sr_api/blob/1c97c1b355f1ef12b1dc64a5e80ecba37ad3fc81/sr_api/image.py
class Image:
  __slots__ = ("url", "_http_client")

  def __init__(self, http_client: HTTPClient, url):
    self.url = url
    self._http_client = http_client

  def __str__(self):
    return self.url if self.url is not None else ''

  async def read(self):
    return await self._http_client.get(self.url)

  async def save(self, fp, seek_start=True):
    data = await self.read()
    if isinstance(fp, io.IOBase) and fp.writable():
      written = fp.write(data)

      if seek_start:
        fp.seek(0)

      return written

    else:
      with open(fp, 'wb') as f:
        return f.write(data)
