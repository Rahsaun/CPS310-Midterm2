"""Regression checks for the process controls and actual game integration."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from control_pipeline.pipeline import (PACKAGE, prepare, read_json, run,
                                       validate_candidate, validate_ontology_bindings, write_json)

CONFIG = {"width": 400, "height": 400, "num_regular": 24, "num_armed": 6,
          "num_zombies": 10, "ticks": 12, "seed": 7, "strategy_mode": "thompson"}


class ControlPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.task = {"task_id": "test", "goal": "Run a reproducible mixed-agent scenario", "configuration": CONFIG}
        self.candidate = {"task_id": "test", "ontology_version": "1.0", "configuration": dict(CONFIG)}
        self.ontology = read_json(PACKAGE / "ontology.json")
        write_json(self.root / "task.json", self.task)
        self.workspace = self.root / "workspace"
        prepare(self.root / "task.json", self.workspace)

    def execute(self, mode="controlled"):
        write_json(self.root / "response.json", self.candidate)
        return run(self.workspace, self.root / "response.json", self.root / mode, mode)

    def test_valid_scenario_runs_real_game_and_is_reproducible(self):
        self.assertEqual(self.execute()["status"], "passed")
        self.assertEqual(self.execute("naive")["status"], "passed")
        first = read_json(self.root / "controlled/simulation.json")
        second = read_json(self.root / "naive/simulation.json")
        self.assertEqual(first, second)
        self.assertEqual(first["ticks_completed"], 12)
        self.assertTrue((self.root / "controlled/accepted.py").exists())

    def test_unknown_api_field_is_rejected_before_acceptance(self):
        self.candidate["configuration"]["infection_rate"] = 0.5
        report = self.execute()
        self.assertFalse(report["promoted"])
        self.assertIn("unknown=['infection_rate']", report["errors"][0])
        self.assertTrue((self.root / "controlled/repair_prompt.txt").exists())

    def test_naive_accepts_compiling_code_that_fails_at_runtime(self):
        self.candidate["configuration"]["infection_rate"] = 0.5
        report = self.execute("naive")
        self.assertTrue(report["promoted"])
        self.assertEqual(report["status"], "rejected")
        self.assertIn("unexpected keyword argument", (self.root / "naive/stderr.txt").read_text())

    def test_types_relationship_limits_and_intent_are_enforced(self):
        for field, value in [("num_armed", -1), ("ticks", True), ("width", 10),
                             ("num_zombies", 10000), ("strategy_mode", "swarm"), ("seed", 8)]:
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.candidate)
                candidate["configuration"][field] = value
                self.assertTrue(validate_candidate(candidate, self.task, self.ontology))
        candidate = copy.deepcopy(self.candidate)
        candidate["configuration"]["num_regular"] = 0
        candidate["configuration"]["num_armed"] = 0
        self.assertTrue(any("R2" in error for error in validate_candidate(candidate, self.task, self.ontology)))

    def test_runtime_failure_cannot_promote_controlled_artifact(self):
        with patch("control_pipeline.pipeline.subprocess.run", side_effect=OSError("test execution failure")):
            report = self.execute()
        self.assertFalse(report["promoted"])
        self.assertFalse((self.root / "controlled/accepted.py").exists())

    def test_ontology_inheritance_is_bound_to_game_source(self):
        validate_ontology_bindings(self.ontology)
        altered = copy.deepcopy(self.ontology)
        altered["relations"][0]["object"] = "Zombie"
        with self.assertRaises(ValueError):
            validate_ontology_bindings(altered)

    def test_mutated_context_and_duplicate_keys_fail_closed(self):
        with self.assertRaises(ValueError):
            (self.root / "duplicate.json").write_text('{"x": 1, "x": 2}')
            read_json(self.root / "duplicate.json")
        ontology = read_json(self.workspace / "ontology.json")
        ontology["version"] = "edited"
        write_json(self.workspace / "ontology.json", ontology)
        self.assertFalse(self.execute()["promoted"])

    def test_retries_require_separate_attempt_directories(self):
        self.execute()
        with self.assertRaises(FileExistsError):
            self.execute()


if __name__ == "__main__":
    unittest.main()
