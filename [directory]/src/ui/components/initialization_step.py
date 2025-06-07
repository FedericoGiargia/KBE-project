from __future__ import annotations

from typing import TYPE_CHECKING

from parapy.webgui import mui
from parapy.webgui.core import Component, State
from parapy.webgui.core.websocket.dispatchers import patch_layout
from parapy.webgui.layout import Box, Form
from ui.store import STORE

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class InitializationStep(Component):
    is_loading: bool = State(False)

    def on_submit(self, values: dict[str, float | int | str]) -> None:
        size = values["size"]
        if size > 500:
            raise ValueError("Pop size cannot be over 500")
        self.is_loading = True
        # we update the layout so that the user sees the loading symbol before
        # we start doing our expensive calculation (by going to the next step
        # the user will need to load the viewer and plotly, this takes a second
        # or two)
        patch_layout()
        STORE.pop_size = size
        STORE.height = values["height"]
        STORE.radius = values["radius"]
        STORE.shape = values["shape"]
        STORE.color = values["color"]

        STORE.step += 1

    def render(self) -> NodeType:
        return Box(height="100%", h_align="center")[
            mui.Paper(style={"width": "35em"})[
                Form(
                    children=[
                        {
                            "key": "height",
                            "text": "Height range",
                            "sub_text": "The range of balloon heights to be "
                            "generated. This is the height of the "
                            "balloon itself excluding basket.",
                            "default_value": STORE.height,
                            "value_type": "slider",
                            "min": 6,
                            "max": 14,
                        },
                        {
                            "key": "radius",
                            "text": "Radius range",
                            "sub_text": "The range of balloon radii to be "
                            "generated.",
                            "default_value": STORE.radius,
                            "value_type": "slider",
                            "min": 3,
                            "max": 8,
                            "step": 0.1,
                        },
                        {
                            "key": "shape",
                            "text": "Tube height",
                            "sub_text": "The height of the narrow part of "
                            "the balloon, low will result in an "
                            "egg shape whist high will result in "
                            "a mushroom shape.",
                            "default_value": STORE.shape,
                            "value_type": "slider",
                            "min": 0,
                            "max": 8,
                        },
                        {
                            "key": "size",
                            "text": "Population Size",
                            "default_value": STORE.pop_size,
                            "validator": lambda v: "Population size cannot be "
                            "over 500"
                            if v > 500
                            else None,
                        },
                        {
                            "key": "color",
                            "text": "Balloon color",
                            "default_value": STORE.color,
                            "value_type": "select",
                            "options": [
                                {"label": "red", "value": "red"},
                                {"label": "blue", "value": "blue"},
                                {"label": "green", "value": "green"},
                                {"label": "yellow", "value": "yellow"},
                            ],
                        },
                    ],
                    button_text="Generate population",
                    on_submit=self.on_submit,
                    title=mui.Typography(variant="h5")[
                        "Balloon population configuration"
                    ],
                    button_type=mui.LoadingButton,
                    button_props={
                        "endIcon": mui.Icon["send_icon"],
                        "loading": self.is_loading,
                        "loadingPosition": "end",
                    },
                )
            ]
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(InitializationStep, reload=True)
