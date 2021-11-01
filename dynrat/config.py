import os

import yaml


class Config:

    def __init__(self, path):

        if not os.path.exists(path):
            raise FileNotFoundError
        self._config_path = path

        self._load_config()

    def _load_config(self):

        with open(self._config_path, 'r') as stream:
            config = yaml.load(stream, yaml.Loader)

        self._config = config

    def __getitem__(self, key):

        self._load_config()

        if key in self._config.keys():
            return self._config[key]
        else:
            raise KeyError

    def __repr__(self):

        return self._config.__repr__()
