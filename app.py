"""Gradio web interface for the CrewAI debate."""

from __future__ import annotations

import os
import random
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

ENGLISH_MOTIONS = (
    "Remote work should be the default for knowledge workers",
    "Governments should strictly regulate artificial intelligence",
    "Universities should replace traditional exams with project-based assessment",
    "Social media platforms should require verified identities",
    "A four-day workweek should become the legal standard",
    "Public transportation should be free in major cities",
    "Nuclear energy is essential to fighting climate change",
    "Companies should disclose the salary range for every job opening",
    "Voting should be mandatory in national elections",
    "Autonomous vehicles should be prioritized over public transit investment",
)

SPANISH_MOTIONS = (
    "El trabajo remoto debería ser la opción predeterminada para los trabajadores del conocimiento",
    "Los gobiernos deberían regular estrictamente la inteligencia artificial",
    "Las universidades deberían reemplazar los exámenes tradicionales por evaluaciones basadas en proyectos",
    "Las plataformas sociales deberían exigir identidades verificadas",
    "La semana laboral de cuatro días debería convertirse en el estándar legal",
    "El transporte público debería ser gratuito en las grandes ciudades",
    "La energía nuclear es esencial para combatir el cambio climático",
    "Las empresas deberían publicar el rango salarial de cada oferta laboral",
    "El voto debería ser obligatorio en las elecciones nacionales",
    "Los vehículos autónomos deberían tener prioridad sobre la inversión en transporte público",
)

SUGGESTED_INDICES = random.sample(range(len(ENGLISH_MOTIONS)), k=3)


def suggested_motions(language: str) -> list[str]:
    source = SPANISH_MOTIONS if language == "Español" else ENGLISH_MOTIONS
    return [source[index] for index in SUGGESTED_INDICES]


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
    return (
        header_html(language),
        gr.Group(visible=language == "English"),
        gr.Group(visible=language == "Español"),
    )


def initialize_language(browser_language: str):
    language = "Español" if (browser_language or "").lower().startswith("es") else "English"
    header, english_group, spanish_group = localized_ui(language)
    return language, header, english_group, spanish_group


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


def debate_english(message: str, history) -> str:
    return debate_motion(message, history, "English")


def debate_spanish(message: str, history) -> str:
    return debate_motion(message, history, "Español")


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

    with gr.Group(visible=True) as english_chat:
        english_examples = suggested_motions("English")
        with gr.Row(elem_id="motion-examples-en", elem_classes="motion-examples"):
            english_buttons = [gr.Button(motion) for motion in english_examples]
        english_textbox = gr.Textbox(
            placeholder=initial["placeholder"],
            submit_btn=initial["submit"],
            show_label=False,
            render=False,
        )
        gr.ChatInterface(
            debate_english,
            chatbot=gr.Chatbot(
                value=[{"role": "assistant", "content": initial["greeting"]}],
                show_label=False,
                height=390,
                elem_id="debate-chat-en",
            ),
            textbox=english_textbox,
            flagging_mode="never",
        )
        for button, motion in zip(english_buttons, english_examples):
            button.click(lambda value=motion: value, outputs=english_textbox)
    with gr.Group(visible=False) as spanish_chat:
        spanish = UI_TEXT["Español"]
        spanish_examples = suggested_motions("Español")
        with gr.Row(elem_id="motion-examples-es", elem_classes="motion-examples"):
            spanish_buttons = [gr.Button(motion) for motion in spanish_examples]
        spanish_textbox = gr.Textbox(
            placeholder=spanish["placeholder"],
            submit_btn=spanish["submit"],
            show_label=False,
            render=False,
        )
        gr.ChatInterface(
            debate_spanish,
            chatbot=gr.Chatbot(
                value=[{"role": "assistant", "content": spanish["greeting"]}],
                show_label=False,
                height=390,
                elem_id="debate-chat-es",
            ),
            textbox=spanish_textbox,
            flagging_mode="never",
        )
        for button, motion in zip(spanish_buttons, spanish_examples):
            button.click(lambda value=motion: value, outputs=spanish_textbox)

    language.change(
        localized_ui,
        inputs=language,
        outputs=[header, english_chat, spanish_chat],
        js="(language) => { document.title = language === 'Español' ? 'Debate con IA' : 'AI Debate'; return language; }",
    )
    browser_language = gr.Textbox(visible=False)
    demo.load(
        initialize_language,
        inputs=browser_language,
        outputs=[language, header, english_chat, spanish_chat],
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
