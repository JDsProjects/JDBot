import aiohttp
from .http import HTTPClient
from yarl import URL

class Client:
  def __init__(self,session: aiohttp.ClientSession = None):
    self._http_client = HTTPClient(session)

  def super_api_url(self,endpoint):
    url = URL.build(
      scheme: "https",
      host: "asuna.ga/api",
      path=endpoint
    )
    return str(url)

  async def get_gif(self,name):
    options = ("hug","kiss","neko","pat","slap","wholesome_foxes")
    response = await self._http_client.get(self.srapi_url(name))
    url = response.get("url")
    return Image(self._http_client, url)



  async def close(self):
      await self._http_client.close()