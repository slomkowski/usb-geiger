import configparser
import logging
import os
import pathlib

CONFIG_FILE_NAME = 'configuration.ini'


def load_configuration(custom_path: pathlib.Path = None) -> configparser.ConfigParser:
    config_parser = configparser.ConfigParser()

    if custom_path:
        config_paths = [custom_path]
    else:
        config_paths = [pathlib.Path(os.path.join(directory, CONFIG_FILE_NAME)) for directory in
                        [".", os.path.dirname(__file__), os.path.expanduser("~/.geiger"), "/etc/geiger"]]

    for config_path in config_paths:
        if config_path.is_file():
            config_parser.read(config_path)
            logging.info("Configuration file loaded from: %s", config_path)
            return config_parser
        else:
            logging.debug("Skipping %s configuration file, because it doesn't exist.", config_path)

    raise Exception("no configuration file exists")
