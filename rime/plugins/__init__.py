from dataclasses import dataclass
import importlib
import os
from typing import Callable

from ruamel.yaml import YAML

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Plugin:
    name: str
    category: str
    config: dict
    module_name: str
    func_name: str
    _fn: Callable | None

    @property
    def fn(self):
        """
        Return the plugin's entrypoint function, importing it lazily.
        """
        if self._fn is None:
            module = importlib.import_module(f'rime.plugins.{self.category}.{self.name}.{self.module_name}')
            self._fn = getattr(module, self.func_name)

        return self._fn


def load_plugin(category, name):
    plugin_dir = os.path.join(BASE_PATH, category)
    yaml = YAML()
    with open(os.path.join(plugin_dir, name, 'plugin.yaml')) as h:
        config = yaml.load(h)

    module_name, func_name = config['entrypoint'].rsplit('.', 1)

    return Plugin(name=name, category=category, config=config, module_name=module_name, func_name=func_name, _fn=None)
