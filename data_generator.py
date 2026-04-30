"""Synthetic SCADA data generator for AquaSmart SEWA demo.

This file intentionally creates fake, realistic-looking operational data.
It is not connected to any SEWA live system.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

ZONES = {
    "Zubara": {
        "lat": 25.3527,
        "lon": 56.3525,
        "base_flow": 62,
        "base_pressure": 5.8,
        "base_consumption": 1180,
        "profile": "stable residential",
    },
    "Mussala": {
        "lat": 25.3467,
        "lon": 56.3577,
        "base_flow": 94,
        "base_pressure": 5.2,
        "base_consumption": 1760,
        "profile": "mixed commercial demand",
    },
    "Hayawa": {
        "lat": 25.3402,
        "lon": 56.3529,
        "base_flow": 82,
        "base_pressure": 4.9,
        "base_consumption": 1510,
        "profile": "high demand residential",
    },
    "Al Luluyah": {
        "lat": 25.3332,
        "lon": 56.3605,
        "base_flow": 54,
        "base_pressure": 5.5,
        "base_consumption": 980,
        "profile": "coastal community",
    },
    "Al Wurrayah": {
        "lat": 25.3957,
        "lon": 56.3126,
        "base_flow": 122,
        "base_pressure": 4.7,
        "base_consumption": 2240,
        "profile": "transmission/storage influence",
    },
}


def generate_scada_data(hours: int = 168, freq_minutes: int = 15, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    periods = int(hours * 60 / freq_minutes)
    start_time = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=freq_minutes * periods)
    timestamps = pd.date_range(start=start_time, periods=periods, freq=f"{freq_minutes}min")

    rows: list[dict] = []
    for zone, cfg in ZONES.items():
        for i, ts in enumerate(timestamps):
            hour = ts.hour + ts.minute / 60
            daily_pattern = 1 + 0.18 * np.sin((hour - 6) / 24 * 2 * np.pi) + 0.10 * np.sin((hour - 18) / 24 * 2 * np.pi)
            weekend_boost = 1.06 if ts.weekday() >= 5 else 1.0
            noise = rng.normal(0, 0.05)

            flow = cfg["base_flow"] * daily_pattern * weekend_boost * (1 + noise)
            pressure = cfg["base_pressure"] - 0.15 * (daily_pattern - 1) + rng.normal(0, 0.10)
            consumption = cfg["base_consumption"] * daily_pattern * weekend_boost * (1 + rng.normal(0, 0.06))
            leak_probability = max(0.02, rng.normal(0.09, 0.03))
            anomaly = False
            event_type = "Normal"
            response_time = max(20, rng.normal(85, 18))

            # Zone-specific operational behavior
            if zone == "Mussala" and i > periods * 0.55:
                flow *= 1.20
                consumption *= 1.16
                leak_probability += 0.16
                event_type = "High Consumption"

            if zone == "Hayawa" and periods * 0.68 < i < periods * 0.78:
                flow *= 1.34
                pressure -= 1.15
                consumption *= 1.05
                leak_probability += 0.46
                anomaly = True
                event_type = "Possible Leak"
                response_time = max(30, rng.normal(135, 25))

            if zone == "Al Wurrayah" and i > periods * 0.72:
                pressure -= 0.75
                flow *= 1.18
                leak_probability += 0.28
                if rng.random() > 0.35:
                    anomaly = True
                    event_type = "Pressure Drop"
                    response_time = max(35, rng.normal(125, 24))

            if rng.random() < 0.008:
                flow *= rng.uniform(1.30, 1.75)
                pressure -= rng.uniform(0.45, 1.05)
                leak_probability += rng.uniform(0.25, 0.45)
                anomaly = True
                event_type = "Transient Spike"

            leak_probability = float(np.clip(leak_probability, 0.02, 0.98))
            nrw_loss = float(np.clip((flow - (consumption / 24)) / max(flow, 1) * 100, 8, 38) + leak_probability * 5)
            efficiency = float(np.clip(100 - nrw_loss - (leak_probability * 8), 58, 94))

            # Rules are deliberately transparent for demo and operator trust.
            if (flow > cfg["base_flow"] * 1.28 and pressure < cfg["base_pressure"] - 0.65) or leak_probability > 0.62:
                anomaly = True
                if event_type in ["Normal", "High Consumption"]:
                    event_type = "Possible Leak"

            if anomaly and leak_probability >= 0.62:
                status = "Critical"
            elif leak_probability >= 0.33 or pressure < cfg["base_pressure"] - 0.55 or event_type == "High Consumption":
                status = "Warning"
            else:
                status = "Normal"

            rows.append(
                {
                    "timestamp": ts,
                    "zone_name": zone,
                    "zone_profile": cfg["profile"],
                    "latitude": cfg["lat"],
                    "longitude": cfg["lon"],
                    "flow_rate_m3h": round(float(flow), 2),
                    "pressure_bar": round(float(max(1.1, pressure)), 2),
                    "consumption_m3": round(float(max(200, consumption)), 2),
                    "leakage_probability": round(leak_probability, 3),
                    "system_status": status,
                    "anomaly_flag": int(anomaly),
                    "event_type": event_type,
                    "nrw_loss_pct": round(nrw_loss, 2),
                    "response_time_min": round(float(response_time), 1),
                    "system_efficiency_pct": round(efficiency, 2),
                }
            )
    return pd.DataFrame(rows)


def ensure_sample_csv(path: str | Path = "sample_scada_data.csv", seed: int = 42) -> pd.DataFrame:
    path = Path(path)
    if path.exists():
        df = pd.read_csv(path, parse_dates=["timestamp"])
    else:
        df = generate_scada_data(seed=seed)
        df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    output = Path(__file__).resolve().parent / "sample_scada_data.csv"
    df = generate_scada_data(seed=42)
    df.to_csv(output, index=False)
    print(f"Created {output} with {len(df):,} rows")
