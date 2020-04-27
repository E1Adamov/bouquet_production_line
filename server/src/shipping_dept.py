from typing import List

from aiohttp.web_ws import WebSocketResponse

from src import global_objects


class ShippingDepartment:
    def __init__(self):
        self.stock: List[str] = list()

    async def accept(self, bouquet: str, client: WebSocketResponse):
        self.stock.append(bouquet)
        msg = f"SHIPPED BOUQUET: {bouquet}"
        global_objects.LOGGER.debug(msg)
        await client.send_str(msg)
        self.stock.remove(bouquet)
