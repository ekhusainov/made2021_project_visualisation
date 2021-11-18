import networkx as nx

import matplotlib.pyplot as plt
from pyvis.network import Network
import streamlit as st

FILEPATH_TO_SIMPLE_BASELINE = "data/simple_baseline.txt"


def simple_graph(physics):
    nx_graph = nx.cycle_graph(20)
    nx_graph.nodes[1]["title"] = "Number 1"
    nx_graph.nodes[1]["group"] = 1
    nx_graph.nodes[3]["title"] = "I belong to a different group!"
    nx_graph.nodes[3]["group"] = 10
    nx_graph.add_node(20, size=20, title="couple", group=2)
    nx_graph.add_node(21, size=15, title="couple", group=2)
    nx_graph.add_edge(20, 21, weight=5)
    nx_graph.add_node(25, size=25, label="lonely",
                      title="lonely node", group=3)

    nt = Network("500px", "500px", notebook=True, heading="")
    nt.from_nx(nx_graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/simple_graph.html")


def simple_baseline(physics):
    graph = nx.read_weighted_edgelist(FILEPATH_TO_SIMPLE_BASELINE, encoding="utf-8")
    nt = Network("800px","800px", notebook=True, heading="Simple baseline")
    nt.from_nx(graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/simple_baseline.html")