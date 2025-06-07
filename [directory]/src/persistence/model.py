import json
import pathlib
from typing import List, Optional

from model.balloon import HotAirBalloon
from parapy.core.datamodel import DataModel
from ui.store import Store

MODEL_VERSION = "1"


class HotAirBalloonModel(DataModel):
    opening_radius: float
    radius: float
    half_height: float
    tube_height: float
    height: float
    basket_width: float
    basket_length: float
    rope_length: float
    color: str

    class Config:
        base_type = HotAirBalloon
        lazy = False
        field_lazy = False


class StoreModel(DataModel):
    _custom_dump_key = "_custom_"

    selected: HotAirBalloonModel
    models: List[HotAirBalloonModel]
    final_design: HotAirBalloonModel

    class Config:
        base_type = Store
        lazy = False

    @classmethod
    def serialize(cls, location: pathlib.Path, *, store: Store) -> None:
        model = cls.from_base(store)
        model_dct = model.dump(version=MODEL_VERSION)

        model_dct["data"][cls._custom_dump_key] = dict(
            step=store.step,
            pop_size=store.pop_size,
            height=store.height,
            radius=store.radius,
            shape=store.shape,
            color=store.color,
        )

        with location.open("w") as f:
            json.dump(model_dct, f)

    @classmethod
    def deserialize(
        cls, location: pathlib.Path, *, store: Optional[Store] = None
    ) -> Store:
        if store is None:
            store = Store()

        with location.open("r") as f:
            model_dct = json.load(f)

        custom_dump = model_dct["data"].pop(cls._custom_dump_key)
        store.step = custom_dump["step"]
        store.pop_size = custom_dump["pop_size"]
        store.height = custom_dump["height"]
        store.radius = custom_dump["radius"]
        store.shape = custom_dump["shape"]
        store.color = custom_dump["color"]

        model = cls.load(model_dct)
        store.selected = HotAirBalloon()
        store.final_design = HotAirBalloon()
        store.models.quantify = len(model.models)
        model.to_base(store)

        return store
