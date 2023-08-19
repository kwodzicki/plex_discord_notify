import logging
import os 
import json

import requests

from .utils import load_hook_url

HOOK_URL = load_hook_url()

def process_plex_webhook(event):

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
        r = requests.post(HOOK_URL, files=files)
    except Exception as err:
        log.exception( err )
        return False

    return r

def format_library_new(event):
    """
    Format Discord message for library.new event

    """

    server   = event['json'].get('Server',   {}).get('title', '')
    metadata = event['json'].get('Metadata', {})
    mtype    = metadata.get('type',    '')
    title    = metadata.get('title',   '')
    year     = metadata.get('year',    '')
    tag      = metadata.get('tagline', '')
    rating   = metadata.get('contentRating', '')
    summary  = metadata.get('summary', '')

    content = (
        f"A new {mtype} has been added to {server}:",
        f"{title} ({year})",
        summary,
    )

    return build_files(
        "\n\n".join(content),
        event.get('poster', None),
    )

def build_files(content, poster=None):

    files    = {}
    payload  = {
        'content' : content,
    }

    if poster is not None:
        payload['embeds'] = [{
            'image' : {
                'url' : f'attachment://poster.jpg',
            }
        }]
        files['poster.jpg'] = poster

    files['payload_json'] = (None, json.dumps(payload))

    return files

   
