import matplotlib.pyplot as plt
import json
import networkx as nx
from networkx.readwrite import json_graph
import altair as alt
import os
from dotenv import load_dotenv
import nx_altair as nxa
import pandas as pd
import random


def html_create_node(nodes, graph):
    node_degrees_out = dict(graph.out_degree())
    node_degrees_in = dict(graph.in_degree())

    nodes['size_out'] = nodes['id'].map(node_degrees_out)
    nodes['size_out'] = nodes['size_out'].apply(
        lambda degree: 100 if degree == 0 else degree * 5000)
    nodes['size_in'] = nodes['id'].map(node_degrees_in)
    nodes['size_in'] = nodes['size_in'].apply(
        lambda degree: 100 if degree == 0 else degree * 5000)
    nodes['size'] = nodes.apply(lambda row: row['size_out'] + row['size_in'] -
                                2000 if row['size_out'] > 2000 and
                                row['size_in'] > 2000 else 2000, axis=1)

    nodes_chart = alt.Chart(nodes).mark_circle().encode(
        x='x',
        y='y',
        size=alt.Size('size', scale=alt.Scale(range=[100, 2000])),
        color=alt.value('skyblue'),
        tooltip=['id']
    ).properties(width=800, height=600, title='')

    return nodes_chart


def html_create_text(nodes):
    nodes_text = alt.Chart(nodes).mark_text(align='left', baseline='middle',
                                            dx=7, size=14).encode(
        x='x:Q',
        y='y:Q',
        text='id'
    )
    return nodes_text


def html_create_chart(pos, graph):
    arrow_data_list = []
    for src, tgt in graph.edges:
        arrow_data_list.append((pos[src][0], pos[src][1],
                                pos[tgt][0], pos[tgt][1]))

    arrow_data = pd.DataFrame(arrow_data_list, columns=['x', 'y', 'x2', 'y2'])
    arrows_chart = alt.Chart(arrow_data).mark_text(align='left',
                                                   baseline='middle',
                                                   dx=7, size=10).encode(
        x='x:Q',
        y='y:Q',
        opacity=alt.value(0),
        text='arrow:N'
    ) + alt.Chart(arrow_data).mark_line(opacity=0.5).encode(
        x='x:Q',
        y='y:Q',
        x2='x2:Q',
        y2='y2:Q'
    ).interactive()
    return arrows_chart


def html_paint(graph, pos):
    nodes = pd.DataFrame(pos, index=['x', 'y']).T.reset_index().rename(
        columns={'index': 'id'})
    nodes_chart = html_create_node(nodes, graph)
    nodes_text = html_create_text(nodes)
    arrows_chart = html_create_chart(pos, graph)
    interactive_graph = nodes_chart + nodes_text + arrows_chart

    interactive_graph.save("wiki_graph.html")


def read_json_file():
    load_dotenv()
    WIKI_FILE = os.getenv('WIKI_FILE')
    with open(WIKI_FILE) as f:
        js_graph = json.load(f)
    return nx.DiGraph(json_graph.node_link_graph(js_graph), directed=True)


def create_node_size(node_degrees):
    node_sizes = {}
    for node, degree in node_degrees:
        if degree == 0:
            node_sizes[node] = 50
        else:
            node_sizes[node] = degree * 10
    return node_sizes


def move_node(pos):
    pos_with_offset = {}
    for node, (x, y) in pos:
        new_x = x + random.uniform(-0.1, 0.1)
        new_y = y + random.uniform(-0.1, 0.1)
        pos_with_offset[node] = (new_x, new_y)
    return pos_with_offset


def paint_graph():
    graph = read_json_file()

    node_degrees = dict(graph.out_degree())
    node_sizes = create_node_size(node_degrees.items())

    pos = nx.kamada_kawai_layout(graph)
    pos_with_offset = move_node(pos.items())

    fig, ax = plt.subplots()
    nx.draw(graph, pos_with_offset, with_labels=False,
            node_size=[node_sizes[node] for node in graph.nodes()],
            node_color='skyblue', ax=ax, connectionstyle='arc3, rad=0.1')

    labels_pos = {node: (x, y + 0.02)
                  for node, (x, y) in pos_with_offset.items()}
    bbox_dict = dict(facecolor=(0, 0, 0, 0),
                     edgecolor='black', boxstyle='round,pad=0.5')

    nx.draw_networkx_labels(graph, labels_pos, font_size=10, font_color='red',
                            verticalalignment="center",
                            horizontalalignment="center",
                            ax=ax, bbox=bbox_dict)
    plt.savefig("wiki_graph.png", format='png')

    if input("Создать HTML файл (Y/N)? ").lower() == "y":
        html_paint(graph, pos_with_offset)

    plt.show()


def main():
    paint_graph()


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("file not found")
    except Exception as e:
        print(f"Error: {e}")
