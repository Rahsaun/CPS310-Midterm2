"""Prepare AI context, validate responses, generate and test Python, and publish artifacts.

Commands are available through python -m control_pipeline.pipeline --help.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "control_pipeline"


def read_json(path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    paths = [ROOT / name for name in ("Zombie_Game.py", "models.py", "forecasting.py", "db_manager.py")]
    paths += sorted(PACKAGE.glob("*.py"))
    paths += sorted((PACKAGE / "prompts").glob("*.txt"))
    paths += [PACKAGE / "ontology.json"]
    return {str(path.relative_to(ROOT)): digest(path) for path in paths}


def validate_ontology_bindings(ontology):
    """Check declared class inheritance against the actual Python source."""
    module = ast.parse((ROOT / "Zombie_Game.py").read_text(encoding="utf-8"))
    classes = {node.name: node for node in module.body if isinstance(node, ast.ClassDef)}
    for relation in ontology["relations"]:
        if relation["predicate"] == "subclass_of":
            child, parent = relation["subject"], relation["object"]
            if child not in classes or parent not in classes:
                raise ValueError(f"ontology class missing from game: {child} or {parent}")
            parents = {base.id for base in classes[child].bases if isinstance(base, ast.Name)}
            if parent not in parents:
                raise ValueError(f"ontology inheritance disagrees with game: {child} -> {parent}")
    for name, field in ontology["fields"].items():
        if field["concept"] not in ontology["concepts"]:
            raise ValueError(f"unknown field concept: {name}")


def validate_configuration(configuration, ontology):
    errors = []
    if not isinstance(configuration, dict):
        return ["configuration must be an object"]
    fields = ontology["fields"]
    if configuration.keys() != fields.keys():
        errors.append(f"fields mismatch; missing={sorted(fields.keys() - configuration.keys())}, unknown={sorted(configuration.keys() - fields.keys())}")
    for name, value in configuration.items():
        if name not in fields:
            continue
        spec = fields[name]
        if spec["type"] == "integer":
            if type(value) is not int:
                errors.append(f"{name} requires an integer")
            elif not spec["min"] <= value <= spec["max"]:
                errors.append(f"{name} outside [{spec['min']}, {spec['max']}]")
        elif type(value) is not str or value not in spec["enum"]:
            errors.append(f"{name} must be one of {spec['enum']}")
    for rule in ontology["rules"]:
        values = [configuration.get(name) for name in rule["fields"]]
        if all(type(value) is int for value in values):
            total = sum(values)
            if rule["kind"] == "population_limit" and total > rule["max"]:
                errors.append(f"{rule['id']}: population exceeds {rule['max']}")
            if rule["kind"] == "minimum_humans" and total < rule["min"]:
                errors.append(f"{rule['id']}: scenario needs at least one human")
    return errors


def validate_candidate(candidate, task, ontology):
    if not isinstance(candidate, dict):
        return ["response must be an object"]
    errors = validate_configuration(candidate.get("configuration"), ontology)
    if set(candidate) != {"task_id", "ontology_version", "configuration"}:
        errors.append("response fields must be task_id, ontology_version, configuration")
    if candidate.get("task_id") != task["task_id"]:
        errors.append("task_id mismatch")
    if candidate.get("ontology_version") != ontology["version"]:
        errors.append("ontology_version mismatch")
    if candidate.get("configuration") != task["configuration"]:
        errors.append("configuration differs from requested values")
    return errors


def render(configuration):
    # repr produces Python literals. Model text is never interpolated as Python statements.
    return ('"""Generated scenario. Execute with the repository root on the Python import path."""\n'
            'import json\nfrom control_pipeline.runtime import run_scenario\n\n'
            f'CONFIGURATION = {configuration!r}\n\n'
            'if __name__ == "__main__":\n'
            '    print(json.dumps(run_scenario(**CONFIGURATION), allow_nan=False))\n')


def prepare(task_path, workspace):
    task = read_json(task_path)
    ontology = read_json(PACKAGE / "ontology.json")
    validate_ontology_bindings(ontology)
    errors = validate_configuration(task.get("configuration"), ontology)
    if set(task) != {"task_id", "goal", "configuration"} or not isinstance(task.get("task_id"), str) or not isinstance(task.get("goal"), str):
        errors.append("task requires string task_id, string goal and configuration")
    if errors:
        raise ValueError("; ".join(errors))
    workspace.mkdir(parents=True, exist_ok=False)
    write_json(workspace / "task.json", task)
    write_json(workspace / "ontology.json", ontology)
    write_json(workspace / "source_hashes.json", source_hashes())
    for mode in ("controlled", "naive"):
        prompt = (PACKAGE / "prompts" / f"{mode}.txt").read_text()
        prompt += "\nTASK\n" + json.dumps(task, indent=2)
        if mode == "controlled":
            prompt += "\nONTOLOGY\n" + json.dumps(ontology, indent=2)
        (workspace / f"prompt_{mode}.txt").write_text(prompt + "\n", encoding="utf-8")


def run(workspace, candidate_path, output, mode):
    # Each attempt gets a new directory. Failed/repeated attempts cannot overwrite prior evidence.
    output.mkdir(parents=True, exist_ok=False)
    report = {"mode": mode, "status": "rejected", "promoted": False, "stages": [], "errors": []}
    try:
        task = read_json(workspace / "task.json")
        ontology = read_json(workspace / "ontology.json")
        candidate = read_json(candidate_path)
        write_json(output / "response.json", candidate)
        report["response_sha256"] = digest(candidate_path)
        report["ontology_sha256"] = digest(workspace / "ontology.json")
        report["source_hashes"] = source_hashes()
        if read_json(workspace / "source_hashes.json") != source_hashes():
            raise ValueError("source or control files changed since context preparation; prepare a new workspace")
        if ontology != read_json(PACKAGE / "ontology.json"):
            raise ValueError("workspace ontology differs from the prepared source ontology")
        validate_ontology_bindings(ontology)
        report["stages"].append("context_verified")
        if mode == "controlled":
            errors = validate_candidate(candidate, task, ontology)
            if errors:
                raise ValueError("; ".join(errors))
            report["stages"].append("ontology_and_intent_validated")
        code = render(candidate["configuration"])
        (output / "candidate.py").write_text(code, encoding="utf-8")
        ast.parse(code)
        compile(code, str(output / "candidate.py"), "exec")
        report["stages"].append("python_compiled")
        # Naive development accepts generated code once it compiles. Runtime checks are
        # then an external observer, allowing the comparison to expose premature acceptance.
        if mode == "naive":
            (output / "accepted.py").write_text(code, encoding="utf-8")
            report["promoted"] = True
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT)
        process = subprocess.run([sys.executable, str(output / "candidate.py")],
                                 cwd=ROOT, env=environment, capture_output=True, text=True, timeout=120)
        (output / "stdout.txt").write_text(process.stdout, encoding="utf-8")
        (output / "stderr.txt").write_text(process.stderr, encoding="utf-8")
        if process.returncode:
            raise ValueError(f"runtime failed with exit code {process.returncode}; see stderr.txt")
        result = json.loads(process.stdout)
        write_json(output / "simulation.json", result)
        report["stages"].append("runtime_invariants_passed")
        # An independent task check also measures whether a naive output met the request.
        intent_errors = validate_candidate(candidate, task, ontology)
        if intent_errors:
            raise ValueError("task evaluation: " + "; ".join(intent_errors))
        if mode == "controlled":
            with tempfile.NamedTemporaryFile(mode="w", dir=output, encoding="utf-8", delete=False) as stream:
                stream.write(code)
                temporary = stream.name
            os.replace(temporary, output / "accepted.py")
            report["promoted"] = True
        report["stages"].append("accepted")
        report["status"] = "passed"
    except (ValueError, TypeError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        report["errors"].append(str(error))
    write_json(output / "report.json", report)
    if report["errors"]:
        feedback = {"errors": report["errors"], "task": read_json(workspace / "task.json"),
                    "ontology": read_json(workspace / "ontology.json")}
        prompt = (PACKAGE / "prompts/repair.txt").read_text() + "\n" + json.dumps(feedback, indent=2)
        (output / "repair_prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("prepare")
    setup.add_argument("--task", type=Path, required=True)
    setup.add_argument("--workspace", type=Path, required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--workspace", type=Path, required=True)
    execute.add_argument("--candidate", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    execute.add_argument("--mode", choices=("controlled", "naive"), default="controlled")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.task, args.workspace)
    else:
        report = run(args.workspace, args.candidate, args.output, args.mode)
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "passed" else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
