# Ontology-guided process control for AI development of the Zombie Game

**Individual assignment by Rahsaun Jeffrey**

## Problem and scope

This submission designs and implements a process control pipeline for AI-driven development using an explicit ontology. The development task is generating executable simulation scenarios for the existing Zombie Game. An AI response supplies a structured scenario program, which a code generator turns into a Python launcher. The launcher configures and executes the real agent simulation. It includes civilians, armed civilians, zombies, movement, combat, conversion and agent strategy selection.

The scope is intentionally bounded to scenario development. Supported changes include arena dimensions, population composition, tick budget, random seed and strategy selection. The generated Python delegates game behavior to the existing simulation. More general changes to combat algorithms would require additional ontology rules, code-generation support and tests.

The repository began as a copy of [CPS310-Zombie-Game](https://github.com/dokeefe414/CPS310-Zombie-Game), imported at commit `81464f9ed14c10bb87ae3d9d5d011da9ab5e8695`. The original game and forecasting contributions are credited to Daniel O'Keefe, Owen Bowers and Rahsaun Jeffrey. The process control package, report, prompts and new evidence are for Rahsaun's individual assignment. The new pipeline outcomes appear under `evidence/pipeline/run_1/`.

## Ontology and its role

The machine-readable ontology is `control_pipeline/ontology.json`. It represents concepts, typed relations, configurable properties and constraints as a JSON graph. It defines `Agent`, `Human`, `ArmedHuman`, `Zombie`, `SimulationPlayground`, `Scenario` and `Strategy`.

| Relationship or property | Meaning and implementation |
| --- | --- |
| Human is a subclass of Agent | The source binding check verifies this Python inheritance declaration. |
| ArmedHuman is a subclass of Human | Armed civilians count as humans. Runtime checks recognize their inherited type. |
| Zombie is a subclass of Agent | Zombies share agent state but occupy the zombie collection. |
| Zombie converts Human | The game implements conversion. Runtime checks observe collection types and total population. Full conversion behavior is additionally covered by the inherited integration tests. |
| ArmedHuman attacks Zombie | Expresses the game relationship. Existing combat tests and the simulation exercise this behavior. |
| Scenario configures SimulationPlayground | The generated code supplies properties through a fixed adapter to the simulation API. |
| SimulationPlayground uses Strategy | Accepted scenario strategy values are `thompson` and `rush_only`. |

Each configuration property has an owning concept and an allowed type or enumeration. The validator rejects unknown properties. Integers must have the exact integer type, so a Boolean cannot stand in for a count. Cross-property rule R1 caps total initial population at 10,000. R2 requires at least one human. The controls allow nonnegative civilian counts, at least one zombie, arena dimensions from 200 to 2,000 and at most 300 ticks. These are chosen operating bounds for this implementation. Arena bounds leave space for the existing 50-unit spawn margin and scent grid. The population and tick caps bound local demonstration work.

The ontology supplies the vocabulary in the AI context and executable validation rules in the pipeline. Source binding checks compare declared inheritance with the actual game classes. The runtime observer checks collection types, uniqueness, finite state, live health, arena boundaries, requested initial counts, population capacity and tick progression. The ontology's descriptive attack and conversion relations provide context, while the listed checks and regression tests define the validation coverage.

## Overall pipeline design

The pipeline is a sequence of acceptance gates with a feedback loop. The task specifies the requested scenario, the ontology defines valid concepts and relationships, and the AI proposes a structured implementation. The generator converts that proposal into executable Python. The validator controls which proposals reach execution, and the runtime observer controls which executions reach acceptance.

This ordering addresses distinct failure modes. An unsupported field fails the vocabulary gate. A legal value that changes the request fails the intent gate. Generated code must compile, and the resulting simulation must satisfy observable invariants before the controlled workflow accepts it. If a stage fails, its feedback and the original context become a repair prompt. The revised response enters validation as a new attempt.

The implementation separates responsibilities across four components. `ontology.json` defines the domain contract. `pipeline.py` prepares prompts, checks responses, generates code and manages acceptance. `runtime.py` connects generated scenarios to the existing game and checks live state. `demo.py` compares controlled and baseline acceptance using the same candidate responses. The evidence directory links each outcome to the exact inputs and stages that produced it.

The nine steps below include the human interaction with the AI model. Preparation and validation are executable commands. Supplying the prompt to a model and saving its response is a manual step. The demo command replays saved responses through the executable stages.

## Pipeline design and every stage

| Step | Action | Output and control |
| --- | --- | --- |
| 1. State requirements | Save a task identifier, a goal and exact requested configuration values. Validate the task against the ontology. | `task.json` and a valid starting contract. Free text explains the task and structured fields determine acceptance. |
| 2. Bind context | Check ontology inheritance against source and hash the game, runtime, generator, prompts and ontology. | `ontology.json` and `source_hashes.json` in a fresh workspace. |
| 3. Construct AI prompts | Combine the controlled instructions with the task and complete ontology. Also produce the comparison prompt. | `prompt_controlled.txt` and `prompt_naive.txt`. |
| 4. Obtain AI output | Give the saved prompt to an accessible AI model and save its complete JSON response as a separate file. Record model/workflow provenance. | Candidate response. The included examples were authored by the ChatGPT assistant during this development session. |
| 5. Validate the candidate | Reject malformed JSON, duplicate keys, unknown properties, incorrect types, constraint violations, ontology-version mismatches and changes to requested values. Recheck source/context hashes. | Validation receipt or rejection feedback. |
| 6. Generate Python | Render the validated specification into a Python launcher using a fixed template. Parse and compile the generated code. | `candidate.py`. Values are serialized as Python literals, which keeps response strings within data values. |
| 7. Execute and observe | Run the candidate in a child Python process against the real simulation with a 120-second timeout. Check state invariants and capture outputs. | `stdout.txt`, `stderr.txt` and, on success, `simulation.json`. |
| 8. Accept or repair | Accept only after compilation, execution and task evaluation pass. Write `accepted.py` through an atomic file replacement. A rejected response produces a repair prompt containing the task, ontology and feedback. | Accepted artifact or `repair_prompt.txt`. Each repair attempt uses a new output directory. |
| 9. Preserve evidence | Record candidate hashes, source hashes, stage completion, errors, exact prompts and population histories. | `report.json`, response snapshots and comparison evidence committed to GitHub. |

AI interaction is a manual step so that a free accessible model can be used without an API subscription. The executable controls run locally. A user can save a new model response and rerun the acceptance stages. The pipeline generates a repair prompt after a failure. Its demo replays a valid response to exercise recovery. It does not automatically call a model to repair candidates.

Fresh workspace and attempt directories prevent accidental overwrites of earlier evidence. Each invocation uses an isolated child process with fixed Python and NumPy seeds. The adapter uses one simulation worker, which avoids introducing multiprocessing variability into this development-control comparison. Accepted artifacts stay in the attempt directory and can be reviewed or copied into a normal development branch. This pipeline does not automatically merge repository changes.

## Comparison and argument

The comparison approach gives the model the task and the required response format. Its acceptance policy generates Python and accepts it as soon as it compiles. The experiment then executes that artifact and applies the same observer and task evaluator to measure its correctness. A report with `promoted=true` and `status=rejected` records that the baseline accepted an artifact that later failed evaluation.

The replay comparison supplies the same candidate to both policies. This isolates the effect of the acceptance controls. The saved prompts allow fresh AI trials later. The present comparison uses two session-authored valid responses and three deliberate mutations of a valid response. It measures behavior on those examples and faults. Model error frequency would require independently sampled responses across more tasks and models.

| Aspect controlled | Why the control is effective | Baseline comparison and limit |
| --- | --- | --- |
| Vocabulary and API compatibility | A closed field set rejects a property the adapter cannot use. | A Python launcher can compile even though an unsupported keyword causes an error when called. Coverage extends to the supported adapter interface. |
| Population validity | Typed bounds and cross-field rules reject negative counts and invalid totals before execution. | Python accepts a negative integer literal, and `range(-2)` creates zero armed civilians. A later observer catches the count mismatch. |
| Requirement fidelity | Exact comparison with the task catches legal values that change the requested experiment. | A seed changed from 7 to 99 still compiles and runs. Its resulting trajectory differs from the requested one. Structured task values must themselves express the user's intent correctly. |
| Behavior and integration | Runtime invariants require initial counts, valid live state and correct tick progression. Simulation tests check combat, conversion and strategy behavior. | Compilation alone establishes syntax. Runtime checks cover the executed traces, while unexercised behaviors remain possible failure points. |
| Reproducibility and traceability | Saved prompts, inputs, source hashes, seeds and stage receipts connect outputs to their generating context. | A source change after prompt preparation triggers a new context requirement. Hashes detect drift but are not an authentication or security boundary. |
| Acceptance and recovery | Controlled promotion follows successful execution. Rejections retain feedback for a new attempt. | The baseline promotes three failing examples. Atomic artifact writing prevents partial acceptance files, while each retry preserves earlier evidence. |

These controls improve reliability for the stated scenario-development task because they make vocabulary, intent and behavior explicit conditions of acceptance. Their effect depends on ontology quality and test coverage. A valid scenario can still contain undesirable game dynamics. Approval should also consider whether the task and operating bounds match the intended experiment.

### Concrete arguments supported by the demos

**Argument 1. Ontology validation prevents incompatible scenario code from being accepted.** The injected `infection_rate` field falls outside the ontology's property vocabulary and the adapter's supported arguments. The controlled run rejects it before Python generation and records `promoted=false`. The baseline renders and compiles its launcher, records `promoted=true`, then encounters an unexpected-keyword error during execution. This shows why a successful compilation check alone permits an API incompatibility in this task. The supporting files are `evidence/pipeline/run_1/unknown_api_controlled/report.json`, `unknown_api_naive/report.json` and `unknown_api_naive/stderr.txt`.

**Argument 2. Domain constraints prevent silent changes in population composition.** A negative armed count is valid Python syntax, but the simulation's population loop creates zero armed civilians for that count. The ontology rejects the value before execution. The baseline accepts the launcher and subsequently fails its initial armed-count assertion. The control is effective because the required domain meaning is checked before the language runtime interprets the value. The supporting files are the `negative_count_controlled` and `negative_count_naive` reports and the latter's error log.

**Argument 3. Task comparison protects reproducibility even when a scenario runs successfully.** Seed 99 is a valid domain value, yet the request specified seed 7. The controlled pipeline rejects the mismatch. The baseline runs to completion with 30 humans and 8 zombies at tick 30, compared with 28 humans and 12 zombies for the requested seed. The task evaluator then records a failure. The task-equality gate therefore covers an error that syntax and state invariants permit. The supporting files are `small_context/task.json`, both `changed_requirement` reports and the corresponding simulation histories.

**Argument 4. Acceptance gates allow valid work and support correction.** Both workflows pass the 40-agent and 1,000-agent scenarios. The controlled workflow also accepts a valid response replayed after rejection in a separate attempt directory. These outcomes demonstrate successful integration and recovery within the supported task. The repair example exercises the pipeline using a stored valid response. Its evidence establishes recovery behavior, while evaluating AI repair quality would require new model responses.

Across the three chosen faults, controlled acceptance produced zero premature promotions and baseline acceptance produced three. This is a concrete comparison of acceptance policies on specified inputs. The responses are replayed, and the faults are deliberately injected. Independent model-generation trials would be needed to estimate error frequency, productivity or performance across models.

## Demonstrations and concrete outcomes

The committed run is `evidence/pipeline/run_1/`. Exact controlled, comparison and repair prompts, ontology copies, generated Python, stage receipts and simulation histories are included. Run-level provenance identifies the current-session assistant responses and distinguishes deliberate fault injection from naturally observed AI mistakes.

| Demo | Controlled result | Baseline result and observed outcome |
| --- | --- | --- |
| Mixed-agent scenario | Accepted after the actual game completed 30 ticks with 40 initial agents. Final counts were 28 humans and 12 zombies. | Accepted and passed evaluation. Its trajectory matched the controlled run. |
| Larger scenario | Accepted after 10 ticks with 1,000 initial agents. Final counts were 795 humans and 205 zombies. | Accepted and passed evaluation with the same trajectory. This demonstrates integration at this scale over a short run. |
| Injected unknown `infection_rate` property | Rejected before Python generation. | Accepted after compilation, then failed with an unexpected-keyword error. |
| Injected armed count of -2 | Rejected for an invalid count and a requirement mismatch. | Accepted after compilation, then failed the initial armed-count check. |
| Injected seed change to 99 | Rejected for changing a requested value. | Accepted and executed, ending with 30 humans and 8 zombies, then failed task evaluation. |
| Recovery after rejection | A valid saved response was replayed as a separate attempt and accepted. | Demonstrates that a rejected attempt does not prevent a later valid attempt from succeeding. |

In the three deliberately faulty cases, the controlled policy promoted zero artifacts and the compilation-only policy promoted all three. These counts describe the chosen faults. They provide no estimate of how frequently an AI model would produce such errors. The two valid examples passed both policies, showing that the controls also permit supported changes.

The observed test run passed all 12 tests, including eight tests of the pipeline. The log is `evidence/pipeline/tests.txt`. Unit tests include context mutation, duplicate JSON keys, source-bound inheritance, unsupported fields, type and rule failures, deterministic execution, failed-runtime acceptance prevention and safe retry behavior. GUI interaction and database writes are outside these headless demos.

## Reproduction and independent use

Use Python 3.10 or later with Tkinter available. Install the dependency file and run the tests from the repository root.

```powershell
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py -m control_pipeline.demo --output results/pipeline-demo
```

The output path must be new. To repeat a demonstration, choose another path such as `results/pipeline-demo-2`. The `results/` directory is ignored by Git, so select evidence intended for submission before committing it. The committed example evidence is under `evidence/`.

### Run every demo and inspect the results

Download or clone `Rahsaun/CPS310-Midterm2` and open a terminal in its top-level folder, where `requirements.txt` is located. The repository is private, so use your authorized GitHub account. On Windows, run the following in PowerShell.

```powershell
cd path/to/CPS310-Midterm2
py --version
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py -m control_pipeline.demo --output results/pipeline-demo
Import-Csv results/pipeline-demo/summary.csv | Format-Table case,mode,status,promoted
```

Replace `path/to/CPS310-Midterm2` with the actual folder location. Python 3.10 or later and Tkinter are required. On macOS or Linux, use `python3` in place of `py`. Open the resulting CSV with a text editor or spreadsheet application to inspect the summary.

The single demo command runs all six demonstrations and writes 11 comparison rows. Every output path is relative to `results/pipeline-demo/`.

| Demonstration | Output directories | Expected result |
| --- | --- | --- |
| 40-agent scenario | `small_controlled`, `small_naive` | Both pass and promote. |
| 1,000-agent scenario | `large_controlled`, `large_naive` | Both pass and promote. |
| Unsupported property | `unknown_api_controlled`, `unknown_api_naive` | Both eventually reject. Controlled promotion is false and baseline promotion is true. |
| Negative armed count | `negative_count_controlled`, `negative_count_naive` | Both eventually reject. Controlled promotion is false and baseline promotion is true. |
| Changed requested seed | `changed_requirement_controlled`, `changed_requirement_naive` | Both eventually reject. Controlled promotion is false and baseline promotion is true. |
| Recovery attempt | `repaired_controlled` | Passes and promotes. |

The demo command exits successfully when these expected outcomes occur, including the intended rejections. In a report, `status` records the final evaluation and `promoted` records whether the workflow accepted the artifact. Baseline `promoted=true` with `status=rejected` means it accepted the artifact before later evaluation exposed the failure.

Use these PowerShell commands to inspect a rejection and its repair instructions.

```powershell
Get-Content results/pipeline-demo/unknown_api_controlled/report.json
Get-Content results/pipeline-demo/unknown_api_naive/stderr.txt
Get-Content results/pipeline-demo/unknown_api_controlled/repair_prompt.txt
Get-Content results/pipeline-demo/small_controlled/simulation.json
```

The demos run in the terminal and save population histories to JSON. To repeat all demos, choose a fresh output path.

```powershell
py -m control_pipeline.demo --output results/pipeline-demo-2
```

To rerun one acceptance check after the complete demonstration, use a new attempt directory. This example replays the unsupported-field case.

```powershell
py -m control_pipeline.pipeline run --workspace results/pipeline-demo/small_context --candidate results/pipeline-demo/unknown_api_response.json --output results/unknown-api-recheck --mode controlled
```

An individual rejected attempt returns exit code 2 and saves feedback. The accepted small scenario can be executed again with the repository root on Python's import path.

```powershell
py -c "import runpy; runpy.run_path('results/pipeline-demo/small_controlled/accepted.py', run_name='__main__')"
```

### Create a fresh AI response

For a new AI-assisted development attempt, create a task JSON following the examples, prepare the context, give the controlled prompt to a model, save its response and run validation.

```powershell
py -m control_pipeline.pipeline prepare --task control_pipeline/examples/small_task.json --workspace results/my-context
# Give results/my-context/prompt_controlled.txt to a model and save its JSON response as results/my-response.json.
py -m control_pipeline.pipeline run --workspace results/my-context --candidate results/my-response.json --output results/my-attempt
# Exit code 0 indicates success. Exit code 2 indicates rejection. Read report.json and repair_prompt.txt.
# Use a fresh attempt path when testing the revised response.
```

To execute an accepted launcher again, provide the repository root on Python's import path using this command from the repository root.

```powershell
py -c "import runpy; runpy.run_path('results/my-attempt/accepted.py', run_name='__main__')"
```

The runtime seeds global random generators within its child process. Python and NumPy versions should be recorded when comparing runs. Reproduction may vary across library/platform versions. PostgreSQL and a graphical display are unnecessary for these scenario runs, although the inherited module imports require Tkinter and psycopg2 to be installed.

## Submission mapping

| Assignment requirement | Submitted material |
| --- | --- |
| Explicit pipeline steps and design | This report and `control_pipeline/pipeline.py`. |
| Ontology used in AI-driven development | `control_pipeline/ontology.json`, source binding checks and saved controlled prompts. |
| Rigorous argument and comparison | Comparison section, `control_pipeline/demo.py` and `evidence/pipeline/run_1/summary.csv`. |
| All major workflow prompts | Templates under `control_pipeline/prompts/`, full prompts in the committed contexts and generated repair prompts. |
| Demos with concrete outcomes | Generated launchers, simulation histories, receipts and demonstration summary. |
| Intermediate results and ontologies on GitHub | Complete selected evidence under `evidence/pipeline/run_1/`, including context snapshots and response provenance. |
