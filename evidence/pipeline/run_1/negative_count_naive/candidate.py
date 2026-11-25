"""Generated scenario. Execute with the repository root on the Python import path."""
import json
from control_pipeline.runtime import run_scenario

CONFIGURATION = {'width': 400, 'height': 400, 'num_regular': 24, 'num_armed': -2, 'num_zombies': 10, 'ticks': 30, 'seed': 7, 'strategy_mode': 'thompson'}

if __name__ == "__main__":
    print(json.dumps(run_scenario(**CONFIGURATION), allow_nan=False))
