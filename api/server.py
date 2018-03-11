
import os

from aiohttp import web
from aiohttp_cors import ResourceOptions, setup as setup_cors

from api.middleware import database_middleware, json_middleware
from api.routes import routes
from api.signals import create_sentry, dispose_sentry, create_db_pool, dispose_db_pool


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)


def setup_middlewares(app):
    app.middlewares.append(json_middleware)
    if os.environ['APP_ENV'] == 'local':  # pragma: nocover
        app.middlewares.append(database_middleware)


def on_startup_signal(app):
    if os.environ['APP_ENV'] == 'production':  # pragma: nocover
        app.on_startup.append(create_sentry)
        app.on_startup.append(create_db_pool)


def on_cleanup_signal(app):
    if os.environ['APP_ENV'] == 'local':  # pragma: nocover
        app.on_cleanup.append(dispose_db_pool)
    if os.environ['APP_ENV'] == 'production':  # pragma: nocover
        app.on_cleanup.append(dispose_sentry)


def init_cors(app):
    return setup_cors(app, defaults={
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })


def init():
    app = web.Application()
    cors = init_cors(app)
    setup_routes(app)
    setup_middlewares(app)
    for route in app.router.routes():
        cors.add(route)
    on_startup_signal(app)
    on_cleanup_signal(app)
    return app


app = init()
