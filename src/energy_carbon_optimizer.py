from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import product
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "utility_windows.csv"


@dataclass
class UtilityWindow:
    window: int
    shift: str
    demand_units: int
    grid_cost_usd_kwh: float
    carbon_kg_kwh: float
    ambient_c: float
    pressure_bar: float


def load_windows(path: Path = DATA_PATH) -> list[UtilityWindow]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            UtilityWindow(
                window=int(row["window"]),
                shift=row["shift"],
                demand_units=int(row["demand_units"]),
                grid_cost_usd_kwh=float(row["grid_cost_usd_kwh"]),
                carbon_kg_kwh=float(row["carbon_kg_kwh"]),
                ambient_c=float(row["ambient_c"]),
                pressure_bar=float(row["pressure_bar"]),
            )
            for row in csv.DictReader(handle)
        ]


def compressor_kwh(units: int, ambient_c: float, pressure_bar: float) -> float:
    base_specific_energy = 0.92
    pressure_penalty = 1.0 + 0.055 * max(0.0, pressure_bar - 7.0)
    thermal_penalty = 1.0 + 0.012 * max(0.0, ambient_c - 25.0)
    return units * base_specific_energy * pressure_penalty * thermal_penalty


def evaluate_schedule(windows: list[UtilityWindow], fractions: tuple[float, ...]) -> dict[str, float | tuple[float, ...]]:
    produced = 0
    cost = 0.0
    carbon = 0.0
    energy = 0.0

    for window, fraction in zip(windows, fractions):
        units = round(window.demand_units * fraction)
        kwh = compressor_kwh(units, window.ambient_c, window.pressure_bar)
        produced += units
        energy += kwh
        cost += kwh * window.grid_cost_usd_kwh
        carbon += kwh * window.carbon_kg_kwh

    return {
        "fractions": fractions,
        "produced": produced,
        "energy_kwh": round(energy, 2),
        "cost_usd": round(cost, 2),
        "carbon_kg": round(carbon, 2),
    }


def optimize(windows: list[UtilityWindow], required_units: int = 650, carbon_limit_kg: float = 360.0) -> dict[str, float | tuple[float, ...]]:
    candidates = (0.55, 0.70, 0.85, 1.00)
    best = None

    for fractions in product(candidates, repeat=len(windows)):
        result = evaluate_schedule(windows, fractions)
        if result["produced"] < required_units or result["carbon_kg"] > carbon_limit_kg:
            continue
        if best is None or result["cost_usd"] < best["cost_usd"]:
            best = result

    if best is None:
        raise RuntimeError("No feasible schedule found. Relax demand or carbon constraint.")
    return best


def run_optimizer() -> None:
    windows = load_windows()
    best = optimize(windows)
    print("Recommended operating schedule")
    for window, fraction in zip(windows, best["fractions"]):
        units = round(window.demand_units * fraction)
        kwh = compressor_kwh(units, window.ambient_c, window.pressure_bar)
        print(
            f"window={window.window} shift={window.shift:9s} "
            f"run={fraction:0.2f} units={units:3d} energy={kwh:6.1f} kWh "
            f"cost=${kwh * window.grid_cost_usd_kwh:5.2f}"
        )

    print(
        f"\nTotal production={best['produced']} units | "
        f"energy={best['energy_kwh']} kWh | cost=${best['cost_usd']} | carbon={best['carbon_kg']} kg"
    )


if __name__ == "__main__":
    run_optimizer()
