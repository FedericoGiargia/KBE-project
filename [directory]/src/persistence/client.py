"""
The client to Datastore for persisting data.

In a production environment the following environment variables
are automatically available. Hence, a client can be instantiated
without passing any arguments.

- ``PARAPY_DATASTORE_URL``,
- ``PARAPY_IAM_URL``,
- ``PARAPY_APP_MODEL_ID`` and
- ``PARAPY_WEBAUTH_TOKEN``.

In a development environment the `TestingClient` is used.
"""
import os

PRODUCTION_MODE = bool(os.getenv("PARAPY_DATASTORE_URL", False))


if PRODUCTION_MODE:
    from parapy.cloud.datastore.client import Client

    client = Client()  # NOTE: already in an authenticated environment
else:
    import pathlib

    from parapy.cloud.datastore.client import TestingClient as Client

    Client.default_storage_dir = pathlib.Path(__file__).parent.parent.parent / ".remote"
    client = Client()  # NOTE: authentication is mocked
