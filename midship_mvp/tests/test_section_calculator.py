from src.io_utils import load_section_model
from src.section_calculator import calculate_all


def test_section_properties_positive_and_reasonable():
    section = load_section_model('data/sample_ship.json')
    results = calculate_all(section)
    assert results['total_area'] > 0.0
    assert section.ship.bottom_z <= results['neutral_axis_z'] <= section.ship.deck_z
    assert results['Z_deck'] > 0.0 and results['Z_bottom'] > 0.0
