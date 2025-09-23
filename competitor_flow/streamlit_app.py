# streamlit_app.py
from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# --- import path: aggiunge ./src ---
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from competitor_flow.crews.competitor_crew.competitor_crew import CompetitorCrew  # noqa: E402

st.set_page_config(page_title="Competitor News Agent", layout="centered")
st.title("🏁 Competitor News Agent")

competitor = st.text_input("Competitor", value="Deloitte")
run = st.button("Generate report")

def _parse_json(text: str):
    text = text.strip()
    if not (text.startswith("{") or text.startswith("[")):
        start = text.find("{")
        if start != -1:
            text = text[start:]
        end = text.rfind("}")
        if end != -1:
            text = text[:end+1]
    return json.loads(text)

def _to_markdown(data: dict) -> str:
    lines = []
    lines.append("# Executive Summary\n")
    lines.append((data.get("executive_summary") or "").strip() + "\n")

    def section(title, items):
        lines.append(f"## {title}\n")
        for it in items or []:
            lines.append(f"- {it}")
        lines.append("")

    section("Key Takeaways", data.get("key_takeaways"))
    section("Risks", data.get("risks"))
    section("Opportunities", data.get("opportunities"))

    table = data.get("news_table", [])
    if table:
        lines.append("## Sources\n")
        header = table[0] if all(isinstance(c, str) for c in table[0]) else ["Title","Date","Source","URL"]
        rows = table[1:] if header == table[0] else table
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"]*len(header)) + " |")
        for r in rows:
            lines.append("| " + " | ".join(str(c or "") for c in r) + " |")
        lines.append("")
    return "\n".join(lines)

if run:
    if not competitor.strip():
        st.warning("Please enter a competitor.")
        st.stop()

    with st.spinner("Generating report…"):
        result = CompetitorCrew().crew().kickoff(inputs={"competitor": competitor})
        raw = str(getattr(result, "raw", result))

    try:
        data = _parse_json(raw)
    except Exception:
        st.error("Could not parse JSON from agent output.")
        st.code(raw)
        st.stop()

    st.subheader("Executive Summary")
    st.write(data.get("executive_summary", ""))

    cols = st.columns(3)
    with cols[0]:
        st.subheader("Key Takeaways")
        for x in data.get("key_takeaways", []):
            st.write(f"- {x}")
    with cols[1]:
        st.subheader("Risks")
        for x in data.get("risks", []):
            st.write(f"- {x}")
    with cols[2]:
        st.subheader("Opportunities")
        for x in data.get("opportunities", []):
            st.write(f"- {x}")

    st.subheader("Sources")
    table = data.get("news_table", [])
    if table:
        header = table[0] if all(isinstance(c, str) for c in table[0]) else ["Title","Date","Source","URL"]
        rows = table[1:] if header == table[0] else table
        df = pd.DataFrame(rows, columns=header)
        if "URL" in df.columns:
            df["URL"] = df["URL"].apply(lambda u: f"[link]({u})" if isinstance(u, str) else u)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sources table provided.")

    st.divider()
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("⬇️ Download JSON", data=json_bytes,
                       file_name=f"{competitor.lower()}_brief.json", mime="application/json")

    md_text = _to_markdown(data)
    st.download_button("⬇️ Download Markdown", data=md_text.encode("utf-8"),
                       file_name=f"{competitor.lower()}_brief.md", mime="text/markdown")
