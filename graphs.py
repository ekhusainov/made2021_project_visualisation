import ast
from random import sample
from math import floor, sqrt
from itertools import combinations

from altair.vegalite.v4.api import layer

import networkx as nx
from networkx.algorithms.connectivity.kcutsets import all_node_cuts
from networkx.classes.function import neighbors
from networkx.readwrite import gpickle
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
FILEPATH_TO_DTF_GRAPH = "data/dtf_filtered_graph_with_sent_without_likes.gml"
TJ_COMP_TOPIC = "data/tj_topics_upd.csv"
TJ_KEY_WORDS = "data/tj_keywords_upd.npy"
TJ_ADV_ATTR = "data/tj_upd_likes.csv"
MAX_WORD_IN_TITLE = 6
GRAPH_CLUSTERS = "Кластеры"
GRAPH_SENTIMENT = "Анализ тональности"
ALL_NODES = "Все ноды"
PLUS_MINUS = u"\u00B1"
FILEPATH_TO_VC_GRAPH = "data/G_vc_upd_upd.gml"
# ALL_NODES = "blizzard"
FILEPATH_TO_VC_SENT = "data/vc_sent.csv"
FILEPATH_TO_VC_ADV_ATTR = "data/vc_upd_likes.csv"
FILEPATH_TO_DTF_ADV_ATTR = "data/dtf_likes_updated.csv"

def statistic_graph(graph):
    edge_count = len(graph.edges())
    node_count = len(graph.nodes())
    st.sidebar.markdown(f"Количество нод: {node_count}")
    st.sidebar.markdown(f"Количество рёбер: {edge_count}")


def add_topic_bars(node_selector, new_graph, adv_attr=TJ_ADV_ATTR):
    comp = pd.read_csv(TJ_COMP_TOPIC)
    key_word = np.load(TJ_KEY_WORDS)
    adv_attr_data = pd.read_csv(adv_attr)

    for node in new_graph.nodes():
        adv_attr_data_node = adv_attr_data[adv_attr_data["companies"] == node]
        comments_count = round(adv_attr_data_node["commentsCount"].item(), 4)
        hits_count = round(adv_attr_data_node["hitsCount"].item(), 4)
        likes = round(adv_attr_data_node["likes"].item(), 4)
        if node not in list(comp["companies"]):
            continue
        current_dict = ast.literal_eval(
            list(comp[comp["companies"] == node]["probs_sort"].items())[0][1])
        try:
            del current_dict["others"]
        except KeyError:
            pass
        if node == node_selector:
            main_dict = current_dict
        better_key = max(current_dict.items(), key=lambda x: x[1])[0]
        try:
            title = list(key_word[better_key])
            title = sample(title, MAX_WORD_IN_TITLE)
            title = repr(title)
            title = title + "<br>" + f"Avg Comments: {comments_count}"
            title = title + "<br>" + f"Avg Hits: {hits_count}"
            title = title + "<br>" + f"Avg Likes: {likes}"
            new_graph.nodes[node]["title"] = title
        except IndexError:
            pass
    label_from_keys = []
    for key in main_dict.keys():
        label_from_keys.append(list(key_word[key]))

    label_from_keys = list(map(lambda x: "\n".join(x), label_from_keys))

    arr = np.random.normal(1, 1, size=100)
    fig, ax = plt.subplots()
    ax.bar(label_from_keys, list(main_dict.values()))
    ax.set_title("Топики")
    st.sidebar.pyplot(fig)

    return new_graph


