import streamlit as st
from graphviz import Digraph

st.set_page_config(page_title="CSV to Flowchart", layout="wide")
st.title("🔁 CSV → Flowchart")

st.markdown("Upload or paste a CSV-style row (single line) below:")

input_csv = st.text_area("📋 Paste your CSV row here:", height=150,
                         value="Education\tSubject1 $$ Subject2\tTopic1 @@ Topic2 $$ Topic1 @@ Topic2\tSub1 ^^ Sub2 @@ Sub1 ^^ Sub2 $$ Sub1 ^^ Sub2 @@ Sub1 ^^ Sub2")

dpi = st.slider("🖨️ Export DPI (higher = better quality)", min_value=100, max_value=600, value=300, step=50)

if st.button("📊 Generate Flowchart"):
    try:
        # Parse the CSV line
        parts = input_csv.strip().split("\t")
        if len(parts) != 4:
            st.error("CSV row must have exactly 4 tab-separated fields: Super-node, Level1, Level2, Level3")
        else:
            super_node = parts[0]
            level1_nodes = parts[1].split(" $$ ")

            level2_raw = parts[2].split(" $$ ")
            level2_map = {}
            for idx, subject in enumerate(level1_nodes):
                subtopics = level2_raw[idx].split(" @@ ") if idx < len(level2_raw) else []
                level2_map[subject] = subtopics

            level3_raw = parts[3].split(" $$ ")
            level3_map = {}
            for idx, subject in enumerate(level1_nodes):
                topic_map = {}
                if idx < len(level3_raw):
                    topic_chunks = level3_raw[idx].split(" @@ ")
                    subtopics = level2_map.get(subject, [])
                    for j, topic in enumerate(subtopics):
                        subs = topic_chunks[j].split(" ^^ ") if j < len(topic_chunks) else []
                        topic_map[topic] = subs
                level3_map[subject] = topic_map

            # Generate the flowchart
            def generate_graph(super_node, level1_nodes, level2_map, level3_map, display_mode=False):
                dot = Digraph(comment="Flowchart", format='png')
                dot.attr(dpi=str(dpi))
                
                if display_mode:
                    # Smaller display settings
                    dot.attr(rankdir='LR', size='0.1', ratio='compress')
                    dot.attr(nodesep='0.2', ranksep='0.3')
                    fontsize = '10'
                else:
                    # HD export settings
                    dot.attr(rankdir='LR', size='10')
                    fontsize = '14'
                
                dot.node(super_node, super_node, shape='box', style='filled', fillcolor='lightblue', fontsize=fontsize)

                for subject in level1_nodes:
                    dot.node(subject, subject, shape='ellipse', style='filled', fillcolor='lightgreen', fontsize=fontsize)
                    dot.edge(super_node, subject)

                    subtopics = level2_map.get(subject, [])
                    for topic in subtopics:
                        topic_id = f"{subject}_{topic}".replace(" ", "_")
                        dot.node(topic_id, topic, shape='note', style='filled', fillcolor='lightyellow', fontsize=fontsize)
                        dot.edge(subject, topic_id)

                        sub_subs = level3_map.get(subject, {}).get(topic, [])
                        for sub in sub_subs:
                            sub_id = f"{topic_id}_{sub}".replace(" ", "_")
                            dot.node(sub_id, sub, shape='component', style='filled', fillcolor='mistyrose', fontsize=fontsize)
                            dot.edge(topic_id, sub_id)
                return dot

            # Display smaller version
            small_flowchart = generate_graph(super_node, level1_nodes, level2_map, level3_map, display_mode=True)
            st.graphviz_chart(small_flowchart.source, use_container_width=True)

            # Generate HD version for download
            hd_flowchart = generate_graph(super_node, level1_nodes, level2_map, level3_map)
            
            # Save to file
            output_path = "/tmp/flowchart_hd"
            hd_flowchart.render(output_path, cleanup=True)
            with open(f"{output_path}.png", "rb") as f:
                st.download_button("⬇️ Download HD Flowchart (PNG)", data=f, file_name="flowchart_hd.png", mime="image/png")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
