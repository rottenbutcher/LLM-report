# Midship Section MVP (Python)

This MVP is a lightweight computational tool for early-stage midship section structural review.

## What it does
- Loads ship/material/section element data from JSON.
- Computes simplified section properties (area, neutral axis, I_y, section modulus).
- Computes simplified bending stress by element.
- Runs simplified rule-style checks.
- Optimizes plate thickness/stiffener area with penalty constraints.
- Builds local RAG context from `.txt` files.
- Generates deterministic markdown report and LLM-ready prompt.

## What it does **not** do
- No GUI.
- No visualization.
- No direct strength FE analysis.
- No full CSR implementation.
- No fatigue assessment.
- No external LLM API call.

## Run
```bash
cd midship_mvp
python main.py
```
Outputs:
- `output_report.md`
- `llm_prompt.txt`

## Project structure
- `src/models.py`: dataclasses
- `src/section_calculator.py`: section property & stress calculations
- `src/rule_checker.py`: simplified rule checks
- `src/optimizer.py`: penalized optimization
- `src/rag.py`: local text retrieval
- `src/report_generator.py`: report output
- `src/io_utils.py`: JSON input loading
- `data/sample_ship.json`: sample input
- `data/sample_rag_docs/*.txt`: RAG corpus
- `tests/`: pytest tests

## Simplified engineering assumptions
- Section representation is area-lumped by plate and stiffener centroids.
- I_y is computed with simplified parallel-axis area terms only.
- Buckling is a **simplified slenderness proxy**, not CSR buckling.
- Rule checks are conceptual and not class submission ready.

## MVP vs full CSR/HullScan
This MVP demonstrates calculation flow and review logic, but not full rule completeness, numerical fidelity, or production-grade scantling workflows expected from full CSR/HullScan-like platforms.

## Important disclaimer
This MVP is **not** a full CSR implementation. It is for early-stage conceptual calculation and review. Final structural design requires full CSR verification, direct strength analysis, fatigue assessment, and class approval.

## Future extensions
- Integrate real CSR formulas and chapter mapping.
- Add direct strength analysis coupling.
- Add fatigue checks.
- Add GUI/visualization.
- Integrate real LLM API.
- Add PDF parsing for CSR documents.
- Upgrade retrieval to richer embeddings/vector DB.
