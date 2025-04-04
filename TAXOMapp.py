import streamlit as st
import pandas as pd
from graphviz import Digraph

st.set_page_config(page_title="Flowchart Builder to CSV", layout="wide")
st.title("🛠️ Flowchart Builder → CSV + Diagram")

# Step 1: Super Node
super_node = st.text_input("Enter the Super-node (main category)", value="science")

st.subheader("Level 1 Nodes (Subjects)")
level1_count = st.number_input("How many Level-1 nodes do you want to add?", min_value=1, max_value=10, value=4)
level1_nodes = []
level2_map = {}

# Step 2: Level 1 Nodes and Subtopics
for i in range(level1_count):
    with st.expander(f"Level-1 Node {i + 1}", expanded=True):
        subject = st.text_input(f"Subject name #{i + 1}", key=f"subject_{i}")
        level1_nodes.append(subject)

        level2_count = st.number_input(f"How many subtopics for '{subject}'?", min_value=0, max_value=10, value=0, key=f"count_{i}")
        subtopics = []
        for j in range(level2_count):
            topic = st.text_input(f"Subtopic #{j + 1} under {subject}", key=f"sub_{i}_{j}")
            subtopics.append(topic)
        level2_map[subject] = subtopics

# Step 3: Preview Structure
st.subheader("📄 Preview CSV Data Structure")

child_level_1_str = " $$ ".join(level1_nodes)
child_level_2_parts = []
for subject in level1_nodes:
    subtopics = level2_map.get(subject, [])
    if subtopics:
        child_level_2_parts.append(" @@ ".join(subtopics))
    else:
        child_level_2_parts.append("")  # No subtopics for this subject
child_level_2_str = " $$ ".join(child_level_2_parts)

csv_content = f"{super_node}\t{child_level_1_str}\t{child_level_2_str}"
st.code(csv_content, language="text")

# Step 4: Download CSV
st.subheader("⬇️ Download CSV")
csv_data = csv_content.encode('utf-8')
st.download_button("Download CSV", data=csv_data, file_name="flowchart.csv", mime="text/csv")

# Step 5: Flowchart Visualization
st.subheader("📊 Flowchart Preview")

def generate_flowchart(super_node, level1_nodes, level2_map):
    dot = Digraph(comment="Flowchart", format='png')
    dot.attr(rankdir='LR', size='10')

    dot.node(super_node, super_node, shape='box', style='filled', fillcolor='lightblue')

    for subject in level1_nodes:
        dot.node(subject, subject, shape='ellipse', style='filled', fillcolor='lightgreen')
        dot.edge(super_node, subject)

        subtopics = level2_map.get(subject, [])
        for topic in subtopics:
            node_id = f"{subject}_{topic}".replace(" ", "_")
            dot.node(node_id, topic, shape='note', style='filled', fillcolor='lightyellow')
            dot.edge(subject, node_id)

    return dot

flowchart = generate_flowchart(super_node, level1_nodes, level2_map)
st.graphviz_chart(flowchart.source)
