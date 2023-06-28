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
from ariadne.asgi import GraphQL as AriadneGraphQL

# Assume RIME is in the directory above this one.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rime import Rime
from rime.graphql import schema, QueryContext
from rime.config import Config
from rime.pubsub import Scheduler


class RimeScheduler(Scheduler):
    def __init__(self, bg_thread_executor):
        super().__init__()
        self._bg_thread_executor = bg_thread_executor
        self.tasks = set()

    def run_next(self, fn, *args, **kwargs):
        """
        Run "fn" after all other scheduled tasks have completed.

        This will run on the web server thread, so can't block (for long).
        """
        loop = asyncio.get_running_loop()
        task = loop.create_task(fn(*args, **kwargs))
        self.tasks.add(task)
        task.add_done_callback(lambda _: self.tasks.remove(task))
        return task

    def run_in_background(self, fn, *args, **kwargs):
        """
        Run "fn" on a separate thread in the background.
        """
        return self._bg_thread_executor.submit(fn, *args, **kwargs)


class RimeSingleton:
    """
    Serialise access to RIME so all DB access is done from the same thread.

    We use concurrent.futures to provide a single thread for the frontend,
    and another thread for background tasks such as subsetting with anonymisation.
    """
    def __init__(self, config):
        super().__init__()
        self._bg_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        fg_scheduler = RimeScheduler(self._bg_executor)
        self._rime = Rime.create(config, fg_scheduler)

        bg_scheduler = RimeScheduler(self._bg_executor)
        self._bg_rime = self._bg_executor.submit(lambda: Rime.create(config, bg_scheduler)).result()

    def get_context_value(self, request, data):
        return QueryContext(self._rime)

    async def query(self, query_json):
        result = await self._rime.query_async(query_json)
        return result

    async def subscribe(self, query_json):
        return self._rime.subscribe_async(query_json)

    async def get_media(self, media_id):
        return self._rime.get_media(media_id)


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

    @app.get("/media/{media_id:path}")
    async def handle_media(media_id: str):
        media_id = urllib.parse.unquote(media_id)
        media_data = await rime.get_media(media_id)

        response = StreamingResponse(media_data.handle, media_type=media_data.mime_type)
        response.headers['Content-Length'] = str(media_data.length)
        return response

    graphql_app = AriadneGraphQL(schema, context_value=rime.get_context_value)

    # Use a separate endpoint, rather than app.mount, because Starlette doesn't support root mounts not ending in /.
    # See https://github.com/encode/starlette/issues/869 .
    @app.post("/graphql")
    @app.websocket("/graphql")
    async def handle_graphql(request: Request):
        if request.scope['type'] == 'websocket':
            # Subscriptions.
            return await graphql_app.handle_websocket(request)

        return await graphql_app.handle_request(request)

    return app
