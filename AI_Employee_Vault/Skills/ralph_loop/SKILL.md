# Skill: Ralph Wiggum Loop

## Purpose
Keep Claude working autonomously on a multi-step task until it is
fully complete or max iterations reached.

## How It Works
1. Orchestrator creates a state file: /Plans/RALPH_<task_id>.md
2. Claude processes the task
3. If task is not complete, Claude outputs: <promise>TASK_INCOMPLETE</promise>
4. Stop hook re-injects the prompt with updated context
5. If task is complete, Claude outputs: <promise>TASK_COMPLETE</promise>
6. Stop hook detects TASK_COMPLETE and allows Claude to exit
7. If max iterations (10) reached, Claude exits with partial completion log

## Completion Promise Tags
- Still working: <promise>TASK_INCOMPLETE</promise>
- Done: <promise>TASK_COMPLETE</promise>
- Blocked (needs human): <promise>AWAITING_APPROVAL</promise>

## State File Format
/Plans/RALPH_<task_id>.md must contain:
- task description
- current iteration number
- completed steps
- remaining steps
- last output summary
