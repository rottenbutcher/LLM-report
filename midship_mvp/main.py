from __future__ import annotations

from pathlib import Path

from src.io_utils import load_section_model
from src.optimizer import optimize_section
from src.rag import build_retriever, chunk_documents, load_documents
from src.report_generator import generate_reports
from src.rule_checker import run_rule_checks
from src.section_calculator import calculate_all


def build_rag_query(initial_checks: dict, optimized_checks: dict, opt_bundle: dict, optimized_results: dict) -> str:
    failed = [c["check"] for c in optimized_checks["global_checks"] + optimized_checks["member_checks"] if not c["pass"]]
    active = [c["check"] for c in optimized_checks["active_constraints"][:8]]
    changed = [c["id"] for c in opt_bundle["changed_variables"][:8]]
    return " ".join([
        "deck section modulus bottom section modulus stress margin buckling proxy thickness stiffener area optimization",
        " ".join(failed),
        " ".join(active),
        " ".join(changed),
        f"max_stress_{optimized_results['max_abs_stress']:.3e}",
    ])


def main() -> None:
    root = Path(__file__).parent
    section = load_section_model(str(root / "data" / "sample_ship.json"))

    initial_calc = calculate_all(section)
    initial_checks = run_rule_checks(section, initial_calc)

    opt_bundle = optimize_section(section, objective="area")
    optimized_section = opt_bundle["optimized_section"]
    optimized_calc = opt_bundle["optimized_results"]
    optimized_checks = run_rule_checks(optimized_section, optimized_calc)

    docs = load_documents(str(root / "data" / "sample_rag_docs"))
    chunks = chunk_documents(docs)
    retriever = build_retriever(chunks)
    query = build_rag_query(initial_checks, optimized_checks, opt_bundle, optimized_calc)
    retrieved = retriever.retrieve(query, top_k=5)

    report_path, prompt_path = generate_reports(
        section,
        initial_calc,
        initial_checks,
        opt_bundle,
        optimized_checks,
        retrieved,
        output_dir=str(root),
    )

    print("=== Midship MVP Summary ===")
    print(f"Initial area: {initial_calc['total_area']:.4f} m^2")
    print(f"Optimized area: {optimized_calc['total_area']:.4f} m^2")
    print(f"Area reduction: {opt_bundle['area_reduction_percent']:.2f}%")
    print(f"Initial pass: {initial_checks['overall_pass']}")
    print(f"Optimized pass: {optimized_checks['overall_pass']}")
    print(f"Active constraints: {[c['check'] + ':' + c['target'] for c in optimized_checks['active_constraints'][:8]]}")
    print(f"Report saved: {report_path}")
    print(f"LLM prompt saved: {prompt_path}")


if __name__ == "__main__":
    main()
