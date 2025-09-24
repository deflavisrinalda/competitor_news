# pages/try_the_agent.py
from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# ---- import path ----
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from competitor_flow.crews.competitor_crew.competitor_crew import CompetitorCrew  # noqa: E402

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Prova l'Agente", page_icon="🚀", layout="centered")

# ---- STYLES (Dark + Gold) ----
BG = "#0B0F1A"; CARD = "#151923"; TEXT = "#F5F7FA"; MUTED = "#9AA4B2"; BORDER = "#222733"; GOLD = "#C9A227"
st.markdown(f"""
<style>
.stApp {{ background:{BG}; color:{TEXT}; font-family:"Inter", ui-sans-serif, system-ui; }}
.hero {{ border-radius:18px; padding:28px 26px; background:linear-gradient(135deg, rgba(201,162,39,0.14), rgba(21,25,35,0.95));
        border:1px solid {BORDER}; box-shadow:0 6px 24px rgba(0,0,0,0.45); margin-bottom:16px; }}
.hero h1{{ margin:0 0 6px 0; font-weight:800; letter-spacing:-0.02em; color:{TEXT}; }}
.subtitle{{ color:{MUTED}; font-size:1.02rem; line-height:1.55rem; }}
.section-title{{ margin:8px 0 18px 0; font-weight:800; font-size:1.25rem; letter-spacing:-0.01em;
                 border-left:4px solid {GOLD}; padding-left:10px; color:{TEXT}; }}
.card{{ border:1px solid {BORDER}; border-radius:16px; padding:18px; background:{CARD}; box-shadow:0 6px 22px rgba(0,0,0,0.35); }}
.muted{{ color:{MUTED}; }}
.stButton>button{{ background:{GOLD}; color:#0A0D12; border:0; padding:.6rem 1rem; border-radius:999px; font-weight:800;
                   box-shadow:0 4px 14px rgba(201,162,39,0.35); transition: transform .02s ease, filter .15s ease; }}
.stButton>button:hover{{ filter:brightness(1.05); }}
.stButton>button:active{{ transform: translateY(1px); }}
.download-row .stDownloadButton>button{{ background:linear-gradient(135deg, {GOLD}, rgba(201,162,39,0.85)); color:#0A0D12;
                                         border:0; padding:.55rem .9rem; border-radius:12px; font-weight:800;
                                         box-shadow:0 6px 18px rgba(201,162,39,0.35); margin-right:8px; }}

/* Pannelli compatti per Insight */
.panel {{
  border: 1px solid #222733;
  border-radius: 14px;
  background: #151923;
  box-shadow: 0 6px 22px rgba(0,0,0,0.35);
  overflow: hidden;
}}
.panel-head {{
  display: inline-block;
  padding: 6px 12px;
  margin: 12px 12px 4px 12px;
  border-radius: 999px;
  background: rgba(201,162,39,0.12);
  color: #C9A227;
  font-weight: 800;
  letter-spacing: .2px;
}}
.panel-body {{
  padding: 8px 14px 14px 18px;
}}
.panel-body ul {{
  margin: 6px 0 4px 18px;
}}
.panel-body li {{
  margin: 6px 0;
  line-height: 1.35rem;
}}
</style>
""", unsafe_allow_html=True)


# ---- HERO ----
st.markdown("""
<div class="hero">
  <h1>🚀 Prova il Competitor News Agent</h1>
  <div class="subtitle">
    Inserisci un <b>competitor</b> e genera un <b>executive brief</b> con <b>fonti</b>.<br/>
    L'output include riepilogo, key takeaways, rischi, opportunità e tabella sorgenti.
  </div>
</div>
""", unsafe_allow_html=True)

# ---- Helpers ----
def _parse_json(text: str):
    text = text.strip()
    if not (text.startswith("{") or text.startswith("[")):
        start = text.find("{")
        if start != -1: text = text[start:]
        end = text.rfind("}")
        if end != -1: text = text[:end+1]
    return json.loads(text)

