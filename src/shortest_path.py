import argparse
import json
from collections import deque
import os
from dotenv import load_dotenv


def open_file():
    load_dotenv()
    WIKI_FILE = os.getenv('WIKI_FILE')
    with open(WIKI_FILE, "r") as json_file:
        json_dictionary = json.load(json_file)

    return json_dictionary


def convert_in_graph(json_dictionary):
    graph = {}

    for node in json_dictionary["nodes"]:
        graph[node["id"]] = []

    for link in json_dictionary["links"]:
        source = link["source"]
        target = link["target"]
        graph[source].append(target)

    return graph


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", type=str,
                        required=True, dest="start", help="start page")
    parser.add_argument("--to", type=str,
                        required=True, dest="end", help="end page")
    parser.add_argument("--non-directed",
                        action="store_true", help="undirected edges")
    parser.add_argument("-v", action='store_true', help="path output")
    args = parser.parse_args()
    return args


def short_path_search(graph, start, end, non_directed=False):
    if start not in graph or end not in graph:
        return None

    if non_directed:
        convert_to_bidirectional(graph)

    return bfs(graph, start, end)


def convert_to_bidirectional(graph):
    for source in graph:
        for target in graph[source]:
            if source not in graph[target]:
                graph[target].append(source)


def print_graph(graph):
    for source in graph:
        print("- ", source)
        if graph[source] is not None:
            for target in graph[source]:
                print("-- ", target)
        print()


# BFS
def bfs(graph, start, end):
    queue = deque()
    previous = {}  # словарь для отслеживания предыдущей першины

    queue.append(start)
    previous[start] = None

    while queue:
        node = queue.popleft()

        if node == end:
            # Возращаем путь
            path = []
            while node is not None:
                path.insert(0, node)
                node = previous[node]
            return path

        for neighbor in graph[node]:
            if neighbor not in previous:
                queue.append(neighbor)
                previous[neighbor] = node

    return None


def output_path(path, arg_v):
    if path:
        if arg_v:
            print(" -> ".join(path))
        print(len(path) - 1)  # Количество рёбер в пути
    else:
        print("path not found")


def main():
    json_dictionary = open_file()
    graph = convert_in_graph(json_dictionary)
    args = read_args()
    start_page = args.start
    end_page = args.end
    non_directed = args.non_directed
    arg_v = args.v

    if start_page is None or end_page is None:
        print("path not found")
    else:
        path = short_path_search(graph, start_page, end_page, non_directed)
        output_path(path, arg_v)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("file not found")
    except Exception as e:
        print(f"Error: {e}")
