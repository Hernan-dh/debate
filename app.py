"""Bilingual Gradio interface for the CrewAI debate."""

from __future__ import annotations

import os
import random
import queue
import threading
from pathlib import Path

import gradio as gr
from report_export import download_controls, prepare_with_downloads, finish_with_downloads, finish_with_progress_downloads
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
        "examples": "Example motions",
        "status": "**Debate pipeline running**\n\n1. **Proposition Debater** is building the case in favor.\n2. **Opposition Debater** will build the case against.\n3. **Judge** will compare both arguments and produce an impartial decision.",
    },
    "Español": {
        "subtitle": "ARENA DE ARGUMENTOS MULTIAGENTE",
        "greeting": "Ingresá una moción y presentaré la proposición, la oposición y la decisión del juez.",
        "placeholder": "Ingresá una moción para debatir…",
        "submit": "Debatir",
        "instruction": "Escribí la respuesta completa en español.",
        "sections": ("Proposición", "Oposición", "Decisión del juez"),
        "error": "No pude completar este debate. Intentá nuevamente.",
        "examples": "Mociones de ejemplo",
        "status": "**Flujo de debate en ejecución**\n\n1. **Debatiente de proposición** está construyendo el argumento a favor.\n2. **Debatiente de oposición** construirá el argumento en contra.\n3. **Juez** comparará ambos argumentos y emitirá una decisión imparcial.",
    },
}

ENGLISH_MOTIONS = (
    "remote work should be the default for knowledge workers",
    "governments should strictly regulate artificial intelligence",
    "universities should replace traditional exams with project-based assessment",
    "social media platforms should require verified identities",
    "a four-day workweek should become the legal standard",
    "public transportation should be free in major cities",
    "nuclear energy is essential to fighting climate change",
    "companies should disclose the salary range for every job opening",
    "voting should be mandatory in national elections",
    "autonomous vehicles should be prioritized over public transit investment",
)
SPANISH_MOTIONS = (
    "el trabajo remoto debería ser la opción predeterminada para los trabajadores del conocimiento",
    "los gobiernos deberían regular estrictamente la inteligencia artificial",
    "las universidades deberían reemplazar los exámenes tradicionales por evaluaciones basadas en proyectos",
    "las plataformas sociales deberían exigir identidades verificadas",
    "la semana laboral de cuatro días debería convertirse en el estándar legal",
    "el transporte público debería ser gratuito en las grandes ciudades",
    "la energía nuclear es esencial para combatir el cambio climático",
    "las empresas deberían publicar el rango salarial de cada oferta laboral",
    "el voto debería ser obligatorio en las elecciones nacionales",
    "los vehículos autónomos deberían tener prioridad sobre la inversión en transporte público",
)
SUGGESTED_INDICES = random.sample(range(len(ENGLISH_MOTIONS)), k=3)


def suggested_motions(language: str) -> list[str]:
    source = SPANISH_MOTIONS if language == "Español" else ENGLISH_MOTIONS
    return [source[index].capitalize() for index in SUGGESTED_INDICES]


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
    return (
        header_html(language),
        gr.Group(visible=language == "English"),
        gr.Group(visible=language == "Español"),
    )


def initialize_language(browser_language: str):
    language = "Español" if (browser_language or "").lower().startswith("es") else "English"
    header, english_group, spanish_group = localized_ui(language)
    return language, header, english_group, spanish_group


def debate_motion(message: str, _history, language: str, task_callback=None) -> str:
    language = language if language in UI_TEXT else "English"
    text = UI_TEXT[language]
    motion = (message or "").strip()
    if not motion:
        return text["greeting"]
    try:
        result = Debate(llm=fallback_llm(), task_callback=task_callback).crew().kickoff(
            inputs={"motion": motion, "language_instruction": text["instruction"]}
        )
    except Exception as error:
        print(f"[web] debate failed ({type(error).__name__})", flush=True)
        return text["error"]
    outputs = [task.raw for task in result.tasks_output]
    sections = [f"## {title}\n\n{body}" for title, body in zip(text["sections"], outputs)]
    return "\n\n---\n\n".join(sections)


