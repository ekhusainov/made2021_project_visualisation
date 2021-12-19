import ast
from random import sample
from math import floor

import networkx as nx
from networkx.algorithms.connectivity.kcutsets import all_node_cuts
import numpy as np
import pandas as pd


import matplotlib.pyplot as plt
from networkx.classes import graph
from pyvis.network import Network
import streamlit as st
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
# import plotly.figure_factory as ff
from plotly.tools import FigureFactory as ff
# import scipy
import altair as alt

FILEPATH_TO_SIMPLE_BASELINE = "data/simple_baseline.txt"
FILEPATH_TO_TJ_BASELINE = "data/G_tj_upd_upd.gml"
FILEPATH_TO_VC_BASELINE = "data/vc_posts.gml"
FILEPATH_TO_DTF_BASELINE = "data/dtf_posts2.gml"
FILEPATH_TO_TJ_SENTIMENT = "data/tj_sent_upd.csv"
FILEPATH_HTML_TO_TJ_BASELINE = "html/tj_baseline.html"
FILEPATH_HTML_TO_VC_BASELINE = "html/vc_baseline.html"
FILEPATH_HTML_TO_DTF_BASELINE = "html/dtf_baseline.html"
TJ_COMP_TOPIC = "data/tj_topics_upd.csv"
TJ_KEY_WORDS = "data/tj_keywords_upd.npy"
TJ_ADV_ATTR = "data/tj_upd_likes.csv"
MAX_WORD_IN_TITLE = 6
GRAPH_CLUSTERS = "Кластеры"
GRAPH_SENTIMENT = "Анализ тональности"
ALL_NODES = "Все ноды"
# ALL_NODES = "blizzard"


def statistic_graph(graph):
    edge_count = len(graph.edges())
    node_count = len(graph.nodes())
    st.sidebar.markdown(f"Количество нод: {node_count}")
    st.sidebar.markdown(f"Количество рёбер: {edge_count}")


def add_adv_attrs(node_selector):
    adv_attr_data = pd.read_csv(TJ_ADV_ATTR)
    adv_attr_data = adv_attr_data[adv_attr_data["companies"] == node_selector]
    comments_count = adv_attr_data["commentsCount"].item()
    hits_count = adv_attr_data["hitsCount"].item()
    likes = adv_attr_data["likes"].item()
    st.sidebar.markdown(f"Комментов в среднем:\n{comments_count}")
    st.sidebar.markdown(f"Посещений в среднем:\n{hits_count}")
    st.sidebar.markdown(f"Лайков в среднем:\n{likes}")


def int_to_hex_for_rgb(value):
    answer = str(hex(value))[2:]
    if len(answer) == 1:
        answer = "0" + answer
    return answer


def choose_node(node_selector, graph):
    init_sent_data = pd.read_csv(FILEPATH_TO_TJ_SENTIMENT)
    # print(node_selector)
    neutral_value = init_sent_data[init_sent_data["companies"]
                                   == node_selector]["neutral"].item()
    positive_value = init_sent_data[init_sent_data["companies"]
                                    == node_selector]["positive"].item()
    negative_value = init_sent_data[init_sent_data["companies"]
                                    == node_selector]["negative"].item()

    labels = ["neutral", "positive", "negative"]

    sizes_context = [neutral_value, positive_value, negative_value]
    # st.sidebar.markdown(repr(sizes_context))

    # chart_data = pd.DataFrame(
    #     np.array([
    #         [1, 0, 0],
    #         [0, 2, 0],
    #         [0, 0, 3],
    #     ]),
    #     columns=["a", "b", "c"],
    # )

    add_adv_attrs(node_selector)

    alt_data = pd.DataFrame({
        "a": labels[1:],
        "b": sizes_context[1:],
        "color": ["green", "red"],
    })
    st_alt_data = alt.Chart(alt_data).mark_bar().encode(
        x=alt.X("a", axis=alt.Axis(title="")),
        y=alt.X("b", axis=alt.Axis(title="")),
        color=alt.Color("color", scale=None),
    ).properties(
        title="Окрас",
    )
    st.sidebar.altair_chart(st_alt_data, use_container_width=True)

    # st.sidebar.bar_chart(chart_data)

    # explode = (0, 0.1, 0)

    # fig1, ax1 = plt.subplots()
    # ax1.pie(sizes_context, explode=explode, labels=labels, autopct='%1.1f%%',
    #         shadow=True, startangle=90, colors=["blue", "green", "red"])
    # ax1.axis('equal')
    # st.sidebar.pyplot(fig1)

    new_graph = nx.Graph()
    new_graph.add_node(node_selector)
    neighbors = [i for i in graph.neighbors(node_selector)]
    for key, value in graph.nodes[node_selector].items():
        new_graph.nodes[node_selector][key] = value
    for node_neighbor in neighbors:
        new_graph.add_node(node_neighbor)
        new_graph.add_edge(node_selector, node_neighbor)
        for key, value in graph.nodes[node_neighbor].items():
            new_graph.nodes[node_neighbor][key] = value

    return new_graph


