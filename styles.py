"""Agentic Twin visual identity adapted for the debate interface."""

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Manrope:wght@400;500;600;700&display=swap');

:root {
  --ui-bg: #111412;
  --ui-surface: #181c19;
  --ui-raised: #202522;
  --ui-border: #343a35;
  --ui-text: #e9e9e3;
  --ui-muted: #909690;
  --ui-acid: #c7ff37;
  --ui-orange: #ff6947;
  --ui-mono: 'DM Mono', monospace;
  --ui-sans: 'Manrope', sans-serif;
}

footer, .built-with, .show-api, .api-docs { display: none !important; }
html, body, gradio-app { background: var(--ui-bg) !important; color-scheme: dark; }
body {
  background-image: linear-gradient(rgb(255 255 255 / 2.5%) 1px, transparent 1px), linear-gradient(90deg, rgb(255 255 255 / 2.5%) 1px, transparent 1px) !important;
  background-size: 42px 42px !important;
}

.gradio-container {
  width: 100% !important;
  max-width: 920px !important;
  min-width: 0 !important;
  margin: 0 auto !important;
  padding: 34px 24px 48px !important;
  background: transparent !important;
  color: var(--ui-text) !important;
  font-family: var(--ui-sans) !important;
}
.gradio-container *, .gradio-container .main, .gradio-container .contain, .gradio-container .wrap { min-width: 0; }
.gradio-container .main, .gradio-container .contain, .gradio-container .wrap { width: 100% !important; max-width: 100% !important; }

#title-row {
  align-items: center !important;
  flex-wrap: nowrap !important;
  gap: 28px !important;
  margin-bottom: 2.5rem !important;
  padding-bottom: 1.25rem !important;
  border-bottom: 3px solid var(--ui-text) !important;
}
#header-copy, #debate-header { margin: 0 !important; padding: 0 !important; }
.debate-brand { display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 1.4rem; }
.debate-mark { display: flex; flex-direction: column; gap: 5px; width: 38px; }
.debate-bar { display: block; height: 7px; }
.debate-bar-1 { width: 100%; background: #ecad0a; }
.debate-bar-2 { width: 70%; background: #209dd7; }
.debate-bar-3 { width: 45%; background: #753991; }
.debate-headings h1 {
  margin: 0 !important;
  color: var(--ui-text) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
  font-size: clamp(1.8rem, 4vw, 2.6rem) !important;
  font-weight: 900 !important;
  line-height: .95 !important;
  letter-spacing: -.045em !important;
}
.debate-sep { margin: 0 .04em; color: #ecad0a; font-weight: 300; }
.debate-headings p { margin: .55rem 0 0 !important; color: var(--ui-muted) !important; font: 400 .7rem var(--ui-mono) !important; letter-spacing: .22em; }

#language-control { width: 170px !important; min-width: 170px !important; max-width: 170px !important; flex: 0 0 170px !important; gap: 5px !important; margin-left: auto !important; }
#language-label, #language-selector { width: 100% !important; margin: 0 !important; padding: 0 !important; }
#language-label p { margin: 0 !important; color: var(--ui-muted) !important; font: 400 9px var(--ui-mono) !important; letter-spacing: .08em; text-transform: uppercase; }
#language-selector input { height: 34px !important; min-height: 34px !important; padding: 5px 9px !important; font: 400 11px var(--ui-mono) !important; }
#language-selector button { width: 34px !important; height: 34px !important; min-height: 34px !important; padding: 0 !important; }

.motion-examples-label,
.motion-examples-label > div,
.motion-examples,
.motion-examples > div {
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}
.motion-examples-label {
  display: flex !important;
  align-items: center !important;
  gap: .85rem !important;
  margin: 0 0 .85rem !important;
}
.motion-examples-label::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--ui-border);
}
.motion-examples-label p {
  margin: 0 !important;
  color: var(--ui-muted) !important;
  font: 400 .65rem var(--ui-mono) !important;
  letter-spacing: .28em;
  text-transform: uppercase;
}
.motion-examples {
  gap: 8px !important;
  margin: 0 0 18px !important;
  padding: 0 !important;
  background: transparent !important;
}
.motion-examples button {
  min-height: 72px !important;
  height: auto !important;
  padding: .7rem 1.05rem !important;
  border: 1.5px solid var(--ui-border) !important;
  background: var(--ui-surface) !important;
  color: var(--ui-text) !important;
  font: 500 .9rem/1.45 var(--ui-sans) !important;
  letter-spacing: 0 !important;
  text-align: left !important;
  text-transform: none !important;
  white-space: normal !important;
  box-shadow: none !important;
  transition: border-color .15s, color .15s, transform .1s !important;
}
.motion-examples button:hover {
  border-color: #753991 !important;
  color: #a56bc2 !important;
  transform: translateY(-1px);
}

#motion-examples-en,
#motion-examples-es,
#motion-examples-en > div,
#motion-examples-es > div,
#motion-examples-en .form,
#motion-examples-es .form,
#motion-examples-en .wrap,
#motion-examples-es .wrap {
  margin: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}
#motion-examples-en,
#motion-examples-es { gap: 8px !important; margin-bottom: 12px !important; }
#motion-examples-en button,
#motion-examples-es button {
  min-height: 54px !important;
  padding: 8px 12px !important;
  border: 1px solid var(--ui-border) !important;
  background: var(--ui-surface) !important;
  color: var(--ui-text) !important;
  font: 500 12px/1.35 var(--ui-sans) !important;
  letter-spacing: 0 !important;
  text-align: left !important;
  text-transform: none !important;
  white-space: normal !important;
}
#motion-examples-en button:hover,
#motion-examples-es button:hover {
  border-color: var(--ui-acid) !important;
  color: var(--ui-acid) !important;
  background: var(--ui-raised) !important;
}

