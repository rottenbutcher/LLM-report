from src.io_utils import load_section_model
from src.rule_checker import run_rule_checks
from src.section_calculator import calculate_all


def test_rule_checks_margins_and_active_constraints():
    section = load_section_model('data/sample_ship.json')
    section.plates[0].thickness = 0.005
    calc = calculate_all(section)
    checks = run_rule_checks(section, calc)
    mt = [c for c in checks['member_checks'] if c['check'] == 'min_thickness' and c['target'] == section.plates[0].id][0]
    assert mt['margin'] < 0.0
    sz = [c for c in checks['global_checks'] if c['check'] == 'section_modulus_deck'][0]
    assert isinstance(sz['margin'], float)
    assert len(checks['active_constraints']) > 0
