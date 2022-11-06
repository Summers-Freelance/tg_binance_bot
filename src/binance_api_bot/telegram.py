import asyncio
import json

import aiohttp

from .utils import set_env


class Telegram:
    async def send_message(self, message):
        self.base_headers = {
            "Content-Type": "application/json",
        }
        envs = set_env()
        apiToken = envs["TG_TOKEN"]
        chatID = envs["TG_CHANNEL_ID"]
        url = f"https://api.telegram.org/bot{apiToken}/sendMessage"
        payload = json.dumps(
            # For channel -100 has to add as prefix.
            {
                "chat_id": f"-100{chatID}",
                "text": message,
                "parse_mode": "HTML",
            },
        )

        should_retry = True

        while should_retry:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=payload,
                    headers=self.base_headers,
                ) as response:
                    json_response = await response.json()
                    if json_response["error_code"] == 429:
                        asyncio.sleep([json_response["parameters"]["retry_after"]])
                        continue
                    response.raise_for_status()
                    return json_response
