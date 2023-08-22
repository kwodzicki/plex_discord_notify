"""
Relay for Plex webhook to Discord

Using sockets, Plex webhooks are captured, parsed,
and pushed to Discord to notify people that new content
has been added to the Plex server.

"""

import logging
from logging.handlers import RotatingFileHandler

import os
from threading import Event

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

LOGDIR = os.path.join(
    os.path.expanduser('~'),
    'Library',
    'Application Support',
    __name__,
    'logs',
)
os.makedirs(LOGDIR, exist_ok=True)

ROT_HANDLER = RotatingFileHandler(
    os.path.join(LOGDIR, 'plex_discord_notify.log'),
    maxBytes    = 5 * 2**20,
    backupCount = 4,
)
ROT_HANDLER.setLevel(logging.INFO)
ROT_HANDLER.setFormatter(
    logging.Formatter(
        '%(levelname)-.4s - %(asctime)s - %(name)s.%(funcName)-15.15s - %(message)s',
        '%Y-%m-%d %H:%M:%S',
    )
)
LOG.addHandler(ROT_HANDLER)

STOP_EVENT = Event()

def stop_handler(*args, **kwargs):
    """
    Handler for 'stop' event

    """

    STOP_EVENT.set()

def is_running():
    """
    Function for if running

    Returns:
        bool : If no interrupt or kill accepted, then return True,
            else return False

    """

    return not STOP_EVENT.is_set()
