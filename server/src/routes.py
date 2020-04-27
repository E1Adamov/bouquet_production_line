import json
import traceback

import aiohttp
from aiohttp import web

from src import global_objects as go


@go.ROUTES.get(path='/ws/bouquet-order')
async def websocket_handler(request):
    ws = web.WebSocketResponse()

    try:
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close(message=b'close')
                else:
                    go.LOGGER.debug(f'Read websocket: {msg.data}')
                    client_input = json.loads(msg.data)
                    await go.INPUT_SERVICE.accept_input(client_input=client_input, ws=ws)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception {ws.exception()}')

    except BaseException as ex:
        trb = traceback.format_exc()
        error_msg = f'Caught exception {ex.__class__.__name__}: \n\t{ex}'
        go.LOGGER.debug(error_msg)
        go.LOGGER.debug(trb)
        await ws.send_str(error_msg)
        await ws.send_str(trb)
        await ws.close(message=b'close')

        print('websocket connection closed')

    return ws
