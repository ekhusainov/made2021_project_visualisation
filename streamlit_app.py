"""
MADE2021. Final project.
"""

from graphs import (
    simple_graph,
    tj_baseline,
    vc_baseline,
    dtf_baseline,
)
import streamlit.components.v1 as components
import streamlit as st

import networkx as nx

FILEPATH_HTML_TO_SIMPLE_GRAPH = "html/simple_graph.html"
FILEPATH_HTML_TO_SIMPLE_BASELINE = "html/simple_baseline.html"
FILEPATH_HTML_TO_TJ_BASELINE = "html/tj_baseline.html"
FILEPATH_HTML_TO_VC_BASELINE = "html/vc_baseline.html"
FILEPATH_HTML_TO_DTF_BASELINE = "html/dtf_baseline.html"
FILEPATH_TO_SIMPLE_BASELINE = "data/simple_baseline.txt"
FILEPATH_TO_TJ_BASELINE = "data/tj_baseline.gml"
FILEPATH_TO_VC_BASELINE = "data/vc_posts.gml"
FILEPATH_TO_DTF_BASELINE = "data/dtf_posts2.gml"
SIMPLE_EXAMPLE = "Simple example"
SIMPLE_BASELINE = "Simple baseline"
TJ_BASELINE = "TJ baseline"
VC_BASELINE = "VC baseline"
DTF_BASELINE = "DTF baseline"


def main():
    st.title("Альфа версия")
    choose_graph = st.sidebar.selectbox(
        "Choose graph",
        (
            TJ_BASELINE,
            VC_BASELINE,
            DTF_BASELINE,
            SIMPLE_EXAMPLE,
        )
    )
    # physics = st.sidebar.checkbox("add physics interactivity?")

    if choose_graph == SIMPLE_EXAMPLE:
        simple_graph()
        with open(FILEPATH_HTML_TO_SIMPLE_GRAPH, "r") as file:
            source_code = file.read()
        components.html(source_code, height=900, width=900)

    elif choose_graph == VC_BASELINE:
        vc_baseline()
        with open(FILEPATH_HTML_TO_VC_BASELINE, "r", encoding="utf-8") as file:
            source_code = file.read()
        components.html(source_code, height=900, width=900)

    elif choose_graph == TJ_BASELINE:
        tj_baseline()
        with open(FILEPATH_HTML_TO_TJ_BASELINE, "r", encoding="utf-8") as file:
            source_code = file.read()
        components.html(source_code, height=900, width=900)

    elif choose_graph == DTF_BASELINE:
        dtf_baseline()
        with open(FILEPATH_HTML_TO_DTF_BASELINE, "r", encoding="utf-8") as file:
            source_code = file.read()
        components.html(source_code, height=900, width=900)


if __name__ == "__main__":
    main()