def _to_markdown(data: dict) -> str:
    lines = ["# Executive Summary\n", (data.get("executive_summary") or "").strip() + "\n"]
    def section(title, items):
        lines.append(f"## {title}\n")
        for it in items or []: lines.append(f"- {it}")
        lines.append("")
    section("Key Takeaways", data.get("key_takeaways"))
    section("Risks", data.get("risks"))
    section("Opportunities", data.get("opportunities"))
    table = data.get("news_table", [])
    if table:
        header = table[0] if all(isinstance(c, str) for c in table[0]) else ["Title","Date","Source","URL"]
        rows = table[1:] if header == table[0] else table
        lines += ["## Sources\n", "| " + " | ".join(header) + " |", "| " + " | ".join(["---"]*len(header)) + " |"]
        for r in rows: lines.append("| " + " | ".join(str(c or "") for c in r) + " |")
        lines.append("")
    return "\n".join(lines)

# ---- Session init ----
if "result_data" not in st.session_state:
    st.session_state.result_data = None
if "result_competitor" not in st.session_state:
    st.session_state.result_competitor = ""

# ---- INPUT FORM ----
st.markdown('<div class="section-title">Inserisci il competitor</div>', unsafe_allow_html=True)
with st.form("input_form", clear_on_submit=False):
    competitor = st.text_input("Nome competitor", value=st.session_state.result_competitor or "", placeholder="Es. OpenAI, Accenture, EY...")
    submitted = st.form_submit_button("Genera report")

if submitted:
    if not competitor.strip():
        st.warning("Inserisci un nome valido di competitor.")
    else:
        with st.spinner("Generazione in corso…"):
            result = CompetitorCrew().crew().kickoff(inputs={"competitor": competitor})
            raw = str(getattr(result, "raw", result))
        try:
            data = _parse_json(raw)
        except Exception:
            st.error("Impossibile parsare il JSON dall'output dell'agente.")
            st.code(raw)
        else:
            # ---> Salva in sessione (PERSISTE dopo i click dei download)
            st.session_state.result_data = data
            st.session_state.result_competitor = competitor

# ---- RENDER RESULT (se presente) ----
data = st.session_state.result_data
competitor = st.session_state.result_competitor

if data:
    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card">{(data.get("executive_summary") or "").strip()}</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Insight</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-head">Key Takeaways</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{x}</li>" for x in (data.get("key_takeaways") or [])) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-head">Rischi</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{x}</li>" for x in (data.get("risks") or [])) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-head">Opportunità</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        st.markdown("<ul>" + "".join(f"<li>{x}</li>" for x in (data.get("opportunities") or [])) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)


    st.write("")
    st.markdown('<div class="section-title">Fonti</div>', unsafe_allow_html=True)
    table = data.get("news_table", [])
    if table:
        header = table[0] if all(isinstance(c, str) for c in table[0]) else ["Title","Date","Source","URL"]
        rows = table[1:] if header == table[0] else table
        df = pd.DataFrame(rows, columns=header)
        if "URL" in df.columns:
            df["URL"] = df["URL"].apply(lambda u: f"[link]({u})" if isinstance(u, str) else u)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nessuna fonte disponibile.")

    st.write("")
    st.markdown('<div class="section-title">Esporta</div>', unsafe_allow_html=True)
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    md_text = _to_markdown(data)
    d1, d2, d3 = st.columns([1,1,1])
    with d1:
        st.markdown('<div class="download-row">', unsafe_allow_html=True)
        st.download_button("⬇️ Scarica JSON", data=json_bytes,
                           file_name=f"{(competitor or 'report').lower()}_brief.json",
                           mime="application/json")
        st.markdown("</div>", unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="download-row">', unsafe_allow_html=True)
        st.download_button("⬇️ Scarica Markdown", data=md_text.encode("utf-8"),
                           file_name=f"{(competitor or 'report').lower()}_brief.md",
                           mime="text/markdown")
        st.markdown("</div>", unsafe_allow_html=True)

