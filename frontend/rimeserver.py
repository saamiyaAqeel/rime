"""
Serve GraphQL on a socket.
"""

import asyncio
import os
import urllib.parse
import concurrent.futures
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocket
from ariadne.asgi import GraphQL as AriadneGraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler

# Assume RIME is in the directory above this one.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rime import Rime
from rime.graphql import schema, QueryContext
from rime.config import Config


class RimeBGCall:
    """
    When invoked, run the given function in the background, passing as a first argument 'rime'
    (which should correspond to the background RIME instance).
    """
    def __init__(self, bg_rime, bg_executor):
        super().__init__()
        self._bg_rime = bg_rime
        self._bg_executor = bg_executor

    def __call__(self, fn, *args, **kwargs):
        return self._bg_executor.submit(fn, self._bg_rime, *args, **kwargs)


class NullBGCall:
    """
    Acts like a BG Executor, but is passed to the background RIME and just runs things immediately.
    """
    def __init__(self):
        super().__init__()
        self._rime = None

    def set_rime(self, rime):
        self._rime = rime

    def __call__(self, fn, *args, **kwargs):
        return fn(self._rime, *args, **kwargs)


class RimeSingleton:
    """
    Serialise access to RIME so all DB access is done from the same thread.

    We use the current thread for foreground tasks, and create a separate background
    thread for background tasks such as subsetting with anonymisation.
    """
    def __init__(self, config):
        super().__init__()

        # Create the background RIME.
        self._bg_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        null_bg_call = NullBGCall()
        self._bg_rime = self._bg_executor.submit(Rime.create, config, null_bg_call).result()

        # Create the foreground RIME.
        fg_bg_call = RimeBGCall(self._bg_rime, self._bg_executor)
        self._rime = Rime.create(config, fg_bg_call)

    def get_context_value(self, request, data):
        return QueryContext(self._rime)

    async def get_media(self, media_id):
        return self._rime.get_media(media_id)

    async def startup(self):
        await self._rime.start_background_tasks_async()

    async def shutdown(self):
        await self._rime.stop_background_tasks_async()


def create_app():
    # Read config
    frontend_host, frontend_port = os.environ.get('RIME_FRONTEND', 'localhost:3000').split(':')
    for filename in (os.environ.get('RIME_CONFIG', 'rime_settings.local.yaml'), 'rime_settings.yaml'):
        if os.path.exists(filename):
            print("RIME is using the configuration file", filename)
            rime_config = Config.from_file(filename)
            break
    else:
        print("Configuration file not found. Create rime_settings.local.yaml or set RIME_CONFIG.")
        sys.exit(1)

    rime = RimeSingleton(rime_config)
    app = FastAPI()

    # Add CORS middleware to allow the frontend to communicate with the backend on a different port.
    cors_origins = [
        f"http://{frontend_host}:{frontend_port}",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        await rime.startup()

    @app.on_event("shutdown")
    async def shutdown():
        await rime.shutdown()

    @app.get("/media/{media_id:path}")
    async def handle_media(media_id: str):
        media_id = urllib.parse.unquote(media_id)
        media_data = await rime.get_media(media_id)

        response = StreamingResponse(media_data.handle, media_type=media_data.mime_type)
        response.headers['Content-Length'] = str(media_data.length)
        return response

    graphql_app = AriadneGraphQL(
        schema,
        websocket_handler=GraphQLTransportWSHandler(),
        context_value=rime.get_context_value
    )

    # Use a separate endpoint, rather than app.mount, because Starlette doesn't support root mounts not ending in /.
    # See https://github.com/encode/starlette/issues/869 .
    @app.post("/graphql")
    async def handle_graphql_post(request: Request):
        # Queries and mutations.
        return await graphql_app.handle_request(request)

    @app.websocket("/graphql-ws")
    async def handle_graphql_ws(websocket: WebSocket):
        return await graphql_app.handle_websocket(websocket)

    return app
