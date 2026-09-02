# Debate Crew

Welcome to the Debate Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

Copy `.env.example` to `.env` and configure at least one of
`GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY`.

Runtime model names and their quality-first fallback order are committed in
`src/debate/model_config.py`. A failed model call moves to the next provider
without restarting completed tasks. Credentials remain local in `.env`.

- Modify `src/debate/config/agents.yaml` to define your agents
- Modify `src/debate/config/tasks.yaml` to define your tasks
- Modify `src/debate/crew.py` to add your own logic, tools and specific args
- Modify `src/debate/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the debate Crew, assembling the agents and assigning them tasks as defined in your configuration.

### Gradio chatbot

Run the bilingual web interface locally with:

```bash
uv run python app.py
```

Open `http://127.0.0.1:7860`. Each message is treated as a motion and returns
the proposition, opposition, and judge's decision. The interface defaults to
English unless the browser language starts with `es`.

`render.yaml` defines the Render web service. Configure at least one runtime
provider key in Render and deploy the repository as a Blueprint or Web Service.

The command asks for a motion, runs the arguments and judgment, and writes the
results under `output/`.

## Understanding Your Crew

The debate Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Debate Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
