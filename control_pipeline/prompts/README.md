# Major prompts

These files provide the substantive instructions for reviewing and reproducing the work.

| Stage | Prompt |
| --- | --- |
| Design and written argument | [Design and argument specifications](DESIGN_AND_ARGUMENT.md) |
| Controlled scenario generation | [Controlled prompt](controlled.txt) |
| Naive scenario generation | [Naive prompt](naive.txt) |
| Correct a rejected response | [Repair prompt](repair.txt) |

The executable pipeline adds the task and ontology to these templates. Complete composed prompts are saved in the [original contexts](../../evidence/pipeline/run_1/) and [180-agent context](../../evidence/pipeline/session_2/context/). The [correction prompt](../../evidence/pipeline/session_2/injected_rejection/repair_prompt.txt) includes the actual validation feedback.

The design and argument specifications summarize the assignment's substantive requirements for reproducibility. They are reusable specifications assembled from the assignment. The operational composed prompts correspond to the recorded scenario responses and correction example.
