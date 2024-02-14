from bs4 import BeautifulSoup
import requests
import argparse
import json
import networkx as nx
import logging
import os
from dotenv import load_dotenv
from urllib.parse import quote


def read_args():
    parser = argparse.ArgumentParser(description='Great Description')
    parser.add_argument('-p', '--title', type=str,
                        default='Erdős number', help='Article title')
    parser.add_argument('-d', '--depth', type=int,
                        default=3, help='Search depth')
    args = parser.parse_args()
    return args


def open_links(title_link):
    url = 'https://en.wikipedia.org/wiki/'
    page = requests.get(url + quote(title_link))
    if page.status_code == 200:
        logging.info(url + quote(title_link))
        all_links = []
        soup = BeautifulSoup(page.text, 'html.parser')
        artical_links = soup.find_all('p')

        for paragraph in artical_links:
            links = paragraph.find_all(
                'a', href=lambda href: href and href.startswith('/wiki/'))
            for link in links:
                if 'title' in link.attrs:
                    all_links.append(link['title'])

        see_also_section = soup.find('span', {'id': 'See_also'})
        if see_also_section:
            links_see_also_section = see_also_section.find_next('ul')
            if links_see_also_section:
                links = links_see_also_section.find_all(
                    'a', href=lambda href: href and href.startswith('/wiki/'),
                    title=True)
                for link in links:
                    if 'title' in link.attrs:
                        all_links.append(link['title'])
        return all_links
    logging.warning(f"{title_link} does not exist")
    return []


def graph_build(graph, title, step, depth):
    if step >= depth:
        return graph
    links = open_links(title)
    for link_title in links:
        if graph.number_of_nodes() < 1000:
            if link_title not in graph:
                graph.add_node(link_title)
                graph.add_edge(title, link_title)
                graph_build(graph, link_title, step + 1, depth)
            else:
                graph.add_edges_from([(title, link_title)])

    return graph


def save_wiki_file(graph):
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    WIKI_FILE = os.environ.get("WIKI_FILE")
    if WIKI_FILE is None:
        logging.warning("Check file .env, WIKI_FILE is None")
        return
    if graph.number_of_nodes() > 20:
        data = nx.node_link_data(graph)
        with open(WIKI_FILE, "w") as json_file:
            json.dump(data, json_file)
    else:
        if graph.number_of_nodes() != 1:
            logging.warning("Few links, choose another search")


def main():
    logging.basicConfig(level=logging.INFO)
    args = read_args()

    graph = nx.DiGraph()
    graph.add_node(args.title)
    graph = graph_build(graph, args.title, 0, args.depth)
    save_wiki_file(graph)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
