import logging
import os
 
def load_hook_url():

    log = logging.getLogger(__name__)
    url_file = os.path.join(
        os.path.expanduser('~'),
        ".discord_webhook_url",
    )
    if not os.path.isfile(url_file):
        log.warning("Discord webhook URL file not exist : %s", url_file)
        return None

    with open(url_file, mode='r') as iid:
        return iid.read().strip()

def event_filter(event, filters):
    """
    Filter based on Plex event type

    Arguments:
        event (dict) : Parsed data from Plex webhook event
        filters (str,list,tuple) : Various filters for the types of
            events to be handled

    Returns:
        bool : True if event matches filters, False otherwise

    """

    if filters is None:
        return True

    event_type = event.get('json', {}).get('event', '')
    if event_type not in filters:
        return False
 
    return True

def library_filter(event, filters):
    """
    Filter based on Plex library type

    Arguments:
        event (dict) : Parsed data from Plex webhook event
        filters (str,list,tuple) : Various filters for the types of
            events to be handled

    Returns:
        bool : True if event matches filters, False otherwise

    """


    if filters is None:
        return True

    lib_type = (
        event
        .get('json', {})
        .get('Metadata', {})
        .get('librarySectionType', '')
    )
    if lib_type not in filters:
        return False
 
    return True 
