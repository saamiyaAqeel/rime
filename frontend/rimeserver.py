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

# Assume RIME is in the directory above this one.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rime import Rime
from rime.config import Config
from rime.pubsub import Scheduler

FILE_CHUNK_SIZE = 1024 * 1024

frontend_host, frontend_port = os.environ.get('RIME_FRONTEND', 'localhost:3000').split(':')
for filename in (os.environ.get('RIME_CONFIG', 'rime_settings.local.yaml'), 'rime_settings.yaml'):
    if os.path.exists(filename):
        print("RIME is using the configuration file", filename)
        rime_config = Config.from_file(filename)
        break
else:
    print("Configuration file not found. Create rime_settings.yaml or set RIME_CONFIG.")
    sys.exit(1)


# CORS Middleware
origins = [
    f"http://{frontend_host}:{frontend_port}",
]

class RimeScheduler(Scheduler):
    def __init__(self, my_thread_executor, bg_thread_executor):
        super().__init__()
        self._my_thread_executor = my_thread_executor
        self._bg_thread_executor = bg_thread_executor

    def run_on_my_thread(self, fn, *args, **kwargs):
        """
        Schedule a function to run on the main thread. Returns a future.
        """
        return self._my_thread_executor.submit(fn, *args, **kwargs)

    def run_on_background_thread(self, fn, *args, **kwargs):
        """
        Schedule a function to run on the background thread. Returns a future.
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
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._bg_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        fg_scheduler = RimeScheduler(self._executor, self._bg_executor)
        self._rime = self._executor.submit(lambda: Rime.create(config, fg_scheduler)).result()

        bg_scheduler = RimeScheduler(self._bg_executor, self._bg_executor)
        self._bg_rime = self._bg_executor.submit(lambda: Rime.create(config, bg_scheduler)).result()

    async def _run(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, fn, *args, **kwargs)

    async def query(self, query_json):
        return await self._run(self._rime.query, query_json)

    async def get_media(self, media_id):
        return await self._run(self._rime.get_media, media_id)


def create_app():
    rime = RimeSingleton(rime_config)

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
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


    @app.post("/graphql")
    async def handle_graphql(request: Request):
        query_json = await request.json()

        success, result = await rime.query(query_json)
        status = 200 if success else 400

        return JSONResponse(content=result, status_code=status)

    return app
