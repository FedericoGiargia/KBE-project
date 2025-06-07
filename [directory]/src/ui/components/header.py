from __future__ import annotations

from typing import TYPE_CHECKING, Any

from parapy.webgui import mui
from parapy.webgui.app_bar import AppBar
from parapy.webgui.core import Component, State
from parapy.webgui.core.websocket.dispatchers import patch_layout
from parapy.webgui.layout import Box, MarginRight
from persistence import PERSISTENCE_DISABLED, reset, save
from ui.store import STORE

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class Header(Component):
    is_saving: bool = State(False)
    is_resetting: bool = State(False)
    side_bar: bool = State(False)
    snackbar_msg: str = State("")

    def on_save(self, *args: Any) -> None:
        if PERSISTENCE_DISABLED:
            return

        self.is_saving = True
        patch_layout()
        from time import sleep

        sleep(0.5)
        save()
        self.is_saving = False

    def show_side_bar(self, *args: Any) -> None:
        self.side_bar = True

    def close_side_bar(self) -> None:
        self.side_bar = False

    def select_step(self, idx: int) -> None:
        STORE.step = idx
        self.close_side_bar()

    def on_snackbar_close(self, *args: Any) -> None:
        self.snackbar_msg = ""

    def drawer_content(self) -> NodeType:
        def _reset(*, hard: bool):
            STORE.reset(hard=hard)
            if hard:
                reset()
            self.snackbar_msg = f"{'Hard' if hard else 'Soft'} reset application state!"
            self.close_side_bar()

        def _soft_reset(*args: Any) -> None:
            _reset(hard=False)

        def _hard_reset(*args: Any) -> None:
            _reset(hard=True)

        def _start_reset(*args: Any) -> None:
            self.is_resetting = True

        def _cancel_reset(*args: Any) -> None:
            self.is_resetting = False

        return mui.List()[
            mui.ListItem(disablePadding=True)[
                mui.ListItemButton(onClick=lambda evt: self.select_step(0))[
                    mui.ListItemIcon[mui.Icon("settings_icon")],
                    mui.ListItemText["Population config"],
                ]
            ],
            mui.ListItem(disablePadding=True)[
                mui.ListItemButton(
                    disabled=not STORE.models,
                    onClick=lambda evt: self.select_step(1),
                )[
                    mui.ListItemIcon[mui.Icon("assignment_turned_in_icon")],
                    mui.ListItemText["Design selection"],
                ]
            ],
            mui.ListItem(disablePadding=True)[
                mui.ListItemButton(
                    disabled=STORE.final_design is None,
                    onClick=lambda evt: self.select_step(2),
                )[
                    mui.ListItemIcon[mui.Icon("speed_icon")],
                    mui.ListItemText["Design refinement"],
                ]
            ],
            mui.ListItem(disablePadding=True)[
                mui.ListItemButton(
                    disabled=STORE.final_design is None,
                    onClick=lambda evt: self.select_step(3),
                )[
                    mui.ListItemIcon[mui.Icon("assessment_icon")],
                    mui.ListItemText["Report"],
                ]
            ],
            mui.Divider(),
            mui.ListItem(disablePadding=True)[
                mui.ListItemButton(onClick=_start_reset)[
                    mui.ListItemIcon[mui.Icon("rotate_left_icon")],
                    mui.ListItemText["Reset"],
                ]
            ],
            mui.Dialog(
                open=self.is_resetting,
                onClose=_cancel_reset,
            )[
                mui.DialogTitle["Reset"],
                mui.DialogContent[
                    (
                        "Apply a soft or hard reset of the application. A soft "
                        "reset keeps the population generation configuration and "
                        "the save file (if applicable), while a hard reset "
                        "restores the application to its original state."
                    )
                ],
                mui.DialogActions[
                    mui.Button(
                        variant="contained",
                        onClick=_cancel_reset,
                        style={"backgroundColor": "gray"},
                    )["Cancel"],
                    mui.Button(
                        variant="contained",
                        color="primary",
                        onClick=_hard_reset,
                    )["Hard reset"],
                    mui.Button(
                        variant="contained",
                        color="primary",
                        onClick=_soft_reset,
                    )["Soft reset"],
                ],
                mui.IconButton(
                    sx={"position": "absolute", "right": "0"},
                    size="large",
                    onClick=_cancel_reset,
                )[mui.Icon["close"]],
            ],
        ]

    def render(self) -> NodeType:
        return [
            AppBar(title="ParaPy app")[
                MarginRight[
                    Box(height="100%", h_align="right", v_align="center")[
                        mui.Tooltip(title="Save the application state")[
                            mui.LoadingButton(
                                startIcon=mui.Icon["save"],
                                variant="contained",
                                color="secondary",
                                onClick=self.on_save,
                                disabled=PERSISTENCE_DISABLED
                                or STORE.final_design is None,
                                loading=self.is_saving,
                            )["Save"]
                        ]
                    ]
                ]
            ],
            mui.Fab(
                onClick=self.show_side_bar,
                size="small",
                style={
                    "position": "absolute",
                    "left": 0,
                    "top": "50vh",
                    "transform": "translate(-30%, -50%)",
                },
            )[mui.Icon["chevron_right"]],
            mui.Drawer(
                open=self.side_bar,
                onClose=lambda evt, reason: self.close_side_bar(),
                ModalProps={
                    "style": {"zIndex": 1202}
                },  # so that it appears over the appbar, the appbar has a zindex of 1201
            )[self.drawer_content() if self.side_bar else None],
            mui.Snackbar(
                open=self.snackbar_msg,
                onClose=self.on_snackbar_close,
                autoHideDuration=5000,
                anchorOrigin={"vertical": "top", "horizontal": "center"},
            )[
                mui.Alert(severity="success", onClose=self.on_snackbar_close)[
                    self.snackbar_msg
                ]
            ],
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(Header, reload=True)