def normalize_data(data):
    for column in ["negative", "positive", "neutral"]:
        data[column] = ((data[column] - data[column].mean()) /
                        data[column].std() + 1) / 2
        data[column] = data[column].apply(lambda x: min(x, 1))
        data[column] = data[column].apply(lambda x: max(x, 0))
    return data


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

    labels = "VC_posts", "TJ_posts", "DTF_posts", "VC_comments", "TJ_comments", "DTF_comments"
    sizes = [17, 10, 15, 4.9, 13, 16.3]
    explode = (0, 0.1, 0, 0, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    st.sidebar.markdown(f"Общий размер: {sum(sizes)} Гб")
    st.sidebar.pyplot(fig1)

    sizes_count = [199188, 298695, 472045, 113826, 264318, 293516]

    explode_count = (0, 0.1, 0, 0, 0, 0)

    fig1_count, ax1_count = plt.subplots()
    ax1_count.pie(sizes_count, explode=explode_count, labels=labels, autopct='%1.1f%%',
                  shadow=True, startangle=90)

    ax1_count.axis('equal')
    st.sidebar.markdown(f"Общие количество файлов: {sum(sizes_count)}")
    st.sidebar.pyplot(fig1_count)


def add_sentence(graph, sent_data):
    sent_data = normalize_data(sent_data)
    for node in graph.nodes():
        if node in list(sent_data["companies"]):
            neural = sent_data[sent_data["companies"] == node]["neutral"]
            negative = sent_data[sent_data["companies"]
                                 == node]["negative"]
            positive = sent_data[sent_data["companies"]
                                 == node]["positive"]
            try:
                new_red = floor(negative / (negative + positive) * 255)
                new_green = 255 - new_red
                new_blue = 0
                new_rgb_color = "#" + \
                    int_to_hex_for_rgb(
                        new_red) + int_to_hex_for_rgb(new_green) + int_to_hex_for_rgb(new_blue)
                graph.nodes[node]["color"] = new_rgb_color
            except ValueError:
                graph.nodes[node]["color"] = "#0000ff"
    return graph


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
    nx_graph.edges[4, 5]["color"] = "red"
    nx_graph.edges[4, 5]["alpha"] = 0.1
    nx_graph.edges[4, 5]["weight"] = 10
    nx_graph.nodes[10]["labelHighlightBold"] = True

    nt = Network("500px", "500px", notebook=True, heading="")
    nt.from_nx(nx_graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/simple_graph.html")


def tj_baseline(physics=False):
    choose_type = st.sidebar.selectbox(
        "Выберите тип графа",
        (
            GRAPH_CLUSTERS,
            GRAPH_SENTIMENT,
        )
    )
    graph = nx.read_gml(FILEPATH_TO_TJ_BASELINE)
    #
    comp = pd.read_csv(TJ_COMP_TOPIC)
    key_word = np.load(TJ_KEY_WORDS)
    for node in graph.nodes():
        if node not in list(comp["companies"]):
            continue
        graph.nodes[node]["font_size"] = 80
        current_dict = ast.literal_eval(
            list(comp[comp["companies"] == node]["probs_sort"].items())[0][1])
        try:
            del current_dict["others"]
        except KeyError:
            pass
        better_key = max(current_dict.items(), key=lambda x: x[1])[0]
        try:
            title = list(key_word[better_key])
            # title = sample(title, MAX_WORD_IN_TITLE)
            title = repr(title)
            graph.nodes[node]["title"] = title
        except IndexError:
            pass
    #
    for node in graph.nodes():
        # graph.nodes[node]["size"] = max(
        #     5, graph.nodes[node]["adjusted_node_size"] / 5)
        graph.nodes[node]["size"] = graph.nodes[node]["adjusted_node_size"]
        # graph.nodes[node]["color"] = graph.nodes[node]["modularity_color"]

    sent_data = pd.read_csv(FILEPATH_TO_TJ_SENTIMENT)
    if choose_type == GRAPH_SENTIMENT:
        graph = add_sentence(graph, sent_data)
    elif choose_type == GRAPH_CLUSTERS:
        for node in graph.nodes():
            graph.nodes[node]["color"] = graph.nodes[node]["modularity_color"]

    statistic_graph(graph)
    node_selector = st.sidebar.selectbox(
        "Выберите ноду",
        [ALL_NODES] + list(comp["companies"])
    )

    if node_selector != ALL_NODES:
        graph = choose_node(node_selector, graph)
    # graph = choose_node(node_selector, graph)

    for edge in graph.edges():
        graph.edges[edge]["color"] = "#B2B2B2"

    nt = Network("800px", "800px", notebook=True, heading="TJournal")
    nt.barnes_hut()
    nt.from_nx(graph)
    if node_selector != ALL_NODES:
        nt.hrepulsion(central_gravity=5)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/tj_baseline.html")

    # current_dict = ast.literal_eval(
    #     list(comp[comp["companies"] == node_selector]["probs"].items())[0][1])
    # st.title(repr(current_dict))
    # fig = px.bar(
    #     list(current_dict.values()),
    #     # hovertemplate=key_word[list(current_dict.keys())],
    #     # labels=["1", "2"]
    #     hoverlabel = key_word[list(current_dict.keys())]
    # )
    # hover_data = key_word[list(current_dict.keys())]
    # fig.update_traces(hovertemplate=None)

    # # fig.update_layout(hovertemplate="")
    # st.plotly_chart(fig)
    main_statistic()


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
