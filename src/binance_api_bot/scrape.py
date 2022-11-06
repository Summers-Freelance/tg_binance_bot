import asyncio
import concurrent.futures
import logging
import os

import pandas as pd

from binance_api_bot import BinanceAPISDK

from .telegram import Telegram


class Scrape:
    def __init__(self):
        self.sdk = BinanceAPISDK()
        self.tg_client = Telegram()
        self.traders = pd.read_csv("data/traders.csv").to_dict("records")

    async def run(self):
        """Main wrapper that looks up the position changes of traders and send
        to telegram.

        The position changes includes looking for new position or closed position.

        If any of the event occurs the message will be sent to the telegram channel.

        The events are gathered via binance public API at every interval.
        """
        # run all traders parallel in thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    self.process_trader,
                    trader,
                )
                for trader in self.traders
            ]
            for i in await asyncio.gather(*futures):
                try:
                    await i
                except Exception as e:
                    logger = logging.getLogger()
                    logger.error(e, exc_info=True)

    async def process_trader(self, trader: dict[str, str]):
        """Look for position changes for trader.

        Args:
            trader (dict[str,str]):
        """
        encrypted_uid = trader["encryptedUid"]
        latest_positions_json = await self.sdk.list_positions(encrypted_uid)
        latest_positions = latest_positions_json["data"]["otherPositionRetList"]

        data_keys = [
            "symbol",
            "entryPrice",
            "markPrice",
            "amount",
        ]
        latest_positions_df = pd.DataFrame(latest_positions, columns=data_keys)
        latest_positions_df = latest_positions_df[data_keys]

        # check if we have old position to compare with new.
        # if there is no old position exist, then save file the file to compare for next iterations.
        trader_csv_path = f"data/positions/{encrypted_uid}.csv"
        if os.path.exists(trader_csv_path):
            old_positions_df = pd.read_csv(trader_csv_path)
            # csv has to be generated after getting all latest position and reading old positions
            latest_positions_df.to_csv(trader_csv_path, index=False)
        else:
            # create file for next iteration to compare with latest_positions.
            latest_positions_df.to_csv(trader_csv_path, index=False)
            return

        await self.send_new_positions(trader, latest_positions_df, old_positions_df)
        await self.send_closed_positions(trader, latest_positions_df, old_positions_df)

    async def send_new_positions(
        self,
        trader: dict[str, str],
        latest_positions_df: pd.DataFrame,
        old_positions_df: pd.DataFrame,
    ):
        """Finds new positions by comparing latest position and old positions.

        To find that exclude all the old positions from new position.

        Args:
            trader (dict[str,str]):
            latest_positions_df (pd.DataFrame):
            old_positions_df (pd.DataFrame):
        """
        new_df_keys = [
            "symbol",
            "trade",
            "entryPrice",
        ]

        new_positions_df = latest_positions_df[
            ~latest_positions_df.symbol.isin(old_positions_df.symbol)
        ]

        # if amount is position then buying, else selling
        new_positions_df["trade"] = new_positions_df["amount"].apply(
            lambda x: "Buy 🔵" if x > 0 else "Sell 🔴",
        )
        # send message for new positions
        for _, position in new_positions_df.iterrows():

            msg = f"New alert 🚨\n\n<b>Trader</b>: {trader['name']}\n"  # noqa: E501

            for k in new_df_keys:
                msg += f"<b>{k.title()}</b>: {position[k]}\n"

            await self.tg_client.send_message(msg)

    async def send_closed_positions(
        self,
        trader: dict[str, str],
        latest_positions_df: pd.DataFrame,
        old_positions_df: pd.DataFrame,
    ):
        """Finds closed positions by comparing latest position and old
        positions.

        To find that exclude all the new positions from old position.
        Remaining old positions will be consider as closed positions.

        Args:
            trader (dict[str,str]):
            latest_positions_df (pd.DataFrame):
            old_positions_df (pd.DataFrame):
        """
        closed_positions_df = old_positions_df[
            ~old_positions_df.symbol.isin(latest_positions_df.symbol)
        ]

        # calculate profit from entry price and market price
        closed_positions_df["profit"] = (
            round(
                (
                    closed_positions_df["markPrice"]
                    / closed_positions_df["entryPrice"]
                    * 100
                )
                - 100,
                2,
            )
        ).astype(str) + " %"

        closed_df_keys = ["symbol", "profit", "markPrice"]
        # send message for closed positions
        for _, position in closed_positions_df.iterrows():

            msg = f"Trade closed ✅\n\n<b>Trader</b>: {trader['name']}\n"  # noqa: E501

            for k in closed_df_keys:
                msg += f"<b>{k.title()}</b>: {position[k]}\n"

            await self.tg_client.send_message(msg)
