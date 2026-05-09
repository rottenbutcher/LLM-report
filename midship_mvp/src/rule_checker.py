from __future__ import annotations

from .models import SectionModel


def _mk_check(name: str, target: str, passed: bool, margin: float, details: str = "") -> dict:
    return {"check": name, "target": target, "pass": passed, "margin": float(margin), "details": details}


def run_rule_checks(section: SectionModel, calc_results: dict, max_slenderness: float = 120.0) -> dict:
    global_checks: list[dict] = []
    member_checks: list[dict] = []

    for plate in section.plates:
        if plate.min_thickness > 0:
            margin = plate.thickness / plate.min_thickness - 1.0
        else:
            margin = 1.0
        member_checks.append(_mk_check("min_thickness", plate.id, margin >= 0.0, margin))

        slenderness = plate.length / plate.thickness
        margin_b = max_slenderness / slenderness - 1.0
        member_checks.append(
            _mk_check(
                "simple_buckling_proxy",
                plate.id,
                slenderness <= max_slenderness,
                margin_b,
                "Simplified proxy, not full CSR buckling.",
            )
        )

    for stiff in section.stiffeners:
        if stiff.min_area > 0:
            margin = stiff.area / stiff.min_area - 1.0
        else:
            margin = 1.0
        member_checks.append(_mk_check("min_stiffener_area", stiff.id, margin >= 0.0, margin))

    z_deck_margin = calc_results["Z_deck"] / section.ship.required_section_modulus_deck - 1.0
    z_bottom_margin = calc_results["Z_bottom"] / section.ship.required_section_modulus_bottom - 1.0
    global_checks.append(_mk_check("section_modulus_deck", "global", z_deck_margin >= 0.0, z_deck_margin))
    global_checks.append(_mk_check("section_modulus_bottom", "global", z_bottom_margin >= 0.0, z_bottom_margin))

    for elem_id, stress in calc_results["member_stresses"].items():
        material_name = next((p.material for p in section.plates if p.id == elem_id), None)
        if material_name is None:
            material_name = next(s.material for s in section.stiffeners if s.id == elem_id)
        allowable = section.materials[material_name].yield_stress * section.materials[material_name].allowable_stress_factor
        margin = allowable / max(abs(stress), 1e-12) - 1.0
        member_checks.append(_mk_check("allowable_stress", elem_id, abs(stress) <= allowable, margin))

    all_checks = global_checks + member_checks
    active_constraints = [c for c in all_checks if (not c["pass"]) or c["margin"] < 0.05]
    return {
        "global_checks": global_checks,
        "member_checks": member_checks,
        "overall_pass": all(c["pass"] for c in all_checks),
        "active_constraints": active_constraints,
    }
