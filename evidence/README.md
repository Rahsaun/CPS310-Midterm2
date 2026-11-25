# Demonstration evidence

Start with the two summary tables. The folders below them contain the full inputs and intermediate results.

| Evidence | What it establishes |
| --- | --- |
| [Original comparison summary](pipeline/run_1/summary.csv) | Valid 40-agent and 1,000-agent scenarios, three injected faults and a recovery replay. |
| [180-agent comparison summary](pipeline/session_2/summary.csv) | Naive and controlled responses both pass, followed by an injected rejection and a newly authored correction response. |
| [Test log](pipeline/tests.txt) | Results of the 12 pipeline and simulation tests. |
| [Original provenance](pipeline/run_1/provenance.json) and [180-agent provenance](pipeline/session_2/provenance.json) | Response origins, fault labels, runtime versions and implementation hashes. |

## Inspect a demonstration

Each attempt folder has `report.json` with its validation stages and final status. Attempts that reach generation include `candidate.py`. Successful executions include `simulation.json` with the population history. Failed executions retain their error logs. Context folders preserve the exact task, ontology and composed prompts. The correction attempt also has its feedback prompt.

Redundant saved copies of accepted code and empty logs have been omitted from this committed evidence. `candidate.py` is the code evaluated in each attempt, and `report.json` records whether it was accepted. Fresh runs generate their complete outputs, including accepted files.

## Reproduce all results

From the repository root, run the setup commands in the README, then execute the following.

```powershell
py run_demos.py --output results/demos
```

Review `results/demos/validation/summary.csv` and `results/demos/session/summary.csv`. Use a new output directory for each run. The stored results are historical recordings, and fresh runs record the current reproduction-script hash and environment.
