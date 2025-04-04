"""
Format and push messages to Discord

"""

import logging
import json

import requests

from .utils import load_hook_url

HOOK_URL = load_hook_url()
TIMEOUT = 10.0


def process_plex_webhook(event):
    """
    Process a Plex webhook

    Arguments:
        event (dict) : A parsed Plex webhook event

    Returns:
        Response object from requests.post()

    """

    log = logging.getLogger(__name__)

    if HOOK_URL is None:
        log.error("No Discord webhook url loaded!")
        return False

    if 'json' not in event:
        log.error("No JSON data in the event")
        return False

    event_type = event['json'].get('event', '')
    if event_type == 'library.new':
        log.info("New media added!")
        files = format_library_new(event)
    else:
        log.error("Event type '%s' is NOT currently supported", event_type)
        return False

    try:
        res = requests.post(HOOK_URL, files=files, timeout=TIMEOUT)
    except Exception as err:
        log.exception(err)
        return False

    return res


def format_library_new(event):
    """
    Format Discord message for library.new event

    """

    server = event['json'].get('Server', {}).get('title', '')
    metadata = event['json'].get('Metadata', {})
    mtype = metadata.get('type', '')
    title = metadata.get('title', '')
    year = metadata.get('year', '')
    edition = metadata.get('editionTitle', '')
    summary = metadata.get('summary', '')

    content = f"{title} ({year})"
    if edition != '':
        content = f"{content} - {edition}"

    content = (
        f"A new {mtype} has been added to {server}:",
        content,
        summary,
    )

    return build_files(
        "\n\n".join(content),
        event.get('poster', None),
    )


def build_files(content, poster=None):
    """
    Build dict of data to attach

    Arguments:
        content (str) : Content of message to push to Discord

    Keyword arguments:
        poster (bytes) : Byte data for media poster to attach

    Returns:
        dict : Files to attach to the POST request
            sent to Discord webhook

    """

    files = {}
    payload = {
        'content': content,
    }

    if poster is not None:
        payload['embeds'] = [{
            'image': {
                'url': 'attachment://poster.jpg',
            }
        }]
        files['poster.jpg'] = poster

    files['payload_json'] = (None, json.dumps(payload))

    return files
