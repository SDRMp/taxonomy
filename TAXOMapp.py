import streamlit as st
import pandas as pd
from graphviz import Digraph

st.set_page_config(page_title="Flowchart Builder to CSV", layout="wide")
st.title("🛠️ Flowchart Builder → CSV + Diagram")

# Hindi Instructions
with st.expander("ℹ️ यह ऐप कैसे काम करता है? (How does this app work?)", expanded=False):
    st.markdown("""
    **यह ऐप एक Flowchart और CSV structure बनाने के लिए है:**
    
    - Super-node (मुख्य विषय) दर्ज करें
    - Subjects (Level-1), उनके Subtopics (Level-2), और Sub-subtopics (Level-3) जोड़ें
    - फिर उस hierarchy को एक custom format में CSV के रूप में डाउनलोड करें
    - और उसका डायग्राम (Flowchart) भी देखें

    **Delimiters का उपयोग:**
    - `$$` → अलग-अलग Subjects (Level-1) को अलग करता है
    - `@@` → Subtopics को अलग करता है
    - `^^` → Sub-subtopics को उनके parent से जोड़ता है
    """)

# Input Section
super_node = st.text_input("🧠 Super-node (main theme)", value="Education")

st.subheader("📘 Subjects (Level-1 Nodes)")
level1_count = st.number_input("कितने subjects जोड़ने हैं?", min_value=1, max_value=10, value=2)

level1_nodes = []
level2_map = {}
level3_map = {}

for i in range(level1_count):
    with st.expander(f"📚 Subject #{i + 1}", expanded=True):
        default_subject = "Mathematics" if i == 0 else "Physics"
        subject = st.text_input(f"Subject Name:", value=default_subject, key=f"subject_{i}")
        level1_nodes.append(subject)

        level2_count = st.number_input(f"Subtopics for '{subject}'", min_value=0, max_value=10, value=2, key=f"sub_count_{i}")
        subtopics = []
        subsub_map = {}

        for j in range(level2_count):
            default_topic = "Algebra" if subject == "Mathematics" and j == 0 else "Motion"
            topic = st.text_input(f"Subtopic #{j + 1}", value=default_topic, key=f"sub_{i}_{j}")
            subtopics.append(topic)

            level3_count = st.number_input(f"Sub-subtopics for '{topic}'", min_value=0, max_value=10, value=2, key=f"subsub_count_{i}_{j}")
            sub_subs = []

            for k in range(level3_count):
                default_sub = "Linear" if j == 0 and k == 0 else "Quadratic"
                sub_topic = st.text_input(f"Sub-subtopic #{k + 1}", value=default_sub, key=f"subsub_{i}_{j}_{k}")
                sub_subs.append(sub_topic)

            subsub_map[topic] = sub_subs

        level2_map[subject] = subtopics
        level3_map[subject] = subsub_map

# CSV Builder Section
st.subheader("📄 Structured CSV Format with Delimiters")

csv_rows = []

for subject in level1_nodes:
    subtopics = level2_map.get(subject, [])
    subtopic_strs = []
    subsub_strs = []

    for topic in subtopics:
        subtopic_strs.append(topic if topic else "null")
        sub_subs = level3_map.get(subject, {}).get(topic, [])
        if sub_subs:
            subsub_strs.append(" ^^ ".join(sub_subs))
        else:
            subsub_strs.append("null")

    row = [
        super_node,
        subject,
        " @@ ".join(subtopic_strs) if subtopic_strs else "null",
        " @@ ".join(subsub_strs) if subsub_strs else "null"
    ]
    csv_rows.append(row)

# Convert to text
csv_text_rows = ["\t".join(row) for row in csv_rows]
csv_output = "\n".join(csv_text_rows)
st.code(csv_output, language="text")

# Download
st.download_button("⬇️ Download CSV", data=csv_output.encode('utf-8'), file_name="structured_flowchart.csv", mime="text/csv")

# Graphviz Chart
st.subheader("📊 Flowchart Preview")

def generate_graph(super_node, level1_nodes, level2_map, level3_map):
    dot = Digraph(comment="Flowchart", format='png')
    dot.attr(rankdir='LR', size='10')
    dot.node(super_node, super_node, shape='box', style='filled', fillcolor='lightblue')

    for subject in level1_nodes:
        dot.node(subject, subject, shape='ellipse', style='filled', fillcolor='lightgreen')
        dot.edge(super_node, subject)

        subtopics = level2_map.get(subject, [])
        for topic in subtopics:
            topic_id = f"{subject}_{topic}".replace(" ", "_")
            dot.node(topic_id, topic, shape='note', style='filled', fillcolor='lightyellow')
            dot.edge(subject, topic_id)

            sub_subs = level3_map.get(subject, {}).get(topic, [])
            for sub in sub_subs:
                sub_id = f"{topic_id}_{sub}".replace(" ", "_")
                dot.node(sub_id, sub, shape='component', style='filled', fillcolor='mistyrose')
                dot.edge(topic_id, sub_id)

    return dot

flowchart = generate_graph(super_node, level1_nodes, level2_map, level3_map)
st.graphviz_chart(flowchart.source)
