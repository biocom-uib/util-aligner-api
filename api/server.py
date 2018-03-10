
import os

from aiohttp import web

from api.middleware import database_middleware, cache_middleware, error_middleware, json_middleware
from api.routes import routes
from api.signals import create_sentry, dispose_sentry


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)


def setup_middlewares(app):
    middlewares = [
        error_middleware,
        json_middleware,
        database_middleware,
        cache_middleware,
    ]
    for middleware in middlewares:
        app.middlewares.append(middleware)


def on_startup_signal(app):
    if os.environ['APP_ENV'] == 'production':  # pragma: nocover
        app.on_startup.append(create_sentry)


def on_cleanup_signal(app):
    if os.environ['APP_ENV'] == 'production':  # pragma: nocover
        app.on_cleanup.append(dispose_sentry)


def init():
    app = web.Application()
    setup_routes(app)
    setup_middlewares(app)
    on_startup_signal(app)
    on_cleanup_signal(app)
    return app


app = init()
