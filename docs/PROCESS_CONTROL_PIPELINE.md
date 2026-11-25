# Ontology-guided development pipeline

**CPS310 Midterm 2 — Rahsaun Jeffrey**

## 1. Purpose and overall design

This project implements a process control pipeline for AI-assisted development of executable Zombie Game scenarios. The development task is bounded to arena dimensions, population composition, tick count, random seed and agent strategy. A model supplies a JSON scenario specification. A fixed generator turns it into Python that configures and runs the existing simulation, including civilian movement, armed attacks, zombie pursuit, bites and conversion.

The design uses successive acceptance gates. The task states the requested behavior. The ontology defines the accepted domain vocabulary and constraints. The controller checks the proposed specification, generates Python, executes the game and verifies its observed state. A failure produces feedback for correction. Acceptance follows successful checks, and each attempt records evidence.

The components have distinct responsibilities.

| Component | Role |
| --- | --- |
| `control_pipeline/ontology.json` | Defines concepts, relationships, configuration properties and constraints. |
| `control_pipeline/pipeline.py` | Builds prompts, validates responses, generates code and manages acceptance. |
| `control_pipeline/runtime.py` | Connects generated scenarios to the real simulation and checks runtime invariants. |
| `run_demos.py` | Runs all recorded comparisons and correction examples. |
| `evidence/` | Preserves outcomes, prompts, ontology snapshots, generated code and provenance. |

The model interaction is manual so an accessible model can be used without an API subscription. The demonstration commands replay saved responses. A new response can be supplied using the commands in Section 6.

## 2. Every pipeline step

| Step | Action and design reason | Output |
| --- | --- | --- |
| 1. Specify requirements | Record the task identifier, goal and exact configuration. Validate the starting request so the pipeline has an explicit acceptance target. | `task.json` |
| 2. Bind the ontology and source | Check declared inheritance against the game and hash the implementation, prompts and ontology. This detects context drift between preparation and evaluation. | `ontology.json`, `source_hashes.json` |
| 3. Construct prompts | Combine the task with the controlled instructions and ontology. Also produce a naive prompt for comparison. | `prompt_controlled.txt`, `prompt_naive.txt` |
| 4. Obtain a candidate | Supply the prompt to an AI model, save its complete JSON response and record its origin. This preserves the proposed implementation for review. | Candidate response |
| 5. Validate the candidate | Check JSON structure, duplicate keys, supported fields, types, bounds, population rules, ontology version and exact task values. Recheck source hashes. Invalid proposals stop here. | Validation result or rejection feedback |
| 6. Generate Python | Render validated values as Python literals in a fixed launcher template, then parse and compile it. This controls the executable structure. | `candidate.py` |
| 7. Execute and observe | Run the generated scenario in a child process with a 120-second timeout. Check live state and capture the population history and errors. | Execution logs and `simulation.json` |
| 8. Accept or correct | Accept after compilation, execution and task evaluation succeed. Otherwise produce a feedback prompt. Evaluate a correction in a fresh attempt directory. | `accepted.py` or `repair_prompt.txt` |
| 9. Preserve and review evidence | Save stage completion, hashes, inputs and results so the final artifact can be traced to its requirements. | `report.json` and demonstration evidence |

Fresh directories preserve earlier attempts. Successful controlled acceptance uses an atomic file replacement. Scenario execution uses fixed Python and NumPy seeds with one simulation worker. Accepted files remain available for review before incorporation into other work.

## 3. Ontology and enforcement

The ontology represents a typed JSON graph with concepts, relations, properties and rules.

| Domain relationship | Meaning and enforcement |
| --- | --- |
| Human inherits Agent | Source binding verifies the Python inheritance declaration. |
| ArmedHuman inherits Human | Armed civilians count as humans, including in runtime type checks. |
| Zombie inherits Agent | Zombies share agent state and occupy the zombie collection. |
| SimulationPlayground contains Agent | Runtime checks verify collection types, unique objects and population capacity. |
| Zombie converts Human | Describes the conversion relation. Simulation regression tests exercise conversion, while runtime checks observe resulting state. |
| ArmedHuman attacks Zombie | Describes the domain interaction exercised by the real simulation. |
| Scenario configures SimulationPlayground | Supported properties map to the runtime adapter. Unknown properties are rejected. |
| SimulationPlayground uses Strategy | Allowed values are `thompson` and `rush_only`. |

