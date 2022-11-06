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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=payload,
                headers=self.base_headers,
            ) as response:
                print(await response.json())
                response.raise_for_status()
                return await response.json()
