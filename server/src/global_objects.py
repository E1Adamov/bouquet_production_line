import logging
import sys

from aiohttp import web

import config
from src import warehouse
from src import production
from src import input_service
from src import shipping_dept

LOGGER = logging.getLogger()
LOGGER.setLevel(level=config.LOGGER_LEVEL)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

APP = web.Application()
ROUTES = web.RouteTableDef()

INPUT_SERVICE = input_service.InputService()
WAREHOUSE = warehouse.Warehouse()
PRODUCTION = production.Production()
SHIPPING_DEPT = shipping_dept.ShippingDepartment()