Every configurable property has an owning concept and allowed type or enumeration. Boolean values cannot substitute for integer counts. Rule R1 caps the combined population at 10,000. Rule R2 requires at least one human. The chosen operating bounds require at least one zombie, arena dimensions from 200 to 2,000 and a tick budget from 1 to 300. These are implementation bounds that keep the demonstrations manageable and accommodate the game's spawning and scent-grid behavior.

Runtime invariants require unique live objects, correct collection types, finite coordinates and health, live health above zero and within its maximum, arena boundaries, exact initial counts, population within initial capacity and correct tick progression. Descriptive relationships provide model context. The implemented gates and tests define the behavior actually checked.

## 4. Concrete arguments and comparison

The naive acceptance policy generates Python and accepts it after compilation. The experiment subsequently executes it and applies the same observer and task evaluator to measure correctness. The controlled policy requires those checks before acceptance. Replaying the same candidate through both policies isolates the effect of the acceptance gates.

| Argument | Mechanism and concrete outcome | Evidence |
| --- | --- | --- |
| Domain vocabulary prevents incompatible code from reaching acceptance. | The injected `infection_rate` property falls outside the supported vocabulary. Controlled validation rejects it before generation. The naive workflow accepts its compiling launcher, then encounters an unexpected-keyword error. | `evidence/pipeline/run_1/unknown_api_controlled/report.json` and `unknown_api_naive/stderr.txt` |
| Population constraints catch values that valid Python syntax permits. | The injected armed count of -2 compiles, but `range(-2)` creates zero armed civilians. Controlled validation rejects the negative count. The naive workflow accepts it and subsequently fails the requested initial-count check. | The `negative_count_controlled` and `negative_count_naive` attempt folders in `run_1` |
| Task fidelity protects the requested experiment even when code executes. | Seed 99 is a valid domain value but differs from the requested seed 7. Controlled validation rejects the change. The naive run finishes with 30 humans and 8 zombies, compared with 28 humans and 12 zombies for the requested seed, then fails task evaluation. | The `changed_requirement` reports, `small_context/task.json` and corresponding histories in `run_1` |
| Runtime gates make execution behavior a condition of acceptance. | The controller runs the actual game and observes its invariants. Tests confirm that a simulated execution failure prevents controlled promotion. Compilation alone cannot establish these behaviors. | `tests/test_control_pipeline.py` and `evidence/pipeline/tests.txt` |
| Validation supports successful development and correction. | Both policies pass the valid scenarios. After an unsupported property is injected, its feedback is used to author a complete corrected response. The correction passes the controlled pipeline. | `evidence/pipeline/session_2/injected_rejection/` and `corrected/` |
| Saved context improves traceability. | Each result is connected to a task, ontology, response and source hashes. A changed context causes rejection and requires preparation again. | Context snapshots, receipts and the context-mutation test |

For the three chosen faults, the controlled policy accepts zero faulty artifacts and the naive policy prematurely accepts all three. Both workflows accept the valid scenarios. The concrete improvement demonstrated here is enforcement of the specified acceptance conditions for the tested inputs.

The faults are deliberately injected. The responses in the 180-agent comparison share one assistant context, which already included knowledge of the game and ontology. Both initial responses pass. These results establish the demonstrated control behavior within this task. Estimating AI-generation error rates or a prompt-quality advantage would require independent model trials. The ontology and tests also have limited coverage, so valid scenarios can still have undesirable game dynamics.

## 5. Demonstrations and observed outcomes

| Demonstration | Recorded outcome |
| --- | --- |
| 40-agent scenario | Both policies pass after 30 ticks, with 28 humans and 12 zombies. |
| 1,000-agent scenario | Both policies pass after 10 ticks, with 795 humans and 205 zombies. |
| Unsupported property | Controlled rejection occurs before generation. Naive acceptance is followed by runtime failure. |
| Negative armed count | Controlled rejection occurs before execution. Naive acceptance is followed by a count-check failure. |
| Changed seed | Controlled rejection catches the task mismatch. The naive run executes but fails task evaluation. |
| Recovery replay | A stored valid response passes in a new attempt after rejection. |
| 180-agent prompt comparison | Both newly authored initial responses pass after 24 ticks, with 137 humans and 42 zombies. |
| Feedback correction | An injected unsupported property is rejected. A new response authored after reading the feedback removes it and passes with the same 180-agent trajectory. |

