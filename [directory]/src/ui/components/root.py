from __future__ import annotations

from typing import TYPE_CHECKING

from parapy.webgui.core import Component
from parapy.webgui.layout import Split
from ui.components.content import Content
from ui.components.header import Header

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


class Root(Component):
    def render(self) -> NodeType:
        return [
            Split(
                orientation="vertical",
                h_align="center",
                weights=[0, 1],
                height="100vh",
                style={"backgroundColor": "rgba(60, 60, 120, 0.1)"},
            )[Header(), Content()]
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(Root, reload=True)
