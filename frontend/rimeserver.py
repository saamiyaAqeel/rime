"""
Serve GraphQL on a socket.
"""
import os
import urllib.parse
import concurrent.futures
import sys

from flask import Flask, request, jsonify, send_file, make_response

# Assume RIME is in the directory above this one.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rime import Rime
from rime.config import Config
from rime.pubsub import Scheduler

app = Flask(__name__)

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

    We provide a single thread for the frontend, and another thread for background tasks
    such as subsetting with anonymisation.
    """
    def __init__(self, config):
        super().__init__()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._bg_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        fg_scheduler = RimeScheduler(self._executor, self._bg_executor)
        self._rime = self._executor.submit(lambda: Rime.create(config, fg_scheduler)).result()

        bg_scheduler = RimeScheduler(self._bg_executor, self._bg_executor)
        self._bg_rime = self._bg_executor.submit(lambda: Rime.create(config, bg_scheduler)).result()

    def _run(self, fn, *args, **kwargs):
        future = self._executor.submit(fn, *args, **kwargs)
        return future.result()

    def query(self, query_json):
        return self._run(self._rime.query, query_json)

    def get_media(self, media_id):
        return self._run(self._rime.get_media, media_id)


rime = RimeSingleton(rime_config)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = f'http://{frontend_host}:{frontend_port}'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


@app.route('/media/<path:media_id>', methods=['GET'])
def handle_media(media_id):
    media_id = urllib.parse.unquote(media_id)
    return handle_get_media(media_id)


@app.route('/graphql', methods=['POST'])
def handle_graphql():
    return handle_post_graphql(request)


def handle_get_media(media_id):
    media_data = rime.get_media(media_id)

    response = make_response(send_file(media_data.handle, mimetype=media_data.mime_type))
    response.headers['Content-Length'] = str(media_data.length)
    return response


def handle_post_graphql(request):
    query_json = request.get_json()

    success, result = rime.query(query_json)
    status = 200 if success else 400

    return jsonify(result), status, {'Content-Type': 'application/json'}
