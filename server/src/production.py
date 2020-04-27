import copy
from collections import defaultdict
from typing import List, Dict, Tuple, DefaultDict, OrderedDict, Union

from aiohttp.web_ws import WebSocketResponse

from src.internal.bouquet_design import BouquetDesign
from src.internal.flower import Flower
from src import global_objects
from src.internal import tools
from src.internal.observer_pattern import Observer
from src import warehouse


class ProductionLine(Observer):
    def __init__(self, bouquet_design: BouquetDesign, websocket: WebSocketResponse):
        self.bouquet_design: BouquetDesign = bouquet_design
        self.websocket: WebSocketResponse = websocket
        self.stock: DefaultDict[Flower, int] = defaultdict(int)
        self.observe_warehouse()
        self.ready_bouquet: str = str()

    def observe_warehouse(self):
        global_objects.WAREHOUSE.add_observer(self)

    async def update(self, warehouse_stock: DefaultDict[Flower, int]):
        await self.launch_production_process(warehouse_stock)

    def accept(self, flowers: Dict[Flower, int]):
        global_objects.LOGGER.debug(f"Accepting from warehouse: {flowers}")
        self.stock = tools.sum_int_dicts(*(self.stock, flowers))

    async def launch_production_process(self, warehouse_stock: DefaultDict[Flower, int]):
        global_objects.LOGGER.debug(f"Got update from warehouse: {warehouse_stock}")
        concrete_flowers, any_flowers_quantity, any_flowers_size = self.__split_flowers_to_concrete_and_any()
        global_objects.LOGGER.debug(f"Need flowers: {concrete_flowers}, {any_flowers_quantity}, {any_flowers_size}")

        if not tools.is_int_dict_in_dict(dic=concrete_flowers, in_dic=warehouse_stock):
            global_objects.LOGGER.debug('Not enough in the warehouse')
            return

        global_objects.LOGGER.debug('Enough in the warehouse')

        if any_flowers_quantity:
            global_objects.LOGGER.debug('Need extra any flowers')
            not_demanded_flowers: Dict[Flower, int] = global_objects.PRODUCTION.get_not_demanded_flowers(
                size=any_flowers_size,
                needed_quantity=any_flowers_quantity,
            )
            if not_demanded_flowers:
                global_objects.LOGGER.debug(f"Extra flowers available: {not_demanded_flowers}")
                for f, q in not_demanded_flowers.items():
                    global_objects.LOGGER.debug(f"\t{f}: {q}")
                await self.get_flowers_from_warehouse(not_demanded_flowers)
            else:
                global_objects.LOGGER.debug('Not enough extra any flowers in the warehouse')
                return

        try:
            await self.get_flowers_from_warehouse(concrete_flowers)
        except warehouse.NotEnoughStock:
            return
        else:
            self.produce_bouquet()
            await self.move_bouquet_to_the_shipping_department()

    def __split_flowers_to_concrete_and_any(self) -> Tuple[Dict, int, str]:
        concrete_flowers: DefaultDict[Flower, int] = copy.deepcopy(self.bouquet_design.flowers)

        any_flowers_quantity = 0
        any_flowers_size = str()

        for flower, quantity in concrete_flowers.items():
            if flower.species == 'A':
                any_flowers_quantity = quantity
                any_flowers_size = flower.size
                del concrete_flowers[flower]
                break
        return concrete_flowers, any_flowers_quantity, any_flowers_size

    async def move_bouquet_to_the_shipping_department(self):
        global_objects.LOGGER.debug(f"Moving bouquet to the shipping dept: {self.ready_bouquet}")
        await global_objects.SHIPPING_DEPT.accept(bouquet=self.ready_bouquet, client=self.websocket)
        self.ready_bouquet = str()

    def take_from_stock_flowers_for_production(self, flowers):
        self.stock = tools.deduct_int_dicts(from_dict=self.stock, deduct_dict=flowers)

    def produce_bouquet(self):
        global_objects.LOGGER.debug(f"Got enough flowers for {self.bouquet_design}. Starting production")
        self.take_from_stock_flowers_for_production(self.bouquet_design.flowers)
        self.ready_bouquet = self.bouquet_design.client_input

    async def get_flowers_from_warehouse(self, flowers: Dict[Flower, int]):
        global_objects.LOGGER.debug(f"Getting from the warehouse {flowers}")
        await global_objects.WAREHOUSE.ship_out(flowers=flowers, production_line=self)


class Production:
    def __init__(self):
        self.client: Union[WebSocketResponse, None] = None
        self.production_lines: Dict[str, ProductionLine] = dict()

    def set_client(self, client: WebSocketResponse):
        self.client = client

    def start_line(self, bouquet_design: BouquetDesign, websocket: WebSocketResponse):
        if bouquet_design.client_input not in self.production_lines:
            production_line = ProductionLine(bouquet_design=bouquet_design, websocket=websocket)
            self.production_lines[bouquet_design.client_input] = production_line

            global_objects.LOGGER.debug(f"Started production line for {bouquet_design}")
            for flower, qty in bouquet_design.items():
                global_objects.LOGGER.debug(f"\t{flower}: {qty}")

    def get_not_demanded_flowers(self, size: str, needed_quantity: int) -> Dict[Flower, int]:
        flowers_needed_for_all_lines: List[Dict[Flower, int]] = [pl.bouquet_design.flowers for pl in self.production_lines.values()]
        flowers_needed_for_all_lines: Dict[Flower, int] = tools.sum_int_dicts(*flowers_needed_for_all_lines)
        flowers_needed_for_all_lines: Dict[Flower, int] = {fl: qty for fl, qty in flowers_needed_for_all_lines.items() if fl.species != 'A'}
        current_stock = global_objects.WAREHOUSE.get_current_stock()
        not_demanded_flowers_all: Dict[Flower, int] = tools.deduct_int_dicts(
            from_dict=current_stock,
            deduct_dict=flowers_needed_for_all_lines,
        )

        if sum(not_demanded_flowers_all.values()) < needed_quantity:
            return dict()

        not_demanded_flowers_of_specific_size: Dict[Flower, int] = {flower: quantity for flower, quantity in not_demanded_flowers_all.items() if flower.size == size}
        not_demanded_flowers_of_specific_size: OrderedDict[Flower, int] = tools.order_dict_by_value(not_demanded_flowers_of_specific_size)

        # some logic to define least needed flowers should go here
        # for now we pick the ones that we have in biggest quantity

        not_demanded_flowers = dict()

        for flower, qty in not_demanded_flowers_of_specific_size.items():
            still_needed_qty = needed_quantity - sum(not_demanded_flowers.values())
            taking_qty = still_needed_qty if qty >= still_needed_qty else qty
            not_demanded_flowers[flower] = taking_qty
            if sum(not_demanded_flowers.values()) >= needed_quantity:
                break

        return not_demanded_flowers
