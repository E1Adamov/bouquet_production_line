from aiohttp.web_ws import WebSocketResponse

from src import global_objects
from src.internal.bouquet_design import BouquetDesign, InvalidBouquetDesign
from src.internal.flower import Flower, InvalidFlower


class InputService:
    @staticmethod
    async def accept_input(client_input: dict, ws: WebSocketResponse):
        if not client_input['payload']:
            global_objects.LOGGER.debug('Received empty line, switching to accept flowers')
            return
        try:
            input_type = client_input['type']
            client_input = client_input['payload']

            if input_type == 'bouquet_design':
                bouquet_design = BouquetDesign(client_input)
                global_objects.PRODUCTION.set_client(ws)
                global_objects.PRODUCTION.start_line(bouquet_design=bouquet_design, websocket=ws)
            elif input_type == 'flower':
                flower = Flower(client_input=client_input)
                await global_objects.WAREHOUSE.accept(flower=flower)
            else:
                await ws.send_str(f"Invalid type: {input_type}")

        except (InvalidBouquetDesign, InvalidFlower) as ex:
            await ws.send_str(f"[-] {ex}")
