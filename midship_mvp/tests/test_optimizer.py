from src.io_utils import load_section_model
from src.optimizer import optimize_section


def test_optimizer_runs_and_returns_changes():
    section = load_section_model('data/sample_ship.json')
    out = optimize_section(section)
    assert out['optimized_section'] is not None
    assert out['optimized_results']['total_area'] <= out['initial_results']['total_area'] * 1.01
    assert 'changed_variables' in out
