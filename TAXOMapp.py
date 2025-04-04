import streamlit as st
import pandas as pd

st.set_page_config(page_title="Flowchart Builder to CSV", layout="wide")
st.title("🛠️ Flowchart Builder → CSV Exporter")

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
st.subheader("📄 Preview Structure")

# Handle custom formatting:
child_level_1_str = " $$ ".join(level1_nodes)
child_level_2_parts = []
for subject in level1_nodes:
    subtopics = level2_map.get(subject, [])
    if subtopics:
        child_level_2_parts.append(" @@ ".join(subtopics))
    else:
        child_level_2_parts.append("")  # No subtopics for this subject
child_level_2_str = " $$ ".join(child_level_2_parts)

# Show final string
st.code(f"{super_node}\t{child_level_1_str}\t{child_level_2_str}", language="text")

# Step 4: Export to CSV
st.subheader("⬇️ Download CSV")

def generate_csv_content():
    return f"{super_node}\t{child_level_1_str}\t{child_level_2_str}"

csv_data = generate_csv_content().encode('utf-8')
st.download_button("Download CSV", data=csv_data, file_name="flowchart.csv", mime="text/csv")
