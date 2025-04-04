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
level3_map = {}

# Step 2: Level 1 Nodes and Subtopics
for i in range(level1_count):
    with st.expander(f"Level-1 Node {i + 1}", expanded=True):
        subject = st.text_input(f"Subject name #{i + 1}", key=f"subject_{i}")
        level1_nodes.append(subject)

        level2_count = st.number_input(f"How many subtopics for '{subject}'?", min_value=0, max_value=10, value=0, key=f"count_{i}")
        subtopics = []
        sub_subtopics_map = {}
        for j in range(level2_count):
            topic = st.text_input(f"Subtopic #{j + 1} under {subject}", key=f"sub_{i}_{j}")
            subtopics.append(topic)

            level3_count = st.number_input(f"How many sub-subtopics for '{topic}'?", min_value=0, max_value=10, value=0, key=f"count_{i}_{j}")
            sub_subtopics = []
            for k in range(level3_count):
                sub_topic = st.text_input(f"Sub-subtopic #{k + 1} under {topic}", key=f"sub_{i}_{j}_{k}")
                sub_subtopics.append(sub_topic)
            sub_subtopics_map[topic] = sub_subtopics

        level2_map[subject] = subtopics
        level3_map[subject] = sub_subtopics_map

# Step 3: Preview Structure
st.subheader("📄 Preview CSV Data Structure")

child_level_1_str = " $$ ".join(level1_nodes)
child_level_2_parts = []
child_level_3_parts = []

for subject in level1_nodes:
    subtopics = level2_map.get(subject, [])
    subtopic_strs = []
    subsubtopic_strs = []
    if subtopics:
        for topic in subtopics:
            subtopic_strs.append(topic)
            sub_subs = level3_map[subject].get(topic, [])
            if sub_subs:
                subsubtopic_strs.append(" ## ".join(sub_subs))
            else:
                subsubtopic_strs.append("null")
    else:
        subtopic_strs.append("null")
        subsubtopic_strs.append("null")

    child_level_2_parts.append(" @@ ".join(subtopic_strs))
    child_level_3_parts.append(" @@ ".join(subsubtopic_strs))

child_level_2_str = " $$ ".join(child_level_2_parts)
child_level_3_str = " $$ ".join(child_level_3_parts)

csv_content = f"{super_node}\t{child_level_1_str}\t{child_level_2_str}\t{child_level_3_str}"
st.code(csv_content, language="text")

# Step 4: Download CSV
st.subheader("⬇️ Download CSV")
csv_data = csv_content.encode('utf-8')
st.download_button("Download CSV", data=csv_data, file_name="flowchart.csv", mime="text/csv")

# Step 5: Flowchart Visualization
st.subheader("📊 Flowchart Preview")

def generate_flowchart(super_node, level1_nodes, level2_map, level3_map):
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

            sub_subtopics = level3_map.get(subject, {}).get(topic, [])
            for sub_sub in sub_subtopics:
                sub_id = f"{topic_id}_{sub_sub}".replace(" ", "_")
                dot.node(sub_id, sub_sub, shape='component', style='filled', fillcolor='mistyrose')
                dot.edge(topic_id, sub_id)

    return dot

flowchart = generate_flowchart(super_node, level1_nodes, level2_map, level3_map)
st.graphviz_chart(flowchart.source)
