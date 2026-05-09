from __future__ import annotations

import json
from pathlib import Path

from .models import Material, PlateElement, SectionModel, ShipData, StiffenerElement


def load_section_model(json_path: str) -> SectionModel:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    ship = ShipData(**data["ship"])
    materials = {k: Material(**v) for k, v in data["materials"].items()}
    plates = [PlateElement(**p) for p in data["plates"]]
    stiffeners = [StiffenerElement(**s) for s in data["stiffeners"]]
    return SectionModel(ship=ship, materials=materials, plates=plates, stiffeners=stiffeners)
