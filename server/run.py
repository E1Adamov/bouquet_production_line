from aiohttp import web

from src import global_objects, routes
import config


def run():
    global_objects.APP.add_routes(global_objects.ROUTES)
    web.run_app(global_objects.APP, host=config.HOST, port=config.PORT)


if __name__ == '__main__':
    run()
