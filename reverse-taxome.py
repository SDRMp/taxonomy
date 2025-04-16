import streamlit as st
from graphviz import Digraph
import tempfile
from pathlib import Path

st.set_page_config(page_title="CSV to Flowchart", layout="wide")
st.title("🔁 CSV → Flowchart Diagram (HD Export)")

# Instructions
with st.expander("ℹ️ कैसे इस्तेमाल करें (How to Use)", expanded=False):
    st.markdown("""
    **इस ऐप के जरिए आप CSV डेटा से डायग्राम बना सकते हैं:**

    - CSV की लाइन को नीचे दिए गए फॉर्मेट में पेस्ट करें
    - डायग्राम प्रीव्यू देखें
    - और 600 DPI में हाई-क्वालिटी PNG डाउनलोड करें

    **Expected Format (Tab-separated):**  
    `Supernode` → `Subjects ($$)` → `Subtopics (@@)` → `Sub-subtopics (^^)`
    """)

# Input CSV Row
csv_input = st.text_area("📋 Paste your CSV row here:", value="Education\tSubject1 $$ Subject2\tTopic1 @@ Topic2 $$ Topic1 @@ Topic2\tSub1 ^^ Sub2 @@ Sub1 ^^ Sub2 $$ Sub1 ^^ Sub2 @@ Sub1 ^^ Sub2")

if csv_input:
    try:
        # Parse CSV Line
        parts = csv_input.strip().split("\t")
        super_node = parts[0].strip()
        level1_nodes = [s.strip() for s in parts[1].split("$$")]

        # Level-2
        level2_map = {}
        level2_groups = [grp.strip() for grp in parts[2].split("$$")]
        for i, group in enumerate(level2_groups):
            topics = [t.strip() for t in group.split("@@")]
            level2_map[level1_nodes[i]] = topics

        # Level-3
        level3_map = {}
        level3_groups = [grp.strip() for grp in parts[3].split("$$")]
        for i, group in enumerate(level3_groups):
            subsub_map = {}
            topics = level2_map.get(level1_nodes[i], [])
            topic_groups = [tg.strip() for tg in group.split("@@")]
            for j, topic in enumerate(topics):
                subs = topic_groups[j].split("^^") if j < len(topic_groups) else []
                subsub_map[topic] = [s.strip() for s in subs]
            level3_map[level1_nodes[i]] = subsub_map

        # Build Graph
        def generate_graph(super_node, level1_nodes, level2_map, level3_map):
            dot = Digraph(comment="Flowchart", format='png')
            dot.attr(dpi='600', rankdir='LR', size='10')
            dot.node(super_node, super_node, shape='box', style='filled', fillcolor='lightblue')

            for subject in level1_nodes:
                dot.node(subject, subject, shape='ellipse', style='filled', fillcolor='lightgreen')
                dot.edge(super_node, subject)

                for topic in level2_map.get(subject, []):
                    topic_id = f"{subject}_{topic}".replace(" ", "_")
                    dot.node(topic_id, topic, shape='note', style='filled', fillcolor='lightyellow')
                    dot.edge(subject, topic_id)

                    for sub in level3_map.get(subject, {}).get(topic, []):
                        sub_id = f"{topic_id}_{sub}".replace(" ", "_")
                        dot.node(sub_id, sub, shape='component', style='filled', fillcolor='mistyrose')
                        dot.edge(topic_id, sub_id)
            return dot

        dot = generate_graph(super_node, level1_nodes, level2_map, level3_map)

        # Show Flowchart in Streamlit
        st.subheader("📊 Flowchart Preview")
        st.graphviz_chart(dot.source)

        # Export HD PNG
        st.subheader("⬇️ Download High-Quality Diagram (600 DPI)")
        with tempfile.TemporaryDirectory() as tmpdirname:
            path = Path(tmpdirname) / "flowchart"
            dot.render(str(path), format="png", cleanup=True)
            with open(f"{path}.png", "rb") as f:
                st.download_button(
                    label="📥 Download HD Flowchart PNG",
                    data=f,
                    file_name="flowchart_hd.png",
                    mime="image/png"
                )

    except Exception as e:
        st.error(f"❌ Error parsing input: {e}")
