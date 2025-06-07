"""
The client to IAM for obtaining identity information.

In a production environment the following environment variables
are automatically available. Hence, a client can be instantiated
without passing any arguments.

- ``PARAPY_IAM_URL``,
- ``PARAPY_WEBAUTH_TOKEN``.

In a development environment the `TestingClient` is used.
"""
import os

PRODUCTION_MODE = bool(os.getenv("PARAPY_IAM_URL", False))


if PRODUCTION_MODE:
    from parapy.cloud.iam.client import Client

    client = Client()  # NOTE: already in an authenticated environment
else:
    from parapy.cloud.iam.client import TestingClient as Client

    client = Client()  # NOTE: authentication is mocked
