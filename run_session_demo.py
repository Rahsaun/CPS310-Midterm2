"""Replay the fresh session's controlled, naive and correction responses.

python run_session_demo.py --output results/session-demo
"""
import argparse
import copy
import csv
from pathlib import Path
import platform
import sys

import numpy as np

from control_pipeline.pipeline import digest, prepare, read_json, run, source_hashes, write_json

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / 'control_pipeline/examples'


def demonstrate(output):
    output.mkdir(parents=True, exist_ok=False)
    context = output / 'context'
    prepare(EXAMPLES / 'session_task.json', context)
    rows = []
    for mode in ('naive', 'controlled'):
        response = EXAMPLES / f'session_{mode}_response.json'
        report = run(context, response, output / mode, mode)
        rows.append({'attempt': mode, 'source': 'new_session_response',
                     'status': report['status'], 'promoted': report['promoted']})
    faulty = copy.deepcopy(read_json(EXAMPLES / 'session_controlled_response.json'))
    faulty['configuration']['infection_rate'] = 0.5
    faulty_path = output / 'injected_response.json'
    write_json(faulty_path, faulty)
    rejected = run(context, faulty_path, output / 'injected_rejection', 'controlled')
    rows.append({'attempt': 'injected_rejection', 'source': 'deliberate_fault_injection',
                 'status': rejected['status'], 'promoted': rejected['promoted']})
    corrected = run(context, EXAMPLES / 'session_repair_response.json', output / 'corrected', 'controlled')
    rows.append({'attempt': 'corrected', 'source': 'new_response_to_saved_feedback',
                 'status': corrected['status'], 'promoted': corrected['promoted']})
    with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(output / 'provenance.json', {
        'response_author': 'ChatGPT assistant in the ongoing user conversation',
        'response_capture': 'New complete JSON responses were authored after reading the saved task prompts in this conversation. The correction was authored after reading the generated rejection feedback.',
        'shared_context': 'The same assistant saw both prompts and already knew the implementation and ontology. These responses are not independently sampled model trials.',
        'same_output': 'Both initial responses specify the same valid configuration. Matching content is expected for an exact-value task.',
        'fault_origin': 'infection_rate=0.5 was deliberately added to the controlled response to exercise the repair path.',
        'reproduction': 'This script replays saved model outputs. New model output requires manually supplying the saved prompt to a model and recording its response.',
        'prompt_generation': 'context/prompt_naive.txt and context/prompt_controlled.txt are exact composed prompts. injected_rejection/repair_prompt.txt is the composed feedback prompt.',
        'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform(),
        'source_hashes': source_hashes(), 'reproduction_script_sha256': digest(Path(__file__)),
        'response_sha256': {path.name: digest(path) for path in EXAMPLES.glob('session_*_response.json')}
    })
    for row in rows:
        print(f"{row['attempt']:20} {row['status']:8} promoted={row['promoted']}")
    expected = ['passed', 'passed', 'rejected', 'passed']
    if [row['status'] for row in rows] != expected or rejected['promoted']:
        raise RuntimeError('Unexpected demo outcome; inspect the saved reports.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    demonstrate(args.output)


if __name__ == '__main__':
    main()
