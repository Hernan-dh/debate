"""Gradio web interface for the CrewAI debate."""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from debate.crew import Debate
from debate.model_provider import fallback_llm
from styles import CSS, JS

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

UI_TEXT = {
    "English": {
        "subtitle": "MULTI-AGENT ARGUMENT ARENA",
        "greeting": "Enter a motion and I’ll present the proposition, the opposition, and the judge’s decision.",
        "placeholder": "Enter a motion to debate…",
        "submit": "Debate",
        "instruction": "Write the complete response in English.",
        "sections": ("Proposition", "Opposition", "Judge's decision"),
        "error": "I couldn't complete this debate. Please try again.",
    },
    "Español": {
        "subtitle": "ARENA DE ARGUMENTOS MULTIAGENTE",
        "greeting": "Ingresá una moción y presentaré la proposición, la oposición y la decisión del juez.",
        "placeholder": "Ingresá una moción para debatir…",
        "submit": "Debatir",
        "instruction": "Escribí la respuesta completa en español.",
        "sections": ("Proposición", "Oposición", "Decisión del juez"),
        "error": "No pude completar este debate. Intentá nuevamente.",
    },
}


def header_html(language: str) -> str:
    text = UI_TEXT.get(language, UI_TEXT["English"])
    return f"""
    <div class="debate-brand">
      <div class="debate-mark" aria-hidden="true">
        <span class="debate-bar debate-bar-1"></span>
        <span class="debate-bar debate-bar-2"></span>
        <span class="debate-bar debate-bar-3"></span>
      </div>
      <div class="debate-headings">
        <h1>AI<span class="debate-sep">/</span>DEBATE</h1>
        <p>{text['subtitle']}</p>
      </div>
    </div>
    """


def localized_ui(language: str):
    text = UI_TEXT.get(language, UI_TEXT["English"])
    greeting = [{"role": "assistant", "content": text["greeting"]}]
    return (
        header_html(language),
        greeting,
        gr.Textbox(placeholder=text["placeholder"], submit_btn=text["submit"]),
    )


def initialize_language(browser_language: str):
    language = "Español" if (browser_language or "").lower().startswith("es") else "English"
    header, greeting, textbox = localized_ui(language)
    return language, header, greeting, textbox


def debate_motion(message: str, _history, language: str) -> str:
    language = language if language in UI_TEXT else "English"
    text = UI_TEXT[language]
    motion = (message or "").strip()
    if not motion:
        return text["greeting"]

    try:
        result = Debate(llm=fallback_llm()).crew().kickoff(
            inputs={
                "motion": motion,
                "language_instruction": text["instruction"],
            }
        )
    except Exception as error:
        print(f"[web] debate failed ({type(error).__name__})", flush=True)
        return text["error"]

    outputs = [task.raw for task in result.tasks_output]
    sections = [f"## {title}\n\n{body}" for title, body in zip(text["sections"], outputs)]
    return "\n\n---\n\n".join(sections)


initial = UI_TEXT["English"]
with gr.Blocks() as demo:
    with gr.Row(elem_id="title-row"):
        with gr.Column(scale=1, min_width=0, elem_id="header-copy"):
            header = gr.HTML(header_html("English"), elem_id="debate-header")
        with gr.Column(scale=0, min_width=180, elem_id="language-control"):
            gr.Markdown("Idioma / Language:", elem_id="language-label")
            language = gr.Dropdown(
                choices=["Español", "English"],
                value="English",
                show_label=False,
                container=False,
                interactive=True,
                elem_id="language-selector",
            )

    chatbot = gr.Chatbot(
        value=[{"role": "assistant", "content": initial["greeting"]}],
        show_label=False,
        height=470,
        elem_id="debate-chatbot",
    )
    textbox = gr.Textbox(
        placeholder=initial["placeholder"],
        submit_btn=initial["submit"],
        show_label=False,
    )
    gr.ChatInterface(
        debate_motion,
        chatbot=chatbot,
        textbox=textbox,
        additional_inputs=[language],
    )

    language.change(
        localized_ui,
        inputs=language,
        outputs=[header, chatbot, textbox],
        js="(language) => { document.title = language === 'Español' ? 'Debate con IA' : 'AI Debate'; return language; }",
    )
    browser_language = gr.Textbox(visible=False)
    demo.load(
        initialize_language,
        inputs=browser_language,
        outputs=[language, header, chatbot, textbox],
        js="() => navigator.language || ''",
    )

demo.queue(default_concurrency_limit=1)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        css=CSS,
        js=JS,
        theme=gr.themes.Base(),
    )
