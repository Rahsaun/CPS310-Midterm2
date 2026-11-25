"""Generated scenario. Execute with the repository root on the Python import path."""
import json
from control_pipeline.runtime import run_scenario

CONFIGURATION = {'width': 1200, 'height': 1200, 'num_regular': 750, 'num_armed': 50, 'num_zombies': 200, 'ticks': 10, 'seed': 11, 'strategy_mode': 'rush_only'}

if __name__ == "__main__":
    print(json.dumps(run_scenario(**CONFIGURATION), allow_nan=False))
