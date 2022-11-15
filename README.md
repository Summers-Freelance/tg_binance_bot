# Binance API SDK

## Usage

```py
import asyncio

from binance_api_bot import BinanceAPISDK

async def main():
    sdk = BinanceAPISDK()
    traders = await sdk.list_top_monthly()
    for _ in range(10000):
        positions = await sdk.list_positions(traders["data"][1]["encryptedUid"])
        print("positions",positions)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

## Start scraping at interval

```sh
cd src/
python3 -m binance_api_bot.main
```
