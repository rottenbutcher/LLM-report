from __future__ import annotations

from .models import SectionModel


def _all_elements(section: SectionModel):
    for plate in section.plates:
        yield plate.id, plate.z, plate.area, plate.material
    for stiff in section.stiffeners:
        yield stiff.id, stiff.z, stiff.area, stiff.material


def calculate_total_area(section: SectionModel) -> float:
    return sum(area for _, _, area, _ in _all_elements(section))


def calculate_neutral_axis_z(section: SectionModel) -> float:
    """z_NA = sum(A_i * z_i) / sum(A_i)."""
    total_area = calculate_total_area(section)
    if total_area <= 0.0:
        raise ValueError("Total area must be positive.")
    return sum(area * z for _, z, area, _ in _all_elements(section)) / total_area


def calculate_second_moment_area_y(section: SectionModel, neutral_axis_z: float) -> float:
    """Simplified I_y = sum(A_i * (z_i - z_NA)^2)."""
    return sum(area * (z - neutral_axis_z) ** 2 for _, z, area, _ in _all_elements(section))


def calculate_section_modulus(section: SectionModel, I_y: float, neutral_axis_z: float) -> tuple[float, float]:
    z_deck_dist = abs(section.ship.deck_z - neutral_axis_z)
    z_bottom_dist = abs(neutral_axis_z - section.ship.bottom_z)
    if z_deck_dist == 0.0 or z_bottom_dist == 0.0:
        raise ValueError("Neutral axis coincides with deck or bottom reference.")
    return I_y / z_deck_dist, I_y / z_bottom_dist


def calculate_bending_stress(M: float, z: float, neutral_axis_z: float, I_y: float) -> float:
    """sigma = M * (z - z_NA) / I_y."""
    if I_y <= 0.0:
        raise ValueError("Second moment of area must be positive.")
    return M * (z - neutral_axis_z) / I_y


def calculate_member_stresses(section: SectionModel, M: float, neutral_axis_z: float, I_y: float) -> dict[str, float]:
    stresses: dict[str, float] = {}
    for eid, z, _, _ in _all_elements(section):
        stresses[eid] = calculate_bending_stress(M, z, neutral_axis_z, I_y)
    return stresses


def calculate_weight_per_meter(section: SectionModel) -> float:
    """Weight proxy per meter = sum(A_i * rho_i), units kg/m."""
    total = 0.0
    for _, _, area, material in _all_elements(section):
        total += area * section.materials[material].density
    return total


def calculate_all(section: SectionModel) -> dict:
    total_area = calculate_total_area(section)
    neutral_axis_z = calculate_neutral_axis_z(section)
    I_y = calculate_second_moment_area_y(section, neutral_axis_z)
    Z_deck, Z_bottom = calculate_section_modulus(section, I_y, neutral_axis_z)
    member_stresses = calculate_member_stresses(
        section,
        section.ship.design_bending_moment_hogging,
        neutral_axis_z,
        I_y,
    )
    max_abs_stress = max(abs(v) for v in member_stresses.values()) if member_stresses else 0.0
    return {
        "total_area": total_area,
        "neutral_axis_z": neutral_axis_z,
        "I_y": I_y,
        "Z_deck": Z_deck,
        "Z_bottom": Z_bottom,
        "weight_per_meter": calculate_weight_per_meter(section),
        "max_abs_stress": max_abs_stress,
        "member_stresses": member_stresses,
    }
