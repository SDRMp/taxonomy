import streamlit as st
from graphviz import Digraph
import tempfile
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="CSV to Flowchart", layout="wide")
st.title("🔁 CSV → Flowchart Diagram (HD Export)")

# Instructions
with st.expander("ℹ️ कैसे इस्तेमाल करें (How to Use)", expanded=False):
    st.markdown("""
    **इस ऐप के जरिए आप CSV डेटा से डायग्राम बना सकते हैं:**

    - CSV की लाइन को नीचे दिए गए फॉर्मेट में पेस्ट करें
    - सिर्फ एक छोटा प्रीव्यू देखें
    - और 600 DPI में हाई-क्वालिटी PNG डाउनलोड करें

    **Expected Format (Tab-separated):**  
    `Supernode` → `Subjects ($$)` → `Subtopics (@@)` → `Sub-subtopics (^^)`
    """)

csv_input = st.text_area(
    "📋 Paste your CSV row here:",
    value="Education\tSubject1 $$ Subject2\t @@ Topic2 $$ Topic1 @@ Topic2\t @@ Sub1 ^^ Sub2 $$ Sub1 ^^ Sub2 @@ Sub1 ^^ Sub2"
)

if csv_input:
    try:
        parts = csv_input.strip().split("\t")
        super_node = parts[0].strip()

        # Level‑1
        level1 = [s.strip() for s in parts[1].split("$$")]

        # Level‑2
        level2_map = {}
        for i, grp in enumerate(parts[2].split("$$")):
            subj = level1[i] if i < len(level1) else None
            if subj:
                level2_map[subj] = [t.strip() for t in grp.split("@@")]

        # Level‑3
        level3_map = {}
        for i, grp in enumerate(parts[3].split("$$")):
            subj = level1[i] if i < len(level1) else None
            if subj:
                topics = level2_map.get(subj, [])
                topic_groups = grp.split("@@")
                submap = {}
                for j, topic in enumerate(topics):
                    subs = []
                    if j < len(topic_groups):
                        subs = [s.strip() for s in topic_groups[j].split("^^")]
                    submap[topic] = subs
                level3_map[subj] = submap

        def generate_graph(super_node, level1, level2, level3):
            dot = Digraph(format="png")
            dot.attr(dpi="600", rankdir="LR", size="10")
            dot.node(super_node, super_node, shape="box", style="filled", fillcolor="lightblue")

            for subj in level1:
                if not subj:
                    continue
                dot.node(subj, subj, shape="ellipse", style="filled", fillcolor="lightgreen")
                dot.edge(super_node, subj)

                for topic in level2.get(subj, []):
                    if not topic:
                        # break here: no node, no downstream
                        continue
                    tid = f"{subj}_{topic}".replace(" ", "_")
                    dot.node(tid, topic, shape="note", style="filled", fillcolor="lightyellow")
                    dot.edge(subj, tid)

                    for sub in level3.get(subj, {}).get(topic, []):
                        if not sub:
                            continue
                        sid = f"{tid}_{sub}".replace(" ", "_")
                        dot.node(sid, sub, shape="component", style="filled", fillcolor="mistyrose")
                        dot.edge(tid, sid)

            return dot

        dot = generate_graph(super_node, level1, level2_map, level3_map)

        # Render & Preview
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "flowchart"
            dot.render(str(p), cleanup=True)

            st.subheader("🖼️ Preview (Thumbnail)")
            img = Image.open(f"{p}.png")
            st.image(img, width=300)

            st.subheader("⬇️ Download HD PNG (600 DPI)")
            with open(f"{p}.png", "rb") as f:
                st.download_button("📥 Download", f, "flowchart_hd.png", "image/png")

    except Exception as e:
        st.error(f"❌ Parsing error: {e}")