def add_adv_attrs(node_selector, adv_attrs=TJ_ADV_ATTR):
    adv_attr_data = pd.read_csv(adv_attrs)

    mean_comments_count = round(adv_attr_data["commentsCount"].mean(), 2)
    std_comments_count = round(sqrt(adv_attr_data["commentsCount"].std()), 2)
    mean_hit_count = round(adv_attr_data["hitsCount"].mean(), 2)
    std_hit_count = round(sqrt(adv_attr_data["hitsCount"].std()), 2)
    mean_likes = round(adv_attr_data["likes"].mean(), 2)
    std_likes = round(sqrt(adv_attr_data["likes"].std()), 2)

    adv_attr_data = adv_attr_data[adv_attr_data["companies"] == node_selector]
    comments_count = round(adv_attr_data["commentsCount"].item(), 1)
    hits_count = round(adv_attr_data["hitsCount"].item(), 1)
    likes = round(adv_attr_data["likes"].item(), 1)

    st.sidebar.markdown("***")
    st.sidebar.markdown(
        f"Комментов в среднем:\n{comments_count} для {node_selector}")
    st.sidebar.markdown(
        f"При {mean_comments_count} {PLUS_MINUS} {std_comments_count} для всех нод.")
    st.sidebar.markdown("***")
    st.sidebar.markdown(
        f"Посещений в среднем:\n{hits_count} для {node_selector}")
    st.sidebar.markdown(
        f"При {mean_hit_count} {PLUS_MINUS} {std_hit_count} для всех нод.")
    st.sidebar.markdown("***")
    st.sidebar.markdown(f"Лайков в среднем:\n{likes} для {node_selector}")
    st.sidebar.markdown(
        f"При {mean_likes} {PLUS_MINUS} {std_likes} для всех нод.")
    st.sidebar.markdown("***")


def int_to_hex_for_rgb(value):
    answer = str(hex(value))[2:]
    if len(answer) == 1:
        answer = "0" + answer
    return answer


def choose_node(node_selector, graph):
    init_sent_data = pd.read_csv(FILEPATH_TO_TJ_SENTIMENT)
    relevant_nodes = graph.nodes[node_selector]["relevant_nodes"]

    text_rel_nodes = relevant_nodes
    st.sidebar.markdown("Релевантные ноды:")
    st.sidebar.markdown(text_rel_nodes)

    neutral_value = init_sent_data[init_sent_data["companies"]
                                   == node_selector]["neutral"].item()
    positive_value = init_sent_data[init_sent_data["companies"]
                                    == node_selector]["positive"].item()
    negative_value = init_sent_data[init_sent_data["companies"]
                                    == node_selector]["negative"].item()

    labels = ["neutral", "positive", "negative"]

    sizes_context = [neutral_value, positive_value, negative_value]

    add_adv_attrs(node_selector)

    alt_data = pd.DataFrame({
        "a": labels,
        "b": sizes_context,
        "color": ["blue", "green", "red"],
    })
    st_alt_data = alt.Chart(alt_data).mark_bar().encode(
        x=alt.X("a", axis=alt.Axis(title="")),
        y=alt.X("b", axis=alt.Axis(title="")),
        color=alt.Color("color", scale=None),
    ).properties(
        title="Окрас",
    )
    st.sidebar.altair_chart(st_alt_data, use_container_width=True)

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

    for node in new_graph.nodes():
        new_graph.nodes[node]["size"] = max(new_graph.nodes[node]["size"], 10)

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
    st.sidebar.markdown("**Информация о данных.**")
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
    st.sidebar.markdown(f"Общее количество файлов: {sum(sizes_count)}")
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
            title = sample(title, MAX_WORD_IN_TITLE)
            title = repr(title)
            graph.nodes[node]["title"] = title
        except IndexError:
            pass
    #
    for node in graph.nodes():
        graph.nodes[node]["size"] = graph.nodes[node]["adjusted_node_size"]

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
        graph = add_topic_bars(node_selector, graph)
        graph = choose_node(node_selector, graph)

    for edge in graph.edges():
        graph.edges[edge]["color"] = "#B2B2B2"

    nt = Network("800px", "800px", notebook=True, heading="TJournal")
    nt.barnes_hut()
    nt.from_nx(graph)
    if node_selector != ALL_NODES:
        nt.hrepulsion(central_gravity=0.1)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show("html/tj_baseline.html")

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


