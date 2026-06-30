# Thermodynamic Power Optimizer and Real-Time Carbon Compliance Model

This project is a runnable prototype for plant energy optimization. It estimates compressor utility efficiency, calculates cost and carbon intensity across shift windows, and recommends an operating schedule that respects demand and carbon limits.

## Why It Matters

Manufacturing plants need to balance production demand, energy price spikes, machine efficiency, and carbon constraints. Running utilities blindly can create avoidable cost and compliance risk.

## What Is Included

- `src/energy_carbon_optimizer.py` - thermodynamic and scheduling prototype
- `data/utility_windows.csv` - sample shift, demand, grid cost, and carbon data
- `requirements.txt` - no external packages required
- `GITHUB_NOTES.md` - how to publish this project to GitHub

## Run

```bash
python src/energy_carbon_optimizer.py
```

## Engineering Concepts Demonstrated

- Compressor power estimation
- Pressure-drop and efficiency penalties
- Energy cost calculation
- Carbon emission calculation
- Constraint-based production scheduling
- Industrial energy management architecture

## Real-World Extension

This prototype uses a compact search instead of an external optimization solver. A production version could use linear programming, mixed-integer optimization, or a plant historian connection.
