import logging
import signal
import socket
from threading import Thread

from . import stop_handler, is_running, plex_webhook, discord_webhook, utils

TIMEOUT = 1.0
BUFSIZE = 1024

signal.signal(signal.SIGINT,  stop_handler)
signal.signal(signal.SIGTERM, stop_handler)

def main(host='localhost', port=5000, **kwargs):

    log = logging.getLogger(__name__)
    log.debug("Setting up socket on %s:%d", host, port,)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(
            kwargs.get('timeout', TIMEOUT)
        )
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind( (host, port) )
        s.listen()

        while is_running():
            try:
                conn, addr = s.accept()
            except socket.timeout as err:
                continue

            _ = Thread(
                target = on_new_client,
                args   = (conn, addr, process_webhook,),
                kwargs = kwargs,
            ).start()
    log.info("Socket closed")

def process_webhook(data, *args, event_filters=None, library_filter=None, **kwargs):

    event = plex_webhook.parse_webhook(data)
    if not utils.event_filter(event, event_filters):
        return
    if not utils.library_filter(event, library_filter):
        return 
    return discord_webhook.process_plex_webhook(event)

def on_new_client(conn, addr, callback, *args, bufsize=BUFSIZE, timeout=TIMEOUT, **kwargs):
    """
    Receive all data from connection

    On a new connection to the socket, read all the data from the socket
    and return it. If a callback function is defined, pass the data read
    from the socket to the callback function and return result.

    Arguments:
        conn (socket) : New socket object to receive data from
        addr (str) : Address of the socket
        callback (func) : Reference to function to pass data to after
            all data read from socket. The callback function MUST accept
            a bytes string as input
        *args : Any additional arguments are passed to the callback function

    Keyword arguments:
        bufsize (int) : Maximum number of bytes to receive from the
            socket at one time
        timeout (float) : Number of seconds to wait between reads of
            the socket before assuming got all data.
        **kwargs : Any addition arguments are passed to the callback function

    Returns:
        A bytes string if no callback function is defined OR whatever the
        return from the callback function is.

    """

    log = logging.getLogger(__name__)
    data = b'' 
    with conn:
        conn.settimeout(timeout)
        log.debug("Connected by %s", addr)
        while True:
            try:
                tmp = conn.recv(bufsize)
            except socket.timeout as err:
                log.debug('Recieved timed out')
                break

            if not tmp:
                break

            data += tmp
    return callback(data, *args, **kwargs)
