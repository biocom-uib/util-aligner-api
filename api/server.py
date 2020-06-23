
import os

from aiohttp import web
from aiohttp_cors import ResourceOptions, setup as setup_cors

from api.middleware import json_middleware, sources_api_middleware
from api.routes import routes
from api.signals import (# create_sentry, dispose_sentry,
                         # create_db_pool, dispose_db_pool,
                         create_sources_api_session, dispose_sources_api_session,
                         create_celery_app,
                         create_cache_pool,
                         create_mongo)

from config import config


def setup_routes(app):
    for route in routes:
        app.router.add_route(*route)


def setup_middlewares(app):
    app.middlewares.append(sources_api_middleware)
    app.middlewares.append(json_middleware)
    # if os.environ['APP_ENV'] == 'local':  # pragma: nocover
    #     app.middlewares.append(database_middleware)


def on_startup_signal(app):
    app.on_startup.append(create_celery_app)
    # app.on_startup.append(create_db_pool)
    app.on_startup.append(create_cache_pool)
    app.on_startup.append(create_mongo)
    app.on_startup.append(create_sources_api_session)

    # if os.environ['APP_ENV'] == 'production':  # pragma: nocover
    #     app.on_startup.append(create_sentry)


def on_cleanup_signal(app):
    app.on_cleanup.append(dispose_sources_api_session)

    # if os.environ['APP_ENV'] == 'local':  # pragma: nocover
    #     app.on_cleanup.append(dispose_db_pool)
    # if os.environ['APP_ENV'] == 'production':  # pragma: nocover
    #     app.on_cleanup.append(dispose_sentry)


def init_cors(app):
    return setup_cors(app, defaults={
        "*": ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })


def init():
    app = web.Application(client_max_size=config['CLIENT_MAX_SIZE'])
    cors = init_cors(app)
    setup_routes(app)
    setup_middlewares(app)
    for route in app.router.routes():
        cors.add(route)
    on_startup_signal(app)
    on_cleanup_signal(app)
    return app


app = init()
