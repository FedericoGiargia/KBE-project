import os
import pathlib

from persistence.client import PRODUCTION_MODE, Client, client
from persistence.model import StoreModel
from ui.store import STORE

if PRODUCTION_MODE:
    PERSISTENCE_DIR = pathlib.Path.home() / ".parapy" / ".state"
else:
    PERSISTENCE_DIR = pathlib.Path(__file__).parent.parent.parent / ".state"
SAVE_FILENAME = "save.json"
PERSISTENCE_DISABLED = PRODUCTION_MODE and not bool(os.getenv("PARAPY_APP_MODEL_ID"))


def load(client: Client = client, location: pathlib.Path = PERSISTENCE_DIR) -> bool:
    with client.session(download_dir=location) as session:
        if session.files.exists(SAVE_FILENAME):
            session.files.download(SAVE_FILENAME, overwrite=True)
        else:
            return False

    data_model_location = location / SAVE_FILENAME

    _ = StoreModel.deserialize(data_model_location, store=STORE)

    return True


def save(
    client: Client = client, location: pathlib.Path = PERSISTENCE_DIR
) -> pathlib.Path:
    location.mkdir(parents=True, exist_ok=True)
    data_model_location = location / SAVE_FILENAME

    StoreModel.serialize(data_model_location, store=STORE)

    with client.session() as session:
        session.files.stage(
            local_path=data_model_location,
            remote_path=data_model_location.name,
        )
        session.commit()

    return data_model_location


def reset(client: Client = client, location: pathlib.Path = PERSISTENCE_DIR) -> None:
    try:
        (location / SAVE_FILENAME).unlink()
    except FileNotFoundError:
        pass

    with client.session() as session:
        if session.files.exists(SAVE_FILENAME):
            session.files.delete(SAVE_FILENAME)
