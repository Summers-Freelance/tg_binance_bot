import json
from typing import Coroutine

import aiohttp

from .utils import set_env


class BinanceAPISDK:
    def __init__(self) -> None:
        set_env()
        self.base_headers = {
            "Content-Type": "application/json",
        }

    async def list_top_monthly(self) -> Coroutine:
        """List all top monthly traders.

        Returns:
            Coroutine:
        """
        url = "https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getLeaderboardRank"
        payload = json.dumps(
            {
                "isShared": True,
                "periodType": "MONTHLY",
                "statisticsType": "ROI",
                "tradeType": "PERPETUAL",
                "limit": 10,
            },
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=payload,
                headers=self.base_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def list_positions(self, trader: str) -> Coroutine:
        """List latest positions of trader.

        Returns:
            Coroutine:
        """
        url = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"

        payload = json.dumps(
            {
                "encryptedUid": trader,
                "tradeType": "PERPETUAL",
            },
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=payload,
                headers=self.base_headers,
            ) as response:
                response.raise_for_status()
                return await response.json()