The original suite produces 11 evaluation rows. The 180-agent comparison and correction produce four more. The test suite passed all 12 tests. The [evidence index](../evidence/README.md) identifies summaries, intermediate artifacts and recorded provenance.

## 6. Run the demonstrations

Open a terminal in the repository's top-level folder. Use Python 3.10 or later with Tkinter installed. In Windows PowerShell, run the following.

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py run_demos.py --output results/demos
Import-Csv results/demos/validation/summary.csv | Format-Table case,mode,status,promoted
Import-Csv results/demos/session/summary.csv | Format-Table attempt,status,promoted
```

On macOS or Linux, replace `py` with `python3` and open the CSV files with a text editor or spreadsheet application. A PostgreSQL server and graphical display are unnecessary for the headless scenarios. Tkinter and the Python database driver remain import dependencies of the game.

The runner completes successfully when the expected passes and intentional rejections occur. In a report, `status` is the final evaluation and `promoted` records acceptance. A naive report with `promoted=true` and `status=rejected` demonstrates premature acceptance.

| Output within `results/demos/` | Expected outcome |
| --- | --- |
| `validation/small_controlled`, `validation/small_naive` | Both pass and promote. |
| `validation/large_controlled`, `validation/large_naive` | Both pass and promote. |
| Each `validation/unknown_api`, `negative_count` and `changed_requirement` pair | Both eventually reject. Controlled promotion is false and naive promotion is true. |
| `validation/repaired_controlled` | Passes and promotes. |
| `session/naive`, `session/controlled` | Both pass and promote. |
| `session/injected_rejection` | Rejects with promotion false. |
| `session/corrected` | Passes and promotes. |

Inspect a failure, its feedback and a successful history with the following commands.

```powershell
Get-Content results/demos/validation/unknown_api_controlled/report.json
Get-Content results/demos/validation/unknown_api_naive/stderr.txt
Get-Content results/demos/session/injected_rejection/repair_prompt.txt
Get-Content results/demos/session/corrected/simulation.json
```

Use a new output directory for every rerun, such as `results/demos-2`. Each suite saves complete tasks, prompts, ontology snapshots, code, results and provenance. Runtime and library versions are recorded because trajectories may vary across environments.

### Supply a new AI response

```powershell
py -m control_pipeline.pipeline prepare --task control_pipeline/examples/session_task.json --workspace results/my-context
```

Give `results/my-context/prompt_controlled.txt` to an accessible AI model and save its complete JSON response as `results/my-response.json`. Record the model and relevant context. Then run the following.

```powershell
py -m control_pipeline.pipeline run --workspace results/my-context --candidate results/my-response.json --output results/my-attempt
```

Exit code 0 indicates success and exit code 2 indicates rejection. Read the saved feedback prompt when correction is needed. Save the revised response separately and use a new attempt directory. The naive mode is selected with `--mode naive` for comparison. The controller performs deterministic validation and leaves model interaction to the user.

## 7. Prompts, attribution and submission map

The [prompt index](../control_pipeline/prompts/README.md) provides the substantive design and argument specifications and the operational generation and repair templates. Full composed prompts are stored alongside their recorded results. The design and argument specifications were assembled from the assignment for reproduction and review.

The game foundation was imported from [CPS310-Zombie-Game](https://github.com/dokeefe414/CPS310-Zombie-Game) at commit `81464f9`. Its original contributors are Daniel O'Keefe, Owen Bowers and Rahsaun Jeffrey. This individual submission adds the process controls, ontology, prompts and demonstration work with AI assistance under student direction. The response origins and deliberately injected faults are identified in the evidence.

| Assignment requirement | Material |
| --- | --- |
| Explicit pipeline and design | Sections 1–3 and `control_pipeline/pipeline.py` |
| Rigorous argument and naive comparison | Section 4 and both recorded comparison summaries |
| Major prompts | Prompt index, specifications, composed generation prompts and feedback prompts |
| Demos and concrete outcomes | Sections 5–6, `run_demos.py` and generated histories |
| Ontologies and intermediate results on GitHub | `control_pipeline/ontology.json` and the indexed `evidence/` folders |
