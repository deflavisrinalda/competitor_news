# streamlit_app.py
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

st.set_page_config(page_title="AI Agent — Presentazione", page_icon="🤖", layout="wide")

# ------------------ STYLES (Dark + Gold) ------------------
BG = "#0B0F1A"        # quasi-nero
PANEL = "#111318"     # surface 1
CARD = "#151923"      # surface 2
TEXT = "#F5F7FA"      # testo chiaro
MUTED = "#9AA4B2"     # testo secondario
BORDER = "#222733"    # bordo
GOLD = "#C9A227"      # accento
GOLD_SOFT = "rgba(201,162,39,0.18)"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {BG};
        color: {TEXT};
        font-family: "Inter", ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial;
    }}
    /* hero */
    .hero {{
        border-radius: 18px;
        padding: 40px 36px;
        background: linear-gradient(135deg, {GOLD_SOFT}, rgba(17,19,24,0.9));
        border: 1px solid {BORDER};
        box-shadow: 0 8px 28px rgba(0,0,0,0.45);
    }}
    .hero h1 {{
        margin: 0 0 10px 0;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: {TEXT};
    }}
    .subtitle {{
        color: {MUTED};
        font-size: 1.06rem;
        line-height: 1.7rem;
    }}
    .pill {{
        display:inline-block; padding:6px 12px; border-radius:999px;
        border:1px solid {GOLD}; background:rgba(201,162,39,0.10); color:{GOLD};
        font-weight:600; margin-bottom:10px;
    }}
    /* sections */
    .section-title {{
        margin: 8px 0 18px 0;
        font-weight: 800; font-size: 1.35rem; letter-spacing: -0.01em;
        border-left: 4px solid {GOLD}; padding-left: 10px; color: {TEXT};
    }}
    /* cards */
    .card {{
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 18px;
        background: {CARD};
        box-shadow: 0 6px 22px rgba(0,0,0,0.35);
        height: 100%;
    }}
    .card h3 {{ margin: 0 0 8px 0; font-weight: 700; color: {GOLD}; }}
    .muted {{ color: {MUTED}; }}
    .kpi {{ border-left: 4px solid {GOLD}; padding-left: 12px; margin-bottom: 6px; }}

    /* table */
    .tbl {{
        width:100%; border-collapse:collapse; overflow:hidden; border-radius:12px;
        border:1px solid {BORDER}; box-shadow:0 6px 22px rgba(0,0,0,0.35);
        background:{CARD}; color:{TEXT};
    }}
    .tbl th {{
        text-align:left; padding:12px 14px;
        background: linear-gradient(180deg, rgba(201,162,39,0.14), rgba(21,25,35,0.9));
        color:{TEXT}; border-bottom:1px solid {BORDER};
    }}
    .tbl td {{ padding:12px 14px; border-bottom:1px solid {BORDER}; }}
    .tbl tr:hover td {{ background: rgba(201,162,39,0.06); }}

    /* buttons / links */
    .stButton>button {{
        background: {GOLD}; color: #0A0D12; border: 0; padding: 0.6rem 1rem;
        border-radius: 999px; font-weight: 800;
        box-shadow: 0 6px 20px rgba(201,162,39,0.35);
        transition: transform .02s ease, filter .15s ease;
    }}
    .stButton>button:hover {{ filter: brightness(1.05); }}
    .stButton>button:active {{ transform: translateY(1px); }}
    a, .stMarkdown a {{ color: {GOLD}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    /* CTA */
    .cta {{
        border-radius: 16px; padding: 22px;
        background: linear-gradient(135deg, rgba(201,162,39,0.12), rgba(21,25,35,0.95));
        border: 1px solid {BORDER}; text-align:center;
        box-shadow: 0 6px 22px rgba(0,0,0,0.45);
    }}
    .cta h3 {{ margin:0 0 10px 0; font-weight:800; color:{TEXT}; }}
    .footer {{ text-align:center; color:{MUTED}; font-size:.9rem; margin-top:12px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ HERO ------------------
st.markdown(
    """
    <div class="hero">
      <div class="pill">AI Agent • Dark Gold</div>
      <h1>Cos’è un AI Agent e come porta valore</h1>
      <div class="subtitle">
        Un agente è un sistema che può <b>ragionare</b>, <b>pianificare</b> e <b>agire</b> sulla base di informazioni fornite.
        Può <b>gestire flussi di lavoro</b>, <b>usare strumenti esterni</b> e <b>adattarsi</b> quando cambiano dati e contesto.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ---------- Sezione: Cos’è un agente ----------
st.markdown('<div class="section-title">Cos’è un AI Agent</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="card">
          <h3>🎯 Goal-oriented</h3>
          <div class="muted">Parte da un obiettivo e decide <i>come</i> raggiungerlo.</div>
          <div class="kpi">Reason → Plan → Act → Observe → Adapt</div>
          <ul>
            <li>Seleziona strategie e strumenti</li>
            <li>Itera finché il goal è soddisfatto</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )
with c2:
    st.markdown(
        """
        <div class="card">
          <h3>🧠 Ragionamento</h3>
          <div class="muted">Valuta opzioni e pianifica i passi successivi.</div>
          <ul>
            <li>Ragionamento e pianificazione</li>
            <li>Contesto e vincoli guidano le scelte</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )
with c3:
    st.markdown(
        """
        <div class="card">
          <h3>⚙️ Azione & Adattamento</h3>
          <div class="muted">Chiama tool, osserva risultati, si adatta.</div>
          <ul>
            <li>Recupera dati e compie azioni</li>
            <li>Adatta il piano al feedback</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

st.write("")

# ---------- Sezione: Automazioni vs Agenti ----------
st.markdown('<div class="section-title">Automazioni vs Agenti</div>', unsafe_allow_html=True)
st.markdown(
    """
    <table class="tbl">
      <thead>
        <tr><th>Aspetto</th><th>Automazione</th><th>Agente</th></tr>
      </thead>
      <tbody>
        <tr><td>Logica</td><td>Flusso fisso (if-then)</td><td>Ragionamento & pianificazione</td></tr>
        <tr><td>Obiettivo</td><td>Passi predefiniti</td><td>Goal con scelta dei passi</td></tr>
        <tr><td>Adattabilità</td><td>Bassa</td><td>Alta (si adatta al contesto)</td></tr>
        <tr><td>Strumenti</td><td>Sequenza rigida</td><td>Seleziona e combina</td></tr>
        <tr><td>Output</td><td>Predeterminato</td><td>Dipende dal contesto</td></tr>
      </tbody>
    </table>
    """,
    unsafe_allow_html=True,
)

st.caption("Regola pratica: se il percorso cambia al cambiare del contesto (per scelta del sistema), stai usando un **agente**, non solo un’automazione.")

st.write("")

# ---------- Sezione: Componenti ----------
st.markdown('<div class="section-title">Componenti di un Agente</div>', unsafe_allow_html=True)
a1, a2 = st.columns(2)
with a1:
    st.markdown(
        f"""
        <div class="card">
          <h3>🧠 Brain (LLM)</h3>
          <div class="muted">Il cervello che ragiona, pianifica e decide quali tool usare.</div>
          <ul>
            <li>Interpreta goal & vincoli</li>
            <li>Seleziona strategie/strumenti</li>
            <li>Guida il ciclo Reason → Plan → Act → Observe</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )
with a2:
    st.markdown(
        f"""
        <div class="card">
          <h3>🧾 Memory</h3>
          <div class="muted">Mantiene stato e contesto per non ripartire da zero.</div>
          <ul>
            <li>Storico conversazioni, preferenze</li>
            <li>Vector DB / store applicativo</li>
            <li>Contestualizza le decisioni future</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

b1, b2, b3 = st.columns(3)
with b1:
    st.markdown(
        """
        <div class="card">
          <h3>🔎 Tools — Recupero Dati</h3>
          <div class="muted">Informazioni affidabili pertinenti al goal.</div>
          <ul>
            <li>Web search / RAG documentale</li>
            <li>Query a database/API/KB</li>
            <li>Enrichment & fact-check</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )
with b2:
    st.markdown(
        """
        <div class="card">
          <h3>🛠 Tools — Azioni</h3>
          <div class="muted">Effetti reali fuori dal modello.</div>
          <ul>
            <li>Scrivere/salvare report</li>
            <li>Notifiche, ticket, integrazioni</li>
            <li>Chiamate API</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )
with b3:
    st.markdown(
        """
        <div class="card">
          <h3>🧭 Tools — Orchestrazione</h3>
          <div class="muted">Coordinare agenti e task.</div>
          <ul>
            <li>Pipeline e dipendenze</li>
            <li>Schedulazione ricorrente</li>
            <li>Fallback & retry</li>
          </ul>
        </div>
        """, unsafe_allow_html=True
    )

st.write("")
st.markdown(
    """
    <div class="cta">
      <h3>Vuoi provare l’agente sul tuo competitor?</h3>
      <p class="muted">Inserisci un nome e ottieni un executive brief con fonti affidabili.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.page_link("pages/try_the_agent.py", label="🚀 Apri la demo", icon="➡️")
st.markdown('<div class="footer">© 2025 Competitor News Agent · Dark Gold UI</div>', unsafe_allow_html=True)
