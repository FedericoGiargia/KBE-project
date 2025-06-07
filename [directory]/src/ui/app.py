from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from identity import get_display_name
from parapy.webgui import mui
from parapy.webgui.core import Component, State
from parapy.webgui.core.websocket.dispatchers import (
    patch_layout,
    register_post_patch_action,
)
from parapy.webgui.mui.themes import DefaultTheme
from persistence import PERSISTENCE_DISABLED, load
from ui.components.root import Root

if TYPE_CHECKING:
    from parapy.webgui.core.node import DiffStruct, NodeType


class App(Component):
    _current_user: Optional[str] = None
    is_loading: bool = State(False)
    show_welcome_msg: bool = State(True)
    show_loaded_msg: bool = State(False)

    @property
    def current_user(self) -> str:
        if self._current_user is None:
            self._current_user = get_display_name()
        return self._current_user

    def on_load(self) -> None:
        if PERSISTENCE_DISABLED:
            return

        self.is_loading = True
        patch_layout()
        from time import sleep

        sleep(0.5)
        self.show_loaded_msg = load()
        self.is_loading = False

    def on_welcome_snackbar_close(self, *args: Any) -> None:
        self.show_welcome_msg = False

    def on_loading_snackbar_close(self, *args: Any) -> None:
        self.show_loaded_msg = False

    def mount_node(self) -> DiffStruct:
        register_post_patch_action(self.on_load)
        return super().mount_node()

    def render(self) -> NodeType:
        return mui.ThemeProvider(theme=DefaultTheme)[
            Root(),
            mui.Modal(open=self.is_loading)[
                mui.Stack(
                    sx={
                        "height": "100%",
                        "alignItems": "center",
                        "justifyContent": "center",
                    }
                )[
                    mui.CircularProgress(sx={"fontSize": "48px"}),
                ]
            ],
            mui.Snackbar(
                open=self.show_welcome_msg,
                onClose=self.on_welcome_snackbar_close,
                autoHideDuration=5000,
                anchorOrigin={"vertical": "top", "horizontal": "center"},
            )[
                mui.Alert(severity="info", onClose=self.on_welcome_snackbar_close)[
                    f"Welcome {self.current_user}"
                ]
            ],
            mui.Snackbar(
                open=self.show_loaded_msg,
                onClose=self.on_loading_snackbar_close,
                autoHideDuration=5000,
                anchorOrigin={"vertical": "top", "horizontal": "center"},
            )[
                mui.Alert(severity="success", onClose=self.on_loading_snackbar_close)[
                    "Loaded application state!"
                ]
            ],
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(App, reload=True)
