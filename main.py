import os, logging
import B, BotConfig

logging.basicConfig(level = logging.INFO)

B.b()
BotConfig.bot.run(os.environ["classic_token"])