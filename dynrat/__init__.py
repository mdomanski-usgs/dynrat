import logging

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

info_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(info_formatter)
