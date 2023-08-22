"""
Parse Plex webhooks

"""

import json
import re

def parse_webhook(resp):
    """
    Parse JSON and image data from Plex Webhook

    Arguments:
        resp (bytes) : Byte data from the Plex Webhook

    Returns:
        dict : Has keys 'json' and 'file', with file being the
            poster data

    """

    boundary = get_boundary(resp)
    if boundary is None:
        return None

    out = {}
    matches = re.finditer(b'Content-Type:((?:.|\n)*?)'+boundary, resp)
    for match in matches:
        ctype, *data = match.group(1).splitlines(keepends=True)
        if b'json' in ctype:
            out['json'] = parse_json(data)
        elif b'image' in ctype:
            out['poster'] = parse_image(data)

    return out

def parse_json(data):
    """
    Parse JSON from byte string

    """

    out = {}
    for val in data:
        try:
            out.update( json.loads(val) )
        except:
            pass
    return out

def parse_image(data):
    """
    Get image data from byte string

    """

    return b''.join(data).strip()

def get_boundary(val):
    """
    Extract the boundary value from form data

    """

    try:
        boundary = re.findall(br'boundary=([^\r\n]*)', val)[0]
    except:
        return None

    return b"--" + boundary
