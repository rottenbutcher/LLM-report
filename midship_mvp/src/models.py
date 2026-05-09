from dataclasses import dataclass


@dataclass
class Material:
    name: str
    density: float
    yield_stress: float
    allowable_stress_factor: float = 0.72


@dataclass
class PlateElement:
    id: str
    y: float
    z: float
    length: float
    thickness: float
    material: str
    group: str
    min_thickness: float = 0.0
    is_design_variable: bool = True

    @property
    def area(self) -> float:
        return self.length * self.thickness


@dataclass
class StiffenerElement:
    id: str
    y: float
    z: float
    area: float
    material: str
    group: str
    min_area: float = 0.0
    is_design_variable: bool = True


@dataclass
class ShipData:
    name: str
    length: float
    breadth: float
    depth: float
    scantling_draft: float
    design_bending_moment_hogging: float
    design_bending_moment_sagging: float
    required_section_modulus_deck: float
    required_section_modulus_bottom: float
    deck_z: float
    bottom_z: float


@dataclass
class SectionModel:
    ship: ShipData
    materials: dict[str, Material]
    plates: list[PlateElement]
    stiffeners: list[StiffenerElement]
