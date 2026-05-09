from __future__ import annotations

from copy import deepcopy

from .rule_checker import run_rule_checks
from .section_calculator import calculate_all

try:
    from scipy.optimize import minimize
except Exception:  # optional dependency fallback
    minimize = None


def optimize_section(section, objective: str = "area", penalty_factor: float = 1e5) -> dict:
    optimized_section = deepcopy(section)
    vars_meta = []

    for i, p in enumerate(optimized_section.plates):
        if p.is_design_variable:
            lb = p.min_thickness if p.min_thickness > 0 else 1e-4
            ub = max(p.thickness * 1.5, lb * 1.5)
            vars_meta.append(("plate", i, lb, ub, p.thickness, p.id))

    for i, s in enumerate(optimized_section.stiffeners):
        if s.is_design_variable:
            lb = s.min_area if s.min_area > 0 else 1e-5
            ub = max(s.area * 1.5, lb * 1.5)
            vars_meta.append(("stiffener", i, lb, ub, s.area, s.id))

    x0 = [v[4] for v in vars_meta]
    bounds = [(v[2], v[3]) for v in vars_meta]
    history = []

    def apply_x(x):
        for val, (kind, idx, *_rest) in zip(x, vars_meta):
            if kind == "plate":
                optimized_section.plates[idx].thickness = float(val)
            else:
                optimized_section.stiffeners[idx].area = float(val)

    def penalized_obj(x):
        apply_x(x)
        calc = calculate_all(optimized_section)
        checks = run_rule_checks(optimized_section, calc)
        base = calc["total_area"] if objective == "area" else calc["weight_per_meter"]
        penalty = sum(max(0.0, -c["margin"]) ** 2 for c in (checks["global_checks"] + checks["member_checks"]))
        val = base + penalty_factor * penalty
        history.append({"objective": val, "base": base, "penalty": penalty})
        return val

    if minimize is not None and len(x0) > 0:
        res = minimize(penalized_obj, x0=x0, bounds=bounds, method="L-BFGS-B")
        apply_x(res.x)
    else:
        x = x0[:]
        for _ in range(20):
            improved = False
            for i in range(len(x)):
                trial = x[:]
                trial[i] = max(bounds[i][0], trial[i] * 0.97)
                if penalized_obj(trial) <= penalized_obj(x):
                    x = trial
                    improved = True
            if not improved:
                break
        apply_x(x)

    initial_results = calculate_all(section)
    optimized_results = calculate_all(optimized_section)

    changed_variables = []
    for kind, idx, _lb, _ub, init, var_id in vars_meta:
        new_val = optimized_section.plates[idx].thickness if kind == "plate" else optimized_section.stiffeners[idx].area
        if abs(new_val - init) > 1e-10:
            changed_variables.append({"id": var_id, "type": kind, "initial": init, "optimized": new_val})

    return {
        "initial_results": initial_results,
        "optimized_section": optimized_section,
        "optimized_results": optimized_results,
        "optimization_history": history,
        "area_reduction_percent": (initial_results["total_area"] - optimized_results["total_area"]) / initial_results["total_area"] * 100.0,
        "weight_reduction_percent": (initial_results["weight_per_meter"] - optimized_results["weight_per_meter"]) / initial_results["weight_per_meter"] * 100.0,
        "changed_variables": changed_variables,
    }
