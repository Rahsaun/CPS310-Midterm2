# CPS310 Zombie Ontology Pipeline

**Individual process-control assignment by Rahsaun Jeffrey**

This repository implements an ontology-guided pipeline for AI development of executable scenarios using the existing Zombie Game.

- Read the [complete assignment answer](docs/PROCESS_CONTROL_PIPELINE.md) for the design, argument, comparisons and results.
- Inspect the [ontology](control_pipeline/ontology.json) and [major prompts](control_pipeline/prompts/).
- Review the [committed demonstrations](evidence/pipeline/run_1/) and [comparison table](evidence/pipeline/run_1/summary.csv).
- Review the [test log](evidence/pipeline/tests.txt).

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py -m control_pipeline.demo --output results/pipeline-demo
```

Use a new output directory for each run. The demonstration includes 40-agent and 1,000-agent scenarios using the real simulation. Candidate responses were authored by the ChatGPT assistant during development. Deliberately injected faults are labeled in the evidence.

The game foundation was imported from [dokeefe414/CPS310-Zombie-Game](https://github.com/dokeefe414/CPS310-Zombie-Game) at commit `81464f9`. Original game contributors are Daniel O'Keefe, Owen Bowers and Rahsaun Jeffrey. The documentation below describes that inherited foundation.


## Runtime dependencies

`Zombie_Game.py` supplies the simulation used by the demos. It imports `models.py`, `forecasting.py` and `db_manager.py`. Install Python with Tkinter available. The headless demos require the Python database driver but can run without a PostgreSQL server.

Each demo output directory contains the exact prompts, ontology snapshots, generated code, validation results and simulation histories required for the assignment.
