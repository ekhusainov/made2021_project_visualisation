import ast
from random import sample

import networkx as nx
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from networkx.classes import graph
from pyvis.network import Network
import streamlit as st
import matplotlib.pyplot as plt


FILEPATH_TO_SIMPLE_BASELINE = "data/simple_baseline.txt"
FILEPATH_TO_TJ_BASELINE = "data/tj_baseline.gml"
FILEPATH_TO_VC_BASELINE = "data/vc_posts.gml"
FILEPATH_TO_DTF_BASELINE = "data/dtf_posts2.gml"
FILEPATH_HTML_TO_TJ_BASELINE = "html/tj_baseline.html"
FILEPATH_HTML_TO_VC_BASELINE = "html/vc_baseline.html"
FILEPATH_HTML_TO_DTF_BASELINE = "html/dtf_baseline.html"
COMP_TOPIC = "data/comp_topic_.csv"
KEY_WORDS = "data/keywords_.npy"
MAX_WORD_IN_TITLE = 6

def statistic_graph(graph):
    edge_count = len(graph.edges())
    node_count = len(graph.nodes())
    st.sidebar.markdown(f"Количество нод: {node_count}")
    st.sidebar.markdown(f"Количество рёбер: {edge_count}")


def main_statistic():
    st.sidebar.markdown("***")
    st.sidebar.markdown("**Общая информация о данных.**")
    info_about = pd.DataFrame(
        np.array([[
            17,
            10,
            15,
        ]]),
        columns=[
            "VC",
            "TJ",
            "DTF",
        ]
    )
    # info_about = np.array([1, 2, 3])
    # st.sidebar.bar_chart(info_about)

    labels = "VC_posts", "TJ_posts", "DTF_posts", "VC_comments", "TJ_comments", "DTF_comments"
    sizes = [17, 10, 15, 4.9, 13, 16.3]
    explode = (0, 0.1, 0, 0, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    st.sidebar.markdown(f"Общий размер: {sum(sizes)} Гб")
    st.sidebar.pyplot(fig1)

    # labels = "VC_posts", "TJ_posts", "DTF_posts", "VC_comments", "TJ_comments", "DTF_comments"
    sizes_count = [199188, 298695, 472045, 113826, 264318, 293516]
    # only "explode" the 2nd slice (i.e. 'Hogs')
    explode_count = (0, 0.1, 0, 0, 0, 0)

    fig1_count, ax1_count = plt.subplots()
    ax1_count.pie(sizes_count, explode=explode_count, labels=labels, autopct='%1.1f%%',
                  shadow=True, startangle=90)
    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1_count.axis('equal')
    st.sidebar.markdown(f"Общие количество файлов: {sum(sizes_count)}")
    st.sidebar.pyplot(fig1_count)

    # st.sidebar.pyplot(info_about)


def simple_graph(physics=False):
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


def tj_baseline(physics=False):
    graph = nx.read_gml(FILEPATH_TO_TJ_BASELINE)
    #
    comp = pd.read_csv(COMP_TOPIC)
    key_word = np.load(KEY_WORDS)
    for node in graph.nodes():
        if node not in list(comp["companies"]):
            continue

        current_dict = ast.literal_eval(
            list(comp[comp["companies"] == node]["probs"].items())[0][1])
        better_key = max(current_dict.items(), key=lambda x: x[1])[0]
        title = list(key_word[better_key])
        title = sample(title, MAX_WORD_IN_TITLE)
        title = repr(title)
        graph.nodes[node]["title"] = title
    #
    for node in graph.nodes():
        # graph.nodes[node]["size"] = max(
        #     5, graph.nodes[node]["adjusted_node_size"] / 5)
        graph.nodes[node]["size"] = graph.nodes[node]["adjusted_node_size"]
        graph.nodes[node]["color"] = graph.nodes[node]["modularity_color"]
    statistic_graph(graph)
    main_statistic()
    nt = Network("800px", "800px", notebook=True, heading="TJ baseline")
    nt.barnes_hut()
    nt.from_nx(graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/tj_baseline.html")


def vc_baseline(physics=False):
    graph = nx.read_gml(FILEPATH_TO_VC_BASELINE)
    statistic_graph(graph)
    main_statistic()
    nt = Network("800px", "800px", notebook=True, heading="VC baseline")
    nt.barnes_hut()
    nt.from_nx(graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/vc_baseline.html")


def dtf_baseline(physics=False):
    graph = nx.read_gml(FILEPATH_TO_DTF_BASELINE)
    statistic_graph(graph)
    main_statistic()
    nt = Network("800px", "800px", notebook=True, heading="DTF baseline")
    nt.barnes_hut()
    nt.from_nx(graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show(FILEPATH_HTML_TO_DTF_BASELINE)
