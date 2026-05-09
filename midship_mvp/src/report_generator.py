from __future__ import annotations

from pathlib import Path


def generate_reports(section, initial_calc, initial_checks, opt_bundle, optimized_checks, retrieved_chunks, output_dir: str = ".") -> tuple[str, str]:
    out_dir = Path(output_dir)
    report_path = out_dir / "output_report.md"
    prompt_path = out_dir / "llm_prompt.txt"

    changed = opt_bundle["changed_variables"][:8]
    rag_lines = [f"- {c['source']} (score={c['score']:.4f}): {c['text'][:160].replace(chr(10),' ')}..." for c in retrieved_chunks]

    md = f"""# Midship Section MVP Engineering Report

## Input Summary
- Ship: {section.ship.name}
- Depth: {section.ship.depth} m
- Deck z: {section.ship.deck_z} m, Bottom z: {section.ship.bottom_z} m

## Initial Calculation Results
- Total area: {initial_calc['total_area']:.4f} m^2
- Neutral axis z: {initial_calc['neutral_axis_z']:.4f} m
- I_y: {initial_calc['I_y']:.4f} m^4
- Z_deck: {initial_calc['Z_deck']:.4f} m^3
- Z_bottom: {initial_calc['Z_bottom']:.4f} m^3
- Weight per meter: {initial_calc['weight_per_meter']:.2f} kg/m

## Rule Check Summary
- Initial overall pass: {initial_checks['overall_pass']}
- Optimized overall pass: {optimized_checks['overall_pass']}
- Active constraints count: {len(optimized_checks['active_constraints'])}

## Optimization Summary
- Area reduction: {opt_bundle['area_reduction_percent']:.2f}%
- Weight reduction: {opt_bundle['weight_reduction_percent']:.2f}%
- Major changed variables:
""" + "\n".join([f"  - {x['id']} ({x['type']}): {x['initial']:.6f} -> {x['optimized']:.6f}" for x in changed]) + f"""

## RAG Retrieved References
""" + "\n".join(rag_lines) + """

## Engineering Interpretation
This MVP indicates early-stage midship scantling trends and active constraints. Thickness and stiffener area changes should be interpreted as conceptual optimization signals only.

## Limitations
- Not a full CSR implementation.
- Buckling check is a simplified proxy only.
- Section properties are based on simplified area representation.
- Intended for early-stage conceptual review only.
- Final design requires full CSR verification, direct strength analysis, fatigue assessment, and class approval.
"""

    opt_summary = {
        "area_reduction_percent": opt_bundle["area_reduction_percent"],
        "weight_reduction_percent": opt_bundle["weight_reduction_percent"],
        "changed_variables": opt_bundle["changed_variables"],
    }

    prompt = f"""You are reviewing midship calculation outputs.
Use only the provided values and do not invent numbers.
Explain active constraints and design-variable changes.
Mention simplified buckling proxy and that this is not final class approval.

CALC_INITIAL={initial_calc}
CHECKS_INITIAL={initial_checks}
OPT_BUNDLE={opt_summary}
CHECKS_OPTIMIZED={optimized_checks}
RAG_CONTEXT={retrieved_chunks}
"""

    report_path.write_text(md, encoding="utf-8")
    prompt_path.write_text(prompt, encoding="utf-8")
    return str(report_path), str(prompt_path)