.block, .form { background: transparent !important; box-shadow: none !important; }
.chatbot, .chatbot *, .block, .form, button, input, textarea { border-radius: 0 !important; }
.chatbot > .block-label, .chatbot > label, .chatbot .label-wrap, .chatbot .block-label { display: none !important; }
#debate-chat-en, #debate-chat-es,
#debate-chat-en.chatbot, #debate-chat-es.chatbot {
  height: 390px !important;
  min-height: 390px !important;
  border: 1px solid var(--ui-border) !important;
  background: rgb(24 28 25 / 94%) !important;
  box-shadow: 18px 18px 0 rgb(0 0 0 / 18%) !important;
}
#debate-chat-en *, #debate-chat-es * { font-family: var(--ui-sans) !important; }
.message-row, .message-row > div, .message-row .role, .message-wrap, .bubble-wrap { border: 0 !important; background: transparent !important; box-shadow: none !important; }
.message-row .message, .message-row .message-bubble, .message-row .bubble { padding: 10px 13px !important; border: 0 !important; box-shadow: none !important; font-size: 14px !important; line-height: 1.6 !important; }
.message-row.user-row .message, .message-row.user-row .message-bubble, .message-row[data-role='user'] .message { background: var(--ui-acid) !important; color: var(--ui-bg) !important; }
.message-row.bot-row .message, .message-row.bot-row .message-bubble, .message-row[data-role='assistant'] .message, .message-row[data-role='assistant'] .message-bubble { border-left: 2px solid var(--ui-orange) !important; background: var(--ui-raised) !important; color: var(--ui-text) !important; }
.message-row .message a, .message-row .message-bubble a { color: var(--ui-acid) !important; }

textarea, input[type='text'] { min-height: 50px !important; padding: 13px 14px !important; border: 1px solid var(--ui-border) !important; background: var(--ui-surface) !important; color: var(--ui-text) !important; font: 400 14px/1.45 var(--ui-sans) !important; }
textarea:focus, input[type='text']:focus { border-color: var(--ui-acid) !important; outline: none !important; box-shadow: 0 0 0 1px var(--ui-acid) !important; }
textarea::placeholder, input::placeholder { color: var(--ui-muted) !important; }
button { min-height: 50px !important; display: inline-flex !important; align-items: center !important; justify-content: center !important; padding: 0 16px !important; border: 1px solid var(--ui-border) !important; background: var(--ui-surface) !important; color: var(--ui-text) !important; font: 500 10px var(--ui-mono) !important; letter-spacing: .1em !important; text-transform: uppercase !important; }
button:hover { border-color: var(--ui-acid) !important; color: var(--ui-acid) !important; }
button.primary, button[variant='primary'], button.submit, button.submit-button, .submit-button { border-color: var(--ui-acid) !important; background: var(--ui-acid) !important; color: var(--ui-bg) !important; }
.icon-button, .chatbot .icon-button { min-height: 0 !important; padding: 4px !important; border: 0 !important; background: transparent !important; color: var(--ui-muted) !important; }

@media (max-width: 640px) {
  .gradio-container { padding: 22px 14px 34px !important; }
  #title-row { flex-wrap: wrap !important; gap: 16px !important; }
  #language-control { width: 100% !important; max-width: 170px !important; margin-left: 0 !important; }
  .motion-examples { flex-direction: column !important; }
  #debate-chat-en, #debate-chat-es,
  #debate-chat-en.chatbot, #debate-chat-es.chatbot { height: 420px !important; min-height: 420px !important; box-shadow: 8px 8px 0 rgb(0 0 0 / 18%) !important; }
}
"""

JS = r"""
() => {
  document.title = (navigator.language || '').toLowerCase().startsWith('es') ? 'Debate con IA' : 'AI Debate';
  const focus = () => document.querySelector('textarea')?.focus();
  setTimeout(focus, 400);
  new MutationObserver(focus).observe(document.body, { childList: true, subtree: true });
}
"""
