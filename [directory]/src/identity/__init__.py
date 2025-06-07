import logging

from identity.client import Client, client

logger = logging.getLogger(__name__)


def get_display_name(client: Client = client) -> str:
    try:
        return client.get_me().display_name
    except Exception as e:
        logger.error(e)
        return "<unknown>"
