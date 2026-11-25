"""Generated scenario. Execute with the repository root on the Python import path."""
import json
from control_pipeline.runtime import run_scenario

CONFIGURATION = {'width': 500, 'height': 500, 'num_regular': 120, 'num_armed': 20, 'num_zombies': 40, 'ticks': 24, 'seed': 23, 'strategy_mode': 'thompson'}

if __name__ == "__main__":
    print(json.dumps(run_scenario(**CONFIGURATION), allow_nan=False))
