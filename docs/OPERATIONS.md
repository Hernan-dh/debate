# Operations

## Local setup

1. Install Python 3.10–3.13 and `uv`.
2. Run `uv sync`.
3. Copy `.env.example` to `.env` and set local credentials.
4. Run `uv run crewai run`.

For the Gradio interface, run `uv run python app.py` and open
`http://127.0.0.1:7860`.

At least one of `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY` must
be configured. The terminal logs each model attempt without printing secrets.
Fallback occurs per model call, so a later provider failure does not discard
tasks that already completed.

## Render

Deploy `render.yaml` and configure `GEMINI_API_KEY`, `GROQ_API_KEY`, and/or
`OPENROUTER_API_KEY` in Render. The service binds to `0.0.0.0` and Render's
`PORT` automatically.

Generated files in `output/` and `sandbox*/` are local artifacts and are excluded from publication.

## Verification

Run `./scripts/verify.sh`, or on Windows run `uv run python scripts/verify.py`.

Enable the repository-managed pre-commit hook once per clone with `uv run python scripts/install_hooks.py`. GitHub Actions runs the same verifier.

## Documentation

- Rebuild the changelog: `uv run python scripts/document.py changelog`.
- Create an ADR draft: `uv run python scripts/document.py decision "Decision title"`.

## Publishing

Preview a proposal with `uv run python scripts/publish.py --preview`. Interactive publication verifies the repository, proposes an English Conventional Commit title through Gemini with Groq fallback, and requires typing `PUBLISH` before staging, committing, and pushing.

Provide `--title` and `--description` to avoid external metadata generation. Commits and pushes always require explicit user authorization.

## Recovery

- If verification fails, fix every reported item and rerun it.
- If metadata generation fails, inspect the provider attempt names, verify local keys and quotas, or provide commit metadata manually.
- Never recover with a force-push.

Gradio 6 represents Chatbot input content as typed blocks. The submission handler extracts text before calling the research backend. When checking chat changes, round-trip history through Chatbot.postprocess and Chatbot.preprocess; testing only plain string dictionaries misses this conversion.
