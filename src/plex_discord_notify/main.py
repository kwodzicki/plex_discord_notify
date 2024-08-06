"""
Main fucntion for socket listening

Listen to a socket for incoming Plex wehbooks and
process them in threads.

"""

import logging
import argparse
import signal
import socket
from threading import Thread

from . import (
    stop_handler,
    is_running,
    plex_webhook,
    discord_webhook,
    utils,
    ROT_HANDLER,
)

TIMEOUT = 1.0
BUFSIZE = 1024

signal.signal(signal.SIGINT,  stop_handler)
signal.signal(signal.SIGTERM, stop_handler)


def main(host='localhost', port=5000, **kwargs):
    """
    Main function for package

    Keyword arguments:
        host (str) : Name/IP of the host to listen on
        port (int) : Port to list for Plex webhook on
        **kwargs : All others passed to parsing thread.

    Returns:
        None.

    """

    log = logging.getLogger(__name__)
    log.debug("Setting up socket on %s:%d", host, port,)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_obj:
        s_obj.settimeout(
            kwargs.get('timeout', TIMEOUT)
        )
        s_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_obj.bind((host, port))
        s_obj.listen()

        while is_running():
            try:
                conn, addr = s_obj.accept()
            except socket.timeout:
                continue

            _ = Thread(
                target=on_new_client,
                args=(conn, addr, process_webhook,),
                kwargs=kwargs,
            ).start()
    log.info("Socket closed")


def process_webhook(
    data,
    *args,
    event_filters=None,
    library_filters=None,
    **kwargs,
):
    """
    Callback function for webhook processing

    This function applies filters to Plex webhooks before
    passing events to the Discord formatters.

    Arguments:
        data (bytes) : Byte array of data received from socket
        *args : All other arguments are ignored

    Keyword arguments:
        event_filters (str,list,tuple) : Types of events that should be
            sent to Discord
        library_filters (str,list,tuple) : Types of library media that
            are to be sent to Discord
        **kwargs : All other silently ignored

    Returns:
        ?
    """

    event = plex_webhook.parse_webhook(data)
    if not utils.event_filter(event, event_filters):
        return None
    if not utils.library_filter(event, library_filters):
        return None
    return discord_webhook.process_plex_webhook(event)


def on_new_client(
    conn,
    addr,
    callback,
    *args,
    bufsize=BUFSIZE,
    timeout=TIMEOUT,
    **kwargs,
):
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
            except socket.timeout:
                log.debug('Recieved timed out')
                break

            if not tmp:
                break

            data += tmp
    return callback(data, *args, **kwargs)


def cli():

    parser = argparse.ArgumentParser(
        description=(
            "Simple relay to capture Plex webhooks, format them, "
            "and send to Discord"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host URL/name to listen for webhooks on',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen to on host address for webhooks',
    )
    parser.add_argument(
        '-e', '--event-filters',
        type=str,
        nargs='+',
        default='library.new',
        help=(
            'Any number of Plex wehbook events to enable for Discord messaging'
        )
    )
    parser.add_argument(
        '-l', '--library-filters',
        type=str,
        nargs='+',
        default='movie',
        help=(
            'Any number of Plex library section types to enable for Discord '
            'messaging. Possible types are: "movie", "show", and "artist".'
        ),
    )
    parser.add_argument(
        '--log-level',
        type=int,
        default=30,
        help='Logging level for the log file',
    )
    args = parser.parse_args()

    ROT_HANDLER.setLevel(args.log_level)

    main(
        host=args.host,
        port=args.port,
        event_filters=args.event_filters,
        library_filters=args.library_filters,
    )
