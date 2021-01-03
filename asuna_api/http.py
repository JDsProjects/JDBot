import aiohttp

class HTTPClient:
  __slots__ = ("session")

  def __init__(self, session=None):
    self.session = session

  # Aiohttp client sessions must be created in async functions
  async def create_session(self):
    self.session = aiohttp.ClientSession()

    # Send this request to the asuna.ga base + path
    # path is what comes after the / in the base url
    # **kwargs is passed to self.session.request along with the full url

  async def get(self, url, **kwargs):
    if self.session is None:
      await self.create_session()

    async with self.session.get(url, **kwargs) as response:
      if not (300 > response.status >= 200):
          # TODO: Seperate exception for statuses raised
          raise ValueError("Raised " + str(response.status))

      try:
        content = await response.json()
      except aiohttp.ClientResponseError:
        content = await response.read()

      return content

  async def close(self):
    if self.session is not None:
      await self.session.close()
      self.session = None
