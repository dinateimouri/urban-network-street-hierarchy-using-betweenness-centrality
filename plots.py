import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from statistics import mean
import numpy


def node_betweenness_centrality(digraph, weight_string):
    node_bet_centrality = nx.betweenness_centrality(
        digraph, normalized=True, weight=weight_string, endpoints=False
    )
    return node_bet_centrality


def plot_node_bet_centrality_graph(digraph, weight_string, plot_name):
    positions = {
        n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']]
        for n_id in digraph.nodes()
    }

    node_bet_centrality = node_betweenness_centrality(digraph, weight_string)
    norm = mcolors.Normalize(vmin=min(node_bet_centrality.values()), vmax=max(node_bet_centrality.values()))
    cmap = plt.cm.ScalarMappable(norm=norm, cmap=plt.get_cmap('viridis'))
    ec = [cmap.to_rgba(cl) for cl in node_bet_centrality.values()]

    high_important_edge_type = [
        (u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] in ['motorway', 'trunk']
    ]
    middle_important_edge_type = [
        (u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] in ['primary', 'secondary', 'tertiary']
    ]
    low_important_edge_type = [(u, v) for (u, v, d) in digraph.edges(data=True) if d['way_type'] == 'residential']

    edges_width = [15 if w in high_important_edge_type else 10 if w in middle_important_edge_type else 5 for w in
                   digraph.edges()]

    fig, ax = plt.subplots(figsize=(80, 80))
    nodes = nx.draw_networkx_nodes(
        digraph, positions, cmap=plt.get_cmap('plasma'), node_color=ec, nodelist=list(node_bet_centrality.keys())
    )
    nx.draw_networkx_edges(digraph, positions, width=edges_width, arrows=False)

    plt.title("Node Betweenness Centrality")
    plt.colorbar(nodes)
    plt.axis('off')
    plt.savefig(plot_name)
    plt.close(fig)
    return


def plot_node_bet_centrality_importance_graph_using_mean(digraph, plot_name):
    positions = {n_id: [10000000 * digraph.nodes[n_id]['lon'], 10000000 * digraph.nodes[n_id]['lat']] for n_id in
                 digraph.nodes()}

    node_bet_cent_list = [digraph.nodes[node]['node_bet_centrality'] for node in digraph.nodes()]
    node_bet_cent_mean = mean(node_bet_cent_list)
    thr = node_bet_cent_mean

    nodes_color = ['k' if nbc >= thr else 'gray' for nbc in node_bet_cent_list]

    high_important_edge_type = [('motorway', 'trunk'), ('trunk', 'motorway')]
    middle_important_edge_type = [('primary', 'secondary'), ('primary', 'tertiary'), ('secondary', 'primary'),
                                  ('secondary', 'tertiary'), ('tertiary', 'primary'), ('tertiary', 'secondary')]
    low_important_edge_type = [('residential', 'residential')]

    edges_width = [15 if w in high_important_edge_type else 10 if w in middle_important_edge_type else 5 for u, v, w in
                   digraph.edges(data='way_type')]

    plt.figure(figsize=(80, 80))
    nodes = nx.draw_networkx_nodes(digraph, positions, node_color=nodes_color, node_size=300, with_labels=False)
    nx.draw_networkx_edges(digraph, positions, width=edges_width, edge_color='gray', arrows=False)

    plt.title("Node Betweenness Centrality")
    plt.savefig(plot_name)
    return
