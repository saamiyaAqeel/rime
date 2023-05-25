from abc import ABCMeta, abstractmethod
from collections import defaultdict
import traceback
from weakref import WeakMethod
from threading import Lock

class Scheduler(metaclass=ABCMeta):
    @abstractmethod
    def run_on_my_thread(self, fn, *args, **kwargs):
        pass

    @abstractmethod
    def run_on_background_thread(self, fn, *args, **kwargs):
        pass

class _Broker:
    def __init__(self):
        # Ideally, we'd use a defaultdict(WeakSet) here, but we would need to store bound methods in the
        # WeakSets; bound methods are created on-demand, so when the method goes out of scope they would
        # have no more referents and would thus be deleted from the WeakSet unless wrapped by WeakMethod.
        # However, the WeakMethod objects themselves would then go out of scope and have no non-weak
        # referents!
        self._subscribers = defaultdict(set)
        self._lock = Lock()

    def subscribe(self, event, callback):
        if not isinstance(callback, WeakMethod) and hasattr(callback, '__self__'):
            callback = WeakMethod(callback)

        with self._lock:
            self._subscribers[event].add(callback)

    def unsubscribe(self, event, callback):
        with self._lock:
            try:
                self._subscribers[event].remove(callback)
            except KeyError:
                pass

    def publish(self, event, data=None):
        with self._lock:
            subscribers = self._subscribers[event]

        remove = set()

        for callback in subscribers:
            try:
                if isinstance(callback, WeakMethod):
                    meth = callback()
                    if meth is None:
                        remove.add(callback)
                        continue
                    meth(data)
                else:
                    callback(data)
            except Exception as e:
                traceback.print_exc()

        if remove:
            with self._lock:
                for callback in remove:
                    self._subscribers[event].remove(callback)

broker = _Broker()
