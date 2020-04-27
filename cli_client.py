import asyncio
import json
import os
import sys

import websockets
from aioconsole import ainput

import global_config


class Runner:
    def __init__(self):
        self.websocket = None
        self.have_orders = False
        self.input_type = 'bouquet_design'
        self.reader = None

    @property
    def input_type_input_prefix_map(self):
        map_ = dict(
            bouquet_design='Enter a bouquet design or empty line',
            flower='Enter a flower'
        )
        return map_

    @property
    def input_type(self):
        return self.__input_type

    @input_type.setter
    def input_type(self, i_type: str):
        assert i_type in ('bouquet_design', 'flower')
        self.__input_type = i_type

    async def send_client_input(self):
        while True:
            input_prefix = self.input_type_input_prefix_map[self.input_type]

            if len(sys.argv) > 1:
                test_file_name = sys.argv[1]
                test_file_path = os.path.join(os.getcwd(), test_file_name)
                for client_input in self.test_file_reader(test_file_path):
                    if client_input.strip() == 'stop':
                        await asyncio.sleep(999999)

                    self.have_orders = True
                    jsn = json.dumps({'type': self.input_type, 'payload': client_input.strip()})

                    if not client_input.strip() and self.have_orders:
                        self.input_type = 'flower'

                    await self.websocket.send(jsn)

            else:
                client_input = await ainput(f"{input_prefix}: ")

            if not client_input.strip() and self.have_orders:
                self.input_type = 'flower'

            self.have_orders = True
            jsn = json.dumps({'type': self.input_type, 'payload': client_input})
            await self.websocket.send(jsn)

    async def read_server_response(self):
        while True:
            msg = await self.websocket.recv()
            if msg == 'close':
                await self.websocket.disconnect()
            elif 'all orders completed' in msg.lower():
                self.input_type = 'bouquet_design'
                self.have_orders = False
            print(f"\n{msg}")

    async def run(self):
        uri = f"ws://{global_config.PROD_LINE_HOST_NAME}:{global_config.PROD_LINE_PORT}/{global_config.PROD_LINE_URL}"

        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            await asyncio.gather(
                self.send_client_input(),
                self.read_server_response(),
                return_exceptions=True,
            )

    @staticmethod
    def test_file_reader(file):
        with open(file) as f:
            for line in f.readlines():
                yield line


if __name__ == '__main__':
    runner = Runner()

    try:
        asyncio.run(runner.run())
    except KeyboardInterrupt:
        exit(1)
