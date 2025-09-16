"""Time series validation and repair utilities.

Focused on lightweight numeric guards to augment LLM generated sensor data.
Files kept <200 lines per project guidelines.
"""
from __future__ import annotations

from typing import List, Dict, Tuple, Optional
import math

# ---------- Core Numeric Helpers ----------

def _differences(values: List[float]) -> List[float]:
    return [b - a for a, b in zip(values, values[1:])]

def _count_direction_changes(values: List[float]) -> int:
    # Counts sign changes (excluding zeros) to detect sawtooth
    diffs = _differences(values)
    last_sign = 0
    changes = 0
    for d in diffs:
        sign = 0
        if d > 0: sign = 1
        elif d < 0: sign = -1
        if sign == 0:
            continue
        if last_sign != 0 and sign != last_sign:
            changes += 1
        last_sign = sign
    return changes

def _count_local_extrema(values: List[float]) -> Tuple[int,int]:
    peaks = 0
    valleys = 0
    for i in range(1, len(values)-1):
        if values[i] > values[i-1] and values[i] > values[i+1]:
            peaks += 1
        if values[i] < values[i-1] and values[i] < values[i+1]:
            valleys += 1
    return peaks, valleys

# ---------- Deterministic Generators (Fallback) ----------

def generate_diurnal_temperature(length: int, min_temp: float = 20.0, max_temp: float = 26.0) -> List[float]:
    """Generate a smooth single-cycle diurnal temperature curve.
    Uses a cosine shifted so that minimum around index ~0.125*L (early morning) and peak ~0.625*L (afternoon).
    """
    if length <= 1:
        return [ (min_temp + max_temp)/2.0 ] * max(1,length)
    vals: List[float] = []
    for i in range(length):
        # phase in [0,1)
        phase = i/length
        # shift phase so min at ~0.15, max at ~0.65
        shifted = (phase - 0.15) % 1.0
        # cosine: cos(2pi*(shifted-0.15)) would put min at phase 0.15; we want value low then high
        v = 0.5 - 0.5*math.cos(2*math.pi*shifted)  # 0..1 single smooth peak
        temp = min_temp + v*(max_temp - min_temp)
        vals.append(temp)
    return vals

# ---------- Repair Operations ----------

def smooth_sequence(values: List[float], passes: int = 1) -> List[float]:
    if len(values) < 3:
        return values
    out = values[:]
    for _ in range(passes):
        new_vals = out[:]
        for i in range(1, len(out)-1):
            new_vals[i] = (out[i-1] + out[i] + out[i+1]) / 3.0
        out = new_vals
    return out

# ---------- Validation ----------

def _estimate_cycles(values: List[float]) -> Dict[str, float]:
    """Estimate number of cycles using peak spacing heuristic.
    Returns dict with cycle_count (float) and avg_peak_distance.
    """
    peaks_positions: List[int] = []
    for i in range(1, len(values)-1):
        if values[i] > values[i-1] and values[i] > values[i+1]:
            peaks_positions.append(i)
    if len(peaks_positions) < 2:
        return {"cycle_count": 1.0 if peaks_positions else 0.0, "avg_peak_distance": float(len(values))}
    distances = [b - a for a, b in zip(peaks_positions, peaks_positions[1:])]
    avg = sum(distances)/len(distances)
    est_cycles = len(values)/avg if avg > 0 else 0.0
    return {"cycle_count": est_cycles, "avg_peak_distance": avg, "peaks_detected": len(peaks_positions)}


def validate_temperature_series(values: List[float], *, max_direction_changes: int = 4, max_extrema: int = 2, max_step: float = 2.0, enforce_single_cycle: bool = False) -> Dict[str, object]:
    """Validate temperature specific realism constraints.
    - At most one peak & one valley (single daily cycle) -> allow slight noise so thresholds are small (<=2 each)
    - Limited direction changes to prevent sawtooth
    - Reasonable per-step delta
    """
    if not values:
        return {"valid": False, "reason": "empty", "metrics": {}}
    peaks, valleys = _count_local_extrema(values)
    diffs = _differences(values)
    max_abs_step = max((abs(d) for d in diffs), default=0.0)
    direction_changes = _count_direction_changes(values)
    cycle_info = _estimate_cycles(values)
    cycle_ok = True
    if enforce_single_cycle:
        # allow minor overshoot: treat anything >1.6 estimated cycles as violation
        cycle_ok = cycle_info["cycle_count"] <= 1.6
    valid = (
        peaks <= max_extrema and valleys <= max_extrema and
        direction_changes <= max_direction_changes and
        max_abs_step <= max_step and cycle_ok
    )
    return {
        "valid": valid,
        "reason": "ok" if valid else "violations",
        "metrics": {
            "peaks": peaks,
            "valleys": valleys,
            "direction_changes": direction_changes,
            "max_abs_step": max_abs_step,
            "length": len(values),
            **cycle_info,
            "enforce_single_cycle": enforce_single_cycle
        }
    }


def validate_generic_series(values: List[float], *, max_step: float = 10_000.0) -> Dict[str, object]:
    if not values:
        return {"valid": False, "reason": "empty", "metrics": {}}
    diffs = _differences(values)
    max_abs_step = max((abs(d) for d in diffs), default=0.0)
    return {
        "valid": max_abs_step <= max_step,
        "reason": "ok" if max_abs_step <= max_step else "large_step",
        "metrics": {"max_abs_step": max_abs_step, "length": len(values)}
    }


def validate_and_repair(tag_name: str, values: List[float], *, time_horizon: Optional[object] = None) -> Dict[str, object]:
    """Entry point used by handlers.
    Attempts repair (smoothing) once for temperature series before falling back to deterministic diurnal.
    Returns dict with final_values, source, validation metrics, fallback flags.
    """
    lower = tag_name.lower()
    is_temp = any(w in lower for w in ["temp", "temperature", "thermal"])

    if not is_temp:
        gen = validate_generic_series(values)
        return {"final_values": values, "source": "llm", "validation": gen}

    # Temperature path
    enforce_single = False
    if time_horizon:
        # Expect attributes: period, unit, granularity
        try:
            if getattr(time_horizon, 'period', None) == 24 and getattr(time_horizon, 'unit', '').lower().startswith('hour'):
                # If granularity is minutes (contains 'minute') or less than 60 in granularity text, enforce single cycle
                gran = str(getattr(time_horizon, 'granularity', '')).lower()
                if 'min' in gran or '5' in gran or '15' in gran:
                    enforce_single = True
        except Exception:
            pass

    primary = validate_temperature_series(values, enforce_single_cycle=enforce_single)
    if primary["valid"]:
        return {"final_values": values, "source": "llm", "validation": primary}

    # Try smoothing once
    smoothed = smooth_sequence(values, passes=2)
    smooth_val = validate_temperature_series(smoothed, enforce_single_cycle=enforce_single)
    if smooth_val["valid"]:
        return {"final_values": smoothed, "source": "llm_smoothed", "validation": smooth_val, "repaired": True}

    # Fallback deterministic diurnal
    diurnal = generate_diurnal_temperature(len(values), min(values), max(values))
    diurnal_val = validate_temperature_series(diurnal, enforce_single_cycle=True)
    diurnal_val["forced_single_cycle"] = True
    return {"final_values": diurnal, "source": "diurnal_fallback", "validation": diurnal_val, "repaired": False, "fallback": True}

__all__ = [
    "validate_and_repair",
    "generate_diurnal_temperature",
]
