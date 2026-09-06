# AI Debate

A bilingual assistant for exploring arguments on both sides of a motion and comparing them through a separate generated judgment.

## Attribution

Project built from [Ed Donner's agentic AI engineering course](https://github.com/ed-donner/agents). The upstream MIT copyright notice is preserved in [LICENSE](LICENSE). No endorsement by the course author is implied.

## Run locally

Python 3.12 and uv are the documented development baseline.  Run the following commands from this repository's root.

```sh
uv sync
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell, or `cp .env.example .env` on Linux/macOS), then replace only the placeholders for the providers you intend to use. Leave unused credentials empty. Never commit the real `.env`.

Configure at least one model-provider key. `SERPER_API_KEY` is optional: the debater uses Serper when configured and DDGS otherwise. Open `http://127.0.0.1:7860`, enter a motion, and read both arguments and the judgment. Use `uv run crewai run` for the CLI.

```sh
uv run python app.py
```

## Download results

After a request completes, choose Markdown (.md), Word (.docx) or PDF (.pdf),
then select **Prepare download** and click the generated file. Spanish controls
use **Preparar descarga**. Downloads contain the last completed report in that
chat, including sources. Starting another request clears the previous download.

Markdown preserves the original result. DOCX and PDF retain headings, lists,
tables and source URLs with a simplified layout; they do not reproduce the chat
styling or fetch external images. PDF uses an embedded font for English and
Spanish; glyph coverage for other scripts is limited. Files are temporary, so
save a local copy.

## Architecture

```text
Gradio / CLI motion -> debater with optional Serper/DDGS evidence -> proposition -> opposition -> judge -> formatted arguments and decision
```

See [architecture](docs/ARCHITECTURE.md) for components, data flow and trust boundaries, and [operations](docs/OPERATIONS.md) for configuration and recovery.

## Technologies

Python, CrewAI, Gradio 6, YAML, uv and unittest; Gemini, Groq and OpenRouter model providers.

## Reproducible tests

After installing the dependencies above:

```sh
uv run python -m unittest discover -v
uv run python scripts/verify.py
```

Coverage: Actual Gradio message serialization, immediate user feedback, repeated turns, empty-input rejection and backend failure handling; model calls are mocked. Tests run without real credentials or paid API calls. They do not measure model quality, live provider availability, or full browser behavior. CI installs dependencies and runs the same verifier on pushes and pull requests.

## Limitations

Arguments and judgments are generated, not fact-checked or objectively impartial. Each motion is independent; visible chat history is not conversational memory. Output files are shared across executions; do not scale concurrent workers without isolating them. The public UI has no authentication or application-level abuse quotas.

Prompts and relevant context are sent to external model/search providers. Do not submit secrets or confidential data. Provider names in source code are configuration, not promises of current availability, pricing, or free access.

## Public repository and license

The repository includes a placeholder-only [.env.example](.env.example); local credentials, caches and generated artifacts are excluded by [.gitignore](.gitignore). See [operations](docs/OPERATIONS.md) for verification and publication instructions.

The code is distributed under the [MIT license](LICENSE). Dependencies retain their own licenses. Biographical material, third-party documents, logos and linked content are not relicensed by this code license. Publishing scripts can send code diffs to external models when generating commit text; use explicit metadata to avoid that step.
