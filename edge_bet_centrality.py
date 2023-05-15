import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import seaborn as sns
from statistics import mean
import numpy


def edge_betweenness_centrality(digraph, weight_string):
    # Betweenness centrality of an edge e is the sum of the fraction of all-pairs shortest paths that pass through e
    edge_bet_centrality = nx.edge_betweenness_centrality(digraph, normalized=True, weight=weight_string)
    # create_density_plot(digraph, edge_bet_centrality)
    # Returns dictionary of edges with betweenness centrality as the value
    return edge_bet_centrality


def line_graph(digraph):
    # Streets are represented as nodes and intersections are represented as edges
    dual_graph = nx.line_graph(digraph)
    return dual_graph


def plot_edge_bet_centrality_graph(digraph, weight_string, plot_name):
    positions = {n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']] for n_id in
                 digraph.nodes()}

    edge_bet_centrality = edge_betweenness_centrality(digraph, weight_string)
    norm = mcolors.Normalize(vmin=min(edge_bet_centrality.values()), vmax=max(edge_bet_centrality.values()))
    cmap = plt.cm.ScalarMappable(norm=norm, cmap=plt.get_cmap('viridis'))
    ec = [cmap.to_rgba(cl) for cl in edge_bet_centrality.values()]

    high_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                d['way_type'] == 'motorway' or d['way_type'] == 'trunk']
    middle_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                  d['way_type'] == 'primary' or d['way_type'] == 'secondary' or d[
                                      'way_type'] == 'tertiary']
    low_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] == 'residential']

    edges_width = [15 if w in high_important_edge_type else 10 if w in middle_important_edge_type else 5 for w in
                   digraph.edges()]

    plt.figure(figsize=(80, 80))
    nodes = nx.draw_networkx_nodes(digraph, positions)
    edges = nx.draw_networkx_edges(digraph, positions, cmap=plt.get_cmap('plasma'),
                                   edge_color=ec,
                                   edgelist=list(edge_bet_centrality.keys()),
                                   width=edges_width, arrows=False)
    # Not including arrows results in "matplotlib.collection.LineCollection"
    # "matplotlib.collection.LineCollection" make it possible to "plt.colorbar(edges)"
    # I could get a colorbar only if I set arrows to False

    plt.title("Edge Betweenness Centrality")
    plt.colorbar(edges)
    plt.axis('off')
    plt.savefig(plot_name)
    # plt.show()
    return


def plot_edge_bet_centrality_importance_graph_using_mean(digraph, plot_name):
    positions = {n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']] for n_id in
                 digraph.nodes()}

    edge_bet_cent_list = []
    for (node1, node2) in digraph.edges():
        ebc = digraph.edges[node1, node2]['edge_bet_centrality']
        edge_bet_cent_list.append(ebc)
    edge_bet_cent_mean = mean(edge_bet_cent_list)
    # edge_bet_cent_std = numpy.std(edge_bet_cent_list)
    # thr = edge_bet_cent_mean + edge_bet_cent_std
    thr = edge_bet_cent_mean

    edges_color = []
    for (node1, node2) in digraph.edges():
        ebc = digraph.edges[node1, node2]['edge_bet_centrality']
        if ebc >= thr:
            edges_color.append('k')
        else:
            edges_color.append('gray')


    high_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                d['way_type'] == 'motorway' or d['way_type'] == 'trunk']
    middle_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                  d['way_type'] == 'primary' or d['way_type'] == 'secondary' or d[
                                      'way_type'] == 'tertiary']
    low_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] == 'residential']

    edges_width = [30 if w in high_important_edge_type else 15 if w in middle_important_edge_type else 5 for w in
                   digraph.edges()]

    plt.figure(figsize=(80, 80))
    nodes = nx.draw_networkx_nodes(digraph, positions, node_size=0, node_color=['none'], with_labels=False, )
    edges = nx.draw_networkx_edges(digraph, positions,
                                   edge_color=edges_color,
                                   width=edges_width, arrows=False)
    # Not including arrows results in "matplotlib.collection.LineCollection"
    # "matplotlib.collection.LineCollection" make it possible to "plt.colorbar(edges)"
    # I could get a colorbar only if I set arrows to False

    plt.title("Edge Betweenness Centrality")
    plt.savefig(plot_name)
    # plt.show()
    return


def plot_edge_bet_centrality_importance_graph_using_list_of_thresholds(digraph, plot_name):
    thr_list = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
    positions = {n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']] for n_id in
                 digraph.nodes()}
    high_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                d['way_type'] == 'motorway' or d['way_type'] == 'trunk']
    middle_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if
                                  d['way_type'] == 'primary' or d['way_type'] == 'secondary' or d[
                                      'way_type'] == 'tertiary']
    low_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] == 'residential']

    edges_width = [30 if w in high_important_edge_type else 15 if w in middle_important_edge_type else 5 for w in
                   digraph.edges()]

    edge_bet_cent_list = []
    for (node1, node2) in digraph.edges():
        ebc = digraph.edges[node1, node2]['edge_bet_centrality']
        edge_bet_cent_list.append(ebc)
    edge_bet_cent_max = max(edge_bet_cent_list)

    level = len(thr_list)
    for thr in thr_list:
        current_thr = (1-thr) * edge_bet_cent_max
        edges_color = []
        for (node1, node2) in digraph.edges():
            ebc = digraph.edges[node1, node2]['edge_bet_centrality']
            if ebc >= current_thr:
                edges_color.append('orange')
            else:
                edges_color.append('gray')

        plt.figure(figsize=(80, 80))
        nodes = nx.draw_networkx_nodes(digraph, positions, node_size=0, node_color=['none'], with_labels=False, )
        edges = nx.draw_networkx_edges(digraph, positions,
                                       edge_color=edges_color,
                                       width=edges_width, arrows=False)
        # Not including arrows results in "matplotlib.collection.LineCollection"
        # "matplotlib.collection.LineCollection" make it possible to "plt.colorbar(edges)"
        # I could get a colorbar only if I set arrows to False

        # plt.title("Edge Betweenness Centrality")
        current_plot_name = '{}_level_{}.png'.format(plot_name, level)
        plt.savefig(current_plot_name)
        # plt.show()
        level -= 1


    return


def create_density_plot(digraph, edge_bet_centrality):
    lst = []
    for (node1, node2) in digraph.edges():
        k = (node1, node2)
        lst.append(edge_bet_centrality.get(k,  ""))
    df = pd.DataFrame(lst, columns=['edge_bet_centrality'])
    sns.kdeplot(df['edge_bet_centrality'])
    plt.show()
    return

