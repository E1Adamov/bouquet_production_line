from collections import defaultdict
from typing import Dict, DefaultDict

from src import global_objects
from src.internal.flower import Flower
from src.internal.observer_pattern import Observable
from src.production import ProductionLine
from src.internal import tools


class Warehouse(Observable):
    def __init__(self):
        super().__init__()
        self.__flowers = defaultdict(int)

    async def accept(self, flower: Flower):
        self.__flowers[flower] += 1
        await self.notify_observers(self.__flowers)

    async def ship_out(self, flowers: Dict[Flower, int], production_line: ProductionLine):
        if not tools.is_int_dict_in_dict(dic=flowers, in_dic=self.__flowers):
            raise NotEnoughStock(
                f"There are not enough flowers in stock.\n"
                f"\tRequested: {flowers}\n"
                f"\tAvailable: {self.__flowers}")

        global_objects.LOGGER.debug(f"Shipping from the warehouse: {flowers}")

        self.__flowers = tools.deduct_int_dicts(from_dict=self.__flowers, deduct_dict=flowers)
        production_line.accept(flowers)
        await self.notify_observers(self.__flowers, except_={production_line})

    def get_current_stock(self) -> DefaultDict[Flower, int]:
        return self.__flowers


class NotEnoughStock(Exception):
    pass
