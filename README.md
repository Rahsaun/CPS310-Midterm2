# CPS310-Midterm2

**Rahsaun Jeffrey**

An ontology-guided process control pipeline for developing executable Zombie Game scenarios with AI assistance.

## Start here

| What to review | Where to find it |
| --- | --- |
| All nine pipeline steps, overall design and concrete arguments | [Assignment report](docs/PROCESS_CONTROL_PIPELINE.md) |
| Domain concepts, relationships and executable constraints | [Ontology](control_pipeline/ontology.json) |
| Major design, argument, generation and repair prompts | [Prompts](control_pipeline/prompts/README.md) |
| Demo results and intermediate artifacts | [Evidence index](evidence/README.md) |
| Implementation | [Controller](control_pipeline/pipeline.py), [runtime](control_pipeline/runtime.py) and [demo runner](run_demos.py) |

## Run all demos

Open a terminal in this repository's folder. Use Python 3.10 or later with Tkinter installed.

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py run_demos.py --output results/demos
```

On macOS or Linux, use `python3` in place of `py`. Use a fresh output directory for each run, such as `results/demos-2`.

The command runs the valid 40-agent, 1,000-agent and 180-agent scenarios, the controlled-versus-naive comparisons, and the rejection and correction examples. It saves summaries to `results/demos/validation/summary.csv` and `results/demos/session/summary.csv`. Intentional rejections are expected demo outcomes. Detailed instructions and expected results are in the report.

## Credits and scope

The simulation foundation comes from [CPS310-Zombie-Game](https://github.com/dokeefe414/CPS310-Zombie-Game), developed by Daniel O'Keefe, Owen Bowers and Rahsaun Jeffrey. This individual submission adds the ontology, development pipeline, prompts, tests and comparisons.

The demonstrations use saved AI-assisted responses. Injected faults are identified in the evidence. Both initial responses in the 180-agent comparison pass, and their shared assistant context is recorded in the provenance.
