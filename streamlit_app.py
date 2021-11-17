"""
MADE2021. Final project.
"""

from graphs import simple_graph
import streamlit.components.v1 as components
import streamlit as st
FILEPATH_TO_SIMPLE_GRAPH = "html/simple_graph.html"


def main():
    st.title("Simple example.")
    physics = st.sidebar.checkbox("add physics interactivity?")
    simple_graph(physics)
    with open(FILEPATH_TO_SIMPLE_GRAPH, "r") as file:
        source_code = file.read()
    components.html(source_code, height=900, width=900)


if __name__ == "__main__":
    main()
