import asyncio

from .config import Config
from .scrape import Scrape


async def main():
    sdk = Scrape()
    while True:
        await sdk.run()
        await asyncio.sleep(Config.threshold_minute * 60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