def submit_motion(message: str, history: list[dict], language: str):
    """Render the user turn before the queued research starts."""
    message = (message or "").strip()
    if not message:
        raise gr.Error("Ingresá una moción." if language == "Español" else "Enter a motion.")
    status = UI_TEXT[language if language in UI_TEXT else "English"]["status"]
    return gr.Textbox(value="", interactive=False), [
        *(history or []),
        {"role": "user", "content": message},
        {"role": "assistant", "content": status},
    ], gr.Button(interactive=False)


def finish_submission(history: list[dict], language: str):
    if len(history) < 2 or history[-2]["role"] != "user":
        return gr.Textbox(interactive=True), history, gr.Button(interactive=True)
    content = history[-2]["content"]
    # Gradio 6 normalizes Chatbot input into typed content blocks.
    message = content if isinstance(content, str) else "\n".join(
        block["text"] for block in content if block.get("type") == "text"
    )
    response = debate_motion(message, history[:-2], language)
    return gr.Textbox(interactive=True), [
        *history[:-1],
        {"role": "assistant", "content": response},
    ], gr.Button(interactive=True)


def finish_submission_progress(history: list[dict], language: str):
    """Stream sequential CrewAI task progress into the pending chat message."""
    if len(history) < 2 or history[-2]["role"] != "user":
        yield gr.Textbox(interactive=True), history, gr.Button(interactive=True), True
        return
    content = history[-2]["content"]
    motion = content if isinstance(content, str) else "\n".join(block["text"] for block in content if block.get("type") == "text")
    text = UI_TEXT[language]
    updates = queue.Queue()
    stages = (
        "**Opposition Debater** is building the case against the motion.",
        "**Judge** is comparing both arguments and producing an impartial decision.",
    ) if language == "English" else (
        "**Debatiente de oposición** está construyendo el argumento en contra.",
        "**Juez** está comparando ambos argumentos para emitir una decisión imparcial.",
    )
    callback_count = 0
    def on_task_complete(_output):
        nonlocal callback_count
        callback_count += 1
        if callback_count <= len(stages):
            updates.put((stages[callback_count - 1], False))
    def work():
        try:
            updates.put((debate_motion(motion, history[:-2], language, task_callback=on_task_complete), True))
        except Exception as error:
            print(f"[web] debate failed ({type(error).__name__})", flush=True)
            updates.put((text["error"], True))
    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    while thread.is_alive() or not updates.empty():
        try:
            update, completed = updates.get(timeout=0.1)
        except queue.Empty:
            continue
        yield gr.Textbox(interactive=completed), [*history[:-1], {"role": "assistant", "content": update}], gr.Button(interactive=completed), completed


def submit_english(message: str, history: list[dict]):
    return submit_motion(message, history, "English")


def submit_spanish(message: str, history: list[dict]):
    return submit_motion(message, history, "Español")


def finish_english(history: list[dict]):
    return finish_submission(history, "English")


def finish_english_progress(history: list[dict]):
    yield from finish_submission_progress(history, "English")


def finish_spanish(history: list[dict]):
    return finish_submission(history, "Español")


def finish_spanish_progress(history: list[dict]):
    yield from finish_submission_progress(history, "Español")


