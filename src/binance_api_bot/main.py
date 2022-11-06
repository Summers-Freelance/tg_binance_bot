import asyncio
import logging

from .config import Config
from .log_util import setup_logging
from .scrape import Scrape


async def main():
    sdk = Scrape()
    while True:
        try:
            await sdk.run()
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e, exc_info=True)
        await asyncio.sleep(Config.threshold_minute * 60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    setup_logging()
    loop.run_until_complete(main())