def filter_graph_if_there_topic(graph, adv_attrs=FILEPATH_TO_VC_ADV_ATTR):
    data_topics = pd.read_csv(TJ_COMP_TOPIC)
    comp_list = list(data_topics["companies"])
    nodes_for_delete = []
    for node in graph.nodes():
        if node not in comp_list:
            nodes_for_delete.append(node)
    nodes_for_delete = sorted(nodes_for_delete, reverse=True)
    for node in nodes_for_delete:
        graph.remove_node(node)
    adv_attrs = pd.read_csv(adv_attrs)
    comp_list = list(adv_attrs["companies"])
    nodes_for_delete = []
    for node in graph.nodes():
        if node not in comp_list:
            nodes_for_delete.append(node)
    nodes_for_delete = sorted(nodes_for_delete, reverse=True)
    for node in nodes_for_delete:
        graph.remove_node(node)
    return graph


def basic_visualized_add_color_size(graph):
    comp = pd.read_csv(TJ_COMP_TOPIC)
    key_word = np.load(TJ_KEY_WORDS)
    for node in graph.nodes():
        graph.nodes[node]["font_size"] = 80
        current_dict = ast.literal_eval(
            list(comp[comp["companies"] == node]["probs_sort"].items())[0][1]
        )
        try:
            del current_dict["others"]
        except KeyError:
            pass
        better_key = max(current_dict.items(), key=lambda x: x[1])[0]
        try:
            title = list(key_word[better_key])
            title = sample(title, MAX_WORD_IN_TITLE)
            title = repr(title)
            graph.nodes[node]["title"] = title
        except IndexError:
            pass
    for node in graph.nodes():
        graph.nodes[node]["size"] = graph.nodes[node]["adjusted_node_size"]
    # for edge in graph.edges():
    #     graph.edges[edge]["color"] = "#B2B2B2"
    return graph


def add_sentence_adv(graph):
    neutral_list = []
    negative_list = []
    positive_list = []
    for node in graph.nodes():
        neutral = graph.nodes[node]["neutral"]
        negative = graph.nodes[node]["negative"]
        positive = graph.nodes[node]["positive"]
        neutral_list.append(neutral)
        negative_list.append(negative)
        positive_list.append(positive)
    neutral_list = np.array(neutral_list)
    negative_list = np.array(negative_list)
    positive_list = np.array(positive_list)
    neutral_list = (neutral_list - neutral_list.mean()) / neutral_list.std()
    negative_list = (negative_list - negative_list.mean()) / \
        negative_list.std()
    positive_list = (positive_list - positive_list.mean()) / \
        positive_list.std()

    for idx, node in enumerate(graph.nodes()):
        neutral = neutral_list[idx]  # graph.nodes[node]["neutral"]
        negative = negative_list[idx]  # graph.nodes[node]["negative"]
        positive = positive_list[idx]  # graph.nodes[node]["positive"]
        try:
            new_red = floor(negative / (negative + positive) * 255)
            new_green = 255 - new_red
            new_blue = 0
            new_rgb_color = "#" + \
                int_to_hex_for_rgb(
                    new_red) + int_to_hex_for_rgb(new_green) + int_to_hex_for_rgb(new_blue)
            graph.nodes[node]["color"] = new_rgb_color
        except (ValueError, ZeroDivisionError):
            graph.nodes[node]["color"] = "#0000ff"

    return graph


def choose_star_graph(graph, node_selector):
    star_graph = nx.Graph()
    star_graph.add_node(node_selector)
    neighbors = [i for i in graph.neighbors(node_selector)]
    for key, value in graph.nodes[node_selector].items():
        star_graph.nodes[node_selector][key] = value
    for node_neighbor in neighbors:
        star_graph.add_node(node_neighbor)
        star_graph.add_edge(node_selector, node_neighbor)
        for key, value in graph.nodes[node_neighbor].items():
            star_graph.nodes[node_neighbor][key] = value
    for node in star_graph.nodes():
        star_graph.nodes[node]["size"] = max(
            star_graph.nodes[node]["size"], 10)
    for edge in star_graph.edges():
        star_graph.edges[edge]["color"] = "#B2B2B2"
    return star_graph