initial = UI_TEXT["English"]
with gr.Blocks(delete_cache=(3600, 86400)) as demo:
    with gr.Row(elem_id="title-row"):
        with gr.Column(scale=1, min_width=0, elem_id="header-copy"):
            header = gr.HTML(header_html("English"), elem_id="debate-header")
        with gr.Column(scale=0, min_width=180, elem_id="language-control"):
            gr.Markdown("Idioma / Language:", elem_id="language-label")
            language = gr.Dropdown(
                choices=["Español", "English"], value="English", show_label=False,
                container=False, interactive=True, elem_id="language-selector",
            )

    with gr.Group(visible=True) as english_chat:
        english_motions = suggested_motions("English")
        english_chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": initial["greeting"]}],
            show_label=False, height=520, elem_id="debate-chat-en",
        )
        english_report, english_download = download_controls("English")
        gr.Markdown(initial["examples"], elem_classes="motion-examples-label")
        with gr.Row(elem_id="motion-examples-en", elem_classes="motion-examples"):
            english_buttons = [gr.Button(motion) for motion in english_motions]
        with gr.Row(elem_id="motion-input-row-en", elem_classes="motion-input-row"):
            english_textbox = gr.Textbox(
                placeholder=initial["placeholder"], show_label=False, container=False,
                scale=1, elem_id="motion-input-en",
            )
            english_submit = gr.Button(initial["submit"], variant="primary", scale=0)
        for button, motion in zip(english_buttons, english_motions):
            button.click(lambda value=motion: value, outputs=english_textbox)
        english_submit.click(
            prepare_with_downloads(submit_english), [english_textbox, english_chatbot],
            [english_textbox, english_chatbot, english_submit, english_report, english_download], queue=False,
        ).success(
            finish_with_progress_downloads(finish_english_progress, UI_TEXT["English"]["error"]), english_chatbot,
            [english_textbox, english_chatbot, english_submit, english_report, english_download], show_progress="hidden",
        )
        english_textbox.submit(
            prepare_with_downloads(submit_english), [english_textbox, english_chatbot],
            [english_textbox, english_chatbot, english_submit, english_report, english_download], queue=False,
        ).success(
            finish_with_progress_downloads(finish_english_progress, UI_TEXT["English"]["error"]), english_chatbot,
            [english_textbox, english_chatbot, english_submit, english_report, english_download], show_progress="hidden",
        )

    with gr.Group(visible=False) as spanish_chat:
        spanish = UI_TEXT["Español"]
        spanish_motions = suggested_motions("Español")
        spanish_chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": spanish["greeting"]}],
            show_label=False, height=520, elem_id="debate-chat-es",
        )
        spanish_report, spanish_download = download_controls("Español")
        gr.Markdown(spanish["examples"], elem_classes="motion-examples-label")
        with gr.Row(elem_id="motion-examples-es", elem_classes="motion-examples"):
            spanish_buttons = [gr.Button(motion) for motion in spanish_motions]
        with gr.Row(elem_id="motion-input-row-es", elem_classes="motion-input-row"):
            spanish_textbox = gr.Textbox(
                placeholder=spanish["placeholder"], show_label=False, container=False,
                scale=1, elem_id="motion-input-es",
            )
            spanish_submit = gr.Button(spanish["submit"], variant="primary", scale=0)
        for button, motion in zip(spanish_buttons, spanish_motions):
            button.click(lambda value=motion: value, outputs=spanish_textbox)
        spanish_submit.click(
            prepare_with_downloads(submit_spanish), [spanish_textbox, spanish_chatbot],
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], queue=False,
        ).success(
            finish_with_progress_downloads(finish_spanish_progress, UI_TEXT["Español"]["error"]), spanish_chatbot,
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], show_progress="hidden",
        )
        spanish_textbox.submit(
            prepare_with_downloads(submit_spanish), [spanish_textbox, spanish_chatbot],
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], queue=False,
        ).success(
            finish_with_progress_downloads(finish_spanish_progress, UI_TEXT["Español"]["error"]), spanish_chatbot,
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], show_progress="hidden",
        )

    language.change(
        localized_ui, inputs=language, outputs=[header, english_chat, spanish_chat],
        js="(language) => { document.title = language === 'Español' ? 'Debate con IA' : 'AI Debate'; return language; }",
    )
    browser_language = gr.Textbox(visible=False)
    demo.load(
        initialize_language, inputs=browser_language, outputs=[language, header, english_chat, spanish_chat],
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
