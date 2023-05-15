import digraph
import edge_bet_centrality
import node_bet_centrality
import plots


# Create the digraph
osm_filename = "extracted_hamburg.osm"
landmarks_csv_filename = 'extracted_hamburg_landmarks.csv'
digraph = digraph.new_osm_digraph(osm_filename, landmarks_csv_filename)

# Compute node and edge betweenness centrality
digraph = node_bet_centrality.assign_node_bet_centrality_to_digraph(digraph, 'distance')
digraph = edge_bet_centrality.assign_edge_bet_centrality_to_digraph(digraph, 'distance')

# Plot node and edge betweenness centrality
# node_bet_centrality.plot_node_bet_centrality_graph(digraph, 'distance', 'extracted_hamburg_node_bet_centrality.png')
# edge_bet_centrality.plot_edge_bet_centrality_graph(digraph, 'distance', 'extracted_hamburg_edge_bet_centrality.png')

# Plot edge betweenness centrality with mean threshold
# edge_bet_centrality.plot_edge_bet_centrality_importance_graph_using_mean(digraph,
# 'extracted_hamburg_edge_bet_centrality.png')
edge_bet_centrality.plot_edge_bet_centrality_importance_graph_using_list_of_thresholds(digraph, 'extracted_hamburg_edge_bet_centrality')

# Plot node betweenness centrality with mean threshold
# node_bet_centrality.plot_node_bet_centrality_importance_graph_using_mean(digraph,
# 'extracted_hamburg_node_bet_centrality.png')
