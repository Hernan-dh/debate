"""Per-call cross-provider fallback for CrewAI agents."""

from __future__ import annotations

import os
from typing import Any

from crewai.llms.base_llm import BaseLLM
from crewai.llms.providers.openai.completion import OpenAICompletion
from crewai.utilities.types import LLMMessage
from pydantic import Field

from debate.model_config import MODEL_FALLBACKS, MODEL_TIMEOUT_SECONDS, ModelSpec


class FallbackLLM(BaseLLM):
    """Retry only the failed LLM call while preserving completed CrewAI tasks."""

    attempts: list[tuple[ModelSpec, OpenAICompletion]] = Field(exclude=True)
    active_index: int = Field(default=0, exclude=True)

    def call(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Any | None = None,
        from_agent: Any | None = None,
        response_model: type[Any] | None = None,
    ) -> str | Any:
        failures: list[str] = []
        total = len(self.attempts)

        for offset in range(total):
            index = (self.active_index + offset) % total
            spec, llm = self.attempts[index]
            label = f"{spec.label}/{spec.model}"
            print(f"[models] trying {label}", flush=True)
            try:
                result = llm.call(
                    messages=messages,
                    tools=tools,
                    callbacks=callbacks,
                    available_functions=available_functions,
                    from_task=from_task,
                    from_agent=from_agent,
                    response_model=response_model,
                )
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as error:
                failures.append(f"{label}: {type(error).__name__}")
                print(f"[models] {label} failed ({type(error).__name__}); trying next", flush=True)
                continue

            self.active_index = index
            print(f"[models] completed with {label}", flush=True)
            return result

        raise RuntimeError("All configured models failed for this call: " + "; ".join(failures))

    def supports_function_calling(self) -> bool:
        return all(llm.supports_function_calling() for _, llm in self.attempts)

    def supports_stop_words(self) -> bool:
        return all(llm.supports_stop_words() for _, llm in self.attempts)

    def supports_multimodal(self) -> bool:
        return all(llm.supports_multimodal() for _, llm in self.attempts)

    def get_context_window_size(self) -> int:
        return min(llm.get_context_window_size() for _, llm in self.attempts)


def fallback_llm() -> FallbackLLM:
    """Build the shared quality-first LLM used by every debate agent."""
    attempts: list[tuple[ModelSpec, OpenAICompletion]] = []
    for spec in MODEL_FALLBACKS:
        PROVIDER_KEY = os.getenv(spec.api_key_env, "").strip()
        if not PROVIDER_KEY:
            continue
        attempts.append(
            (
                spec,
                OpenAICompletion(
                    model=spec.model,
                    api_key=PROVIDER_KEY,
                    base_url=spec.base_url,
                    provider="openai",
                    max_retries=0,
                    timeout=MODEL_TIMEOUT_SECONDS,
                    temperature=0.4,
                ),
            )
        )

    if not attempts:
        required = ", ".join(dict.fromkeys(spec.api_key_env for spec in MODEL_FALLBACKS))
        raise RuntimeError(f"Configure at least one provider key in .env: {required}")

    return FallbackLLM(model="quality-first-fallback", attempts=attempts)
