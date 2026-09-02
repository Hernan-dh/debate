# Architecture

## Purpose

`debate` is a CrewAI project whose agents and tasks are configured in YAML and orchestrated from Python.

## Components

- `src/debate/config/agents.yaml`: agent roles, goals, and backstories.
- `src/debate/config/tasks.yaml`: task descriptions and expected outputs.
- `src/debate/crew.py`: CrewAI agent, task, and crew construction.
- `src/debate/main.py`: command-line entry points and kickoff inputs.
- `knowledge/`: versioned knowledge supplied to the crew.
- `output/` and `sandbox*/`: generated execution artifacts excluded from Git.
- `scripts/`: shared verification, documentation, hook installation, and safe publishing commands.

## Trust boundaries

- Prompts, model responses, tool results, generated code, and generated reports are untrusted.
- Credentials are loaded from the environment and must not enter Git, prompts, logs, or documentation.
- CrewAI model and tool providers are external services.

## Related decisions

- [Continuous documentation and safe publishing](decisions/0001-continuous-documentation-and-safe-publishing.md)
