import subprocess
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RalphLoop')

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))

def create_state_file(task_id: str, prompt: str) -> Path:
    plans_dir = VAULT_PATH / 'Plans'
    plans_dir.mkdir(parents=True, exist_ok=True)
    state_file = plans_dir / f'RALPH_{task_id}.md'
    state_file.write_text(f'''---
task_id: {task_id}
created: {datetime.now().isoformat()}
status: in_progress
iteration: 0
max_iterations: {MAX_ITERATIONS}
---

# Ralph Loop Task: {task_id}

## Prompt
{prompt}

## Progress Log
''')
    return state_file

def update_state_file(state_file: Path, iteration: int, output: str):
    content = state_file.read_text()
    content = content.replace(f'iteration: {iteration - 1}', f'iteration: {iteration}')
    content += f'\n### Iteration {iteration} — {datetime.now().isoformat()}\n{output[:500]}\n'
    state_file.write_text(content)

def run_ralph_loop(prompt: str, task_id: str = None, completion_promise: str = 'TASK_COMPLETE'):
    if not task_id:
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    state_file = create_state_file(task_id, prompt)
    logger.info(f'Starting Ralph Loop — Task: {task_id}, Max iterations: {MAX_ITERATIONS}')

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f'Iteration {iteration}/{MAX_ITERATIONS}')

        full_prompt = f'''{prompt}

Current iteration: {iteration}/{MAX_ITERATIONS}
State file: {state_file}

When you have completed ALL steps, output exactly: <promise>{completion_promise}</promise>
If you still have work remaining, output: <promise>TASK_INCOMPLETE</promise>
If you are blocked and need human input, output: <promise>AWAITING_APPROVAL</promise>'''

        result = subprocess.run(
            ['claude', '-p', full_prompt, '--cwd', str(VAULT_PATH)],
            capture_output=True, text=True
        )
        output = result.stdout + result.stderr
        update_state_file(state_file, iteration, output)

        if f'<promise>{completion_promise}</promise>' in output:
            logger.info(f'Task {task_id} COMPLETED in {iteration} iterations')
            content = state_file.read_text().replace('status: in_progress', 'status: completed')
            state_file.write_text(content)
            done_path = VAULT_PATH / 'Done' / state_file.name
            state_file.rename(done_path)
            return True

        if '<promise>AWAITING_APPROVAL</promise>' in output:
            logger.info(f'Task {task_id} is BLOCKED — waiting for human approval')
            content = state_file.read_text().replace('status: in_progress', 'status: awaiting_approval')
            state_file.write_text(content)
            return False

        if iteration < MAX_ITERATIONS:
            logger.info(f'Task incomplete, retrying in 5 seconds...')
            time.sleep(5)

    logger.warning(f'Task {task_id} reached MAX ITERATIONS ({MAX_ITERATIONS}) without completion')
    content = state_file.read_text().replace('status: in_progress', 'status: max_iterations_reached')
    state_file.write_text(content)
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python ralph_loop.py "Your task prompt here"')
        sys.exit(1)
    prompt = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    success = run_ralph_loop(prompt, task_id)
    sys.exit(0 if success else 1)
