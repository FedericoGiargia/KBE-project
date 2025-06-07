from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

from parapy.webgui import mui
from parapy.webgui.core import Component
from parapy.webgui.layout import Margin, Split
from ui.components.initialization_step import InitializationStep
from ui.components.refinement_step import RefinementStep
from ui.components.reporting_step import ReportingStep
from ui.components.selection_step import SelectionStep
from ui.store import STORE

if TYPE_CHECKING:
    from parapy.webgui.core.node import NodeType


STEPS = ["Population generation", "Analysis", "Refinement", "Reporting"]


class Content(Component):
    def select_step(self, idx: int, *args: Any) -> None:
        STORE.step = idx

    def render(self) -> NodeType:
        step = STORE.step
        if step == 0:
            content = InitializationStep()
        elif step == 1:
            content = SelectionStep()
        elif step == 2:
            content = RefinementStep()
        elif step == 3:
            content = ReportingStep()

        steps_disabled = [
            False,
            not STORE.models,
            STORE.final_design is None,
            STORE.final_design is None,
        ]

        step_buttons = [
            mui.Step(
                label=label,
                completed=idx < step,
                active=not steps_disabled[idx],
                disabled=steps_disabled[idx],
            )[
                mui.StepButton(color="inherit", onClick=partial(self.select_step, idx))[
                    label
                ]
            ]
            for idx, label in enumerate(STEPS)
        ]

        return Split(orientation="vertical", height="100%", weights=[0, 1])[
            # We add a stepper bar so the user knows at which step he is
            Margin("1.5em")[
                # We use a container since it has a nice default for the width
                # This width is dynamically selected based on screen size
                mui.Container[
                    mui.Stepper(activeStep=step, className="stepper", nonLinear=True)[
                        step_buttons
                    ]
                ]
            ],
            content,
        ]


if __name__ == "__main__":
    from parapy.webgui.core import display

    display(Content, reload=True)
