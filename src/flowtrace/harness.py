from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from .sdk import record_user_action, start_run


@dataclass(frozen=True)
class SimulatedInputScenario:
    name: str
    payload: Any
    tags: tuple[str, ...] = ()


def run_simulated_scenario(
    scenario: SimulatedInputScenario,
    runner: Callable[[Any], Any],
    *,
    run_label_prefix: str = "模拟输入",
) -> dict[str, Any]:
    with start_run(f"{run_label_prefix} - {scenario.name}"):
        record_user_action(
            "simulated.input",
            {
                "scenario": scenario.name,
                "payload": scenario.payload,
                "tags": list(scenario.tags),
            },
            actor="simulator",
        )
        try:
            result = runner(scenario.payload)
        except BaseException as exc:
            record_user_action(
                "simulated.error",
                {
                    "scenario": scenario.name,
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                },
                actor="simulator",
            )
            return {
                "scenario": scenario.name,
                "status": "error",
                "error_type": exc.__class__.__name__,
                "error_message": str(exc),
            }

        record_user_action(
            "simulated.result",
            {
                "scenario": scenario.name,
                "result": result,
            },
            actor="simulator",
        )
        return {
            "scenario": scenario.name,
            "status": "ok",
            "result": result,
        }


def run_simulated_scenarios(
    scenarios: Iterable[SimulatedInputScenario],
    runner: Callable[[Any], Any],
    *,
    run_label_prefix: str = "模拟输入",
) -> list[dict[str, Any]]:
    return [run_simulated_scenario(scenario, runner, run_label_prefix=run_label_prefix) for scenario in scenarios]

