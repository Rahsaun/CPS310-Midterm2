"""Reproduce scenario development and fault-injection comparisons.

python -m control_pipeline.demo --output results/pipeline-demo
"""
import argparse
import copy
import csv
import json
from pathlib import Path
import platform
import sys

import numpy as np

from control_pipeline.pipeline import PACKAGE, prepare, read_json, run, source_hashes, write_json


def demonstrate(output):
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for size in ("small", "large"):
        workspace = output / f"{size}_context"
        prepare(PACKAGE / "examples" / f"{size}_task.json", workspace)
        candidate = PACKAGE / "examples" / f"{size}_response.json"
        for mode in ("controlled", "naive"):
            report = run(workspace, candidate, output / f"{size}_{mode}", mode)
            rows.append({"case": size, "provenance": "session_assistant_response_replay",
                         "mode": mode, "status": report["status"], "promoted": report["promoted"],
                         "error": " | ".join(report["errors"])})
    baseline = read_json(PACKAGE / "examples/small_response.json")
    faults = {"unknown_api": ("infection_rate", 0.5), "negative_count": ("num_armed", -2),
              "changed_requirement": ("seed", 99)}
    for name, (field, value) in faults.items():
        candidate = copy.deepcopy(baseline)
        candidate["configuration"][field] = value
        path = output / f"{name}_response.json"
        write_json(path, candidate)
        for mode in ("controlled", "naive"):
            report = run(output / "small_context", path, output / f"{name}_{mode}", mode)
            rows.append({"case": name, "provenance": "deliberate_fault_injection",
                         "mode": mode, "status": report["status"], "promoted": report["promoted"],
                         "error": " | ".join(report["errors"])})
    repair = run(output / "small_context", PACKAGE / "examples/small_response.json",
                 output / "repaired_controlled", "controlled")
    rows.append({"case": "repair", "provenance": "replay_valid_response_after_rejection",
                 "mode": "controlled", "status": repair["status"], "promoted": repair["promoted"],
                 "error": " | ".join(repair["errors"])})
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(output / "provenance.json", {
        "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
        "source_hashes": source_hashes(),
        "model_response_origin": "ChatGPT assistant authored the two example JSON responses in the current development session; no separate model API calls were made.",
        "experiment": "Replay the same response through both acceptance policies to isolate the effect of controls. Faults are deliberately injected, rather than claimed as observed model mistakes.",
        "repair": "A valid stored response is replayed after rejection to demonstrate recovery. This is not an independent AI repair trial.",
        "model_sampling": "These examples do not estimate model failure rates or compare independently sampled AI responses."
    })
    for row in rows:
        print(f"{row['case']:22} {row['mode']:10} {row['status']:8} promoted={row['promoted']}")
    expected = all(row["status"] == "passed" for row in rows if row["case"] in {"small", "large", "repair"})
    expected &= all(row["status"] == "rejected" for row in rows if row["provenance"] == "deliberate_fault_injection")
    expected &= all(not row["promoted"] for row in rows if row["mode"] == "controlled" and row["status"] == "rejected")
    if not expected:
        raise RuntimeError("demonstration outcome differs from expectations; inspect reports")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    demonstrate(args.output)


if __name__ == "__main__":
    main()