def add_sent_bar_plot(graph, node_selector):
    neutral_value = graph.nodes[node_selector]["neutral"]
    positive_value = graph.nodes[node_selector]["positive"]
    negative_value = graph.nodes[node_selector]["negative"]
    labels = ["neutral", "positive", "negative"]
    sizes_context = [neutral_value, positive_value, negative_value]
    alt_data = pd.DataFrame({
        "a": labels,
        "b": sizes_context,
        "color": ["blue", "green", "red"],
    })
    st_alt_data = alt.Chart(alt_data).mark_bar().encode(
        x=alt.X("a", axis=alt.Axis(title="")),
        y=alt.X("b", axis=alt.Axis(title="")),
        color=alt.Color("color", scale=None),
    ).properties(
        title="Окрас",
    )
    st.sidebar.altair_chart(st_alt_data, use_container_width=True)


def add_rel_nodes(graph, node_selector):
    relevant_nodes = graph.nodes[node_selector]["relevant_nodes"]
    st.sidebar.markdown("Релевантные ноды:")
    st.sidebar.markdown(relevant_nodes)


def vc_graph(physics=False):
    graph = nx.read_gml(FILEPATH_TO_VC_GRAPH)
    graph = filter_graph_if_there_topic(graph, FILEPATH_TO_VC_ADV_ATTR)

    choose_type = st.sidebar.selectbox(
        "Выберите тип графа",
        (
            GRAPH_CLUSTERS,
            GRAPH_SENTIMENT,
        )
    )
    graph = basic_visualized_add_color_size(graph)
    if choose_type == GRAPH_SENTIMENT:
        graph = add_sentence_adv(graph)
    elif choose_type == GRAPH_CLUSTERS:
        for node in graph.nodes():
            graph.nodes[node]["color"] = graph.nodes[node]["modularity_color"]
    statistic_graph(graph)

    company_list = list(graph.nodes())
    node_selector = st.sidebar.selectbox(
        "Выберите ноду",
        [ALL_NODES] + list(company_list),
    )

    if node_selector != ALL_NODES:
        graph = choose_star_graph(graph, node_selector)
        graph = add_topic_bars(node_selector, graph, FILEPATH_TO_VC_ADV_ATTR)
        add_rel_nodes(graph, node_selector)
        add_adv_attrs(node_selector, FILEPATH_TO_VC_ADV_ATTR)
        add_sent_bar_plot(graph, node_selector)

    #

    main_statistic()
    nt = Network("800px", "800px", notebook=True, heading="VC.RU")
    if node_selector != ALL_NODES:
        nt.hrepulsion(central_gravity=0.1)
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


def dtf_graph(physics=False):
    graph = nx.read_gml(FILEPATH_TO_DTF_GRAPH)
    graph = filter_graph_if_there_topic(graph, FILEPATH_TO_DTF_ADV_ATTR)

    choose_type = st.sidebar.selectbox(
        "Выберите тип графа",
        (
            GRAPH_CLUSTERS,
            GRAPH_SENTIMENT,
        )
    )
    graph = basic_visualized_add_color_size(graph)
    if choose_type == GRAPH_SENTIMENT:
        graph = add_sentence_adv(graph)
    elif choose_type == GRAPH_CLUSTERS:
        for node in graph.nodes():
            graph.nodes[node]["color"] = graph.nodes[node]["modularity_color"]
    statistic_graph(graph)
    company_list = list(graph.nodes())
    node_selector = st.sidebar.selectbox(
        "Выберите ноду",
        [ALL_NODES] + list(company_list),
    )

    if node_selector != ALL_NODES:
        graph = choose_star_graph(graph, node_selector)
        graph = add_topic_bars(node_selector, graph, FILEPATH_TO_DTF_ADV_ATTR)
        add_rel_nodes(graph, node_selector)
        add_adv_attrs(node_selector, FILEPATH_TO_DTF_ADV_ATTR)
        add_sent_bar_plot(graph, node_selector)

    # statistic_graph(graph)
    main_statistic()
    nt = Network("800px", "800px", notebook=True, heading="DTF")
    if node_selector != ALL_NODES:
        nt.hrepulsion(central_gravity=0.1)
    nt.barnes_hut()
    nt.from_nx(graph)
    if physics:
        nt.show_buttons(filter_=["physics"])
    nt.show(FILEPATH_HTML_TO_DTF_BASELINE)
