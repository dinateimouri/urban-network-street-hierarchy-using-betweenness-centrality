import xml.sax
import networkx as nx
import pyproj
import numpy as np
import time
import csv
import itertools
import requests
import xml.sax
from typing import Dict


class Node:
    def __init__(self, node_id, lon, lat, is_decision_point):
        self.id = node_id
        self.lon = lon
        self.lat = lat
        self.tags = {}
        self.is_decision_point = is_decision_point


class Way:
    def __init__(self, way_id, osm):
        self.osm = osm
        self.id = way_id
        self.nds = []
        self.tags = {}


class OSM:
    def __init__(self, filename_or_stream):
        nodes = {}
        ways = {}

        class OSMHandler(xml.sax.ContentHandler):
            def __init__(self):
                self.curr_elem = None
                self.counter = {}

            def startElement(self, name, attrs):
                if name == 'node':
                    self.curr_elem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']), False)
                elif name == 'way':
                    self.curr_elem = Way(attrs['id'], self)
                elif name == 'tag':
                    self.curr_elem.tags[attrs['k']] = attrs['v']
                elif name == 'nd':
                    self.curr_elem.nds.append(attrs['ref'])

            def endElement(self, name):
                if name == 'node':
                    nodes[self.curr_elem.id] = self.curr_elem
                elif name == 'way':
                    ways[self.curr_elem.id] = self.curr_elem

            def characters(self, chars):
                pass

            def endDocument(self):
                # Decision Points
                for w in ways.values():
                    if 'highway' in w.tags:
                        highway_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']
                        if w.tags['highway'] in highway_types:
                            for nd_ref in w.nds:
                                if nd_ref not in self.counter:
                                    self.counter[nd_ref] = 0
                                self.counter[nd_ref] += 1
                intersections_ref = [x for x in self.counter if self.counter[x] > 1]
                print(f'Number of Decision Points : {len(intersections_ref)}')

                for n in nodes.values():
                    if n.id in intersections_ref:
                        n.is_decision_point = True

        xml.sax.parse(filename_or_stream, OSMHandler())
        self.nodes = nodes
        self.ways = ways


def create_osm_digraph(filename: str) -> nx.DiGraph:
    print('Start Digraph Creation ...')

    osm = OSM(filename)
    G = nx.DiGraph()
    for w in osm.ways.values():
        if 'highway' in w.tags:
            if w.tags['highway'] in ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']:
                w_dp = [n_id for n_id in w.nds if osm.nodes[n_id].isDP]
                if 'oneway' in w.tags and w.tags['oneway'] == 'yes':
                    G.add_path(w_dp, id=w.id)
                else:
                    G.add_path(w_dp, id=w.id)
                    G.add_path(w_dp[::-1], id=w.id)

    print('Node Parameter Calculation ...')

    for DP_id in G.nodes():
        DP = osm.nodes[DP_id]
        neighbor_one = list(G.neighbors(DP_id))
        neighbor_two = list(G.predecessors(DP_id))
        neighbor_list = list(set(neighbor_one) | set(neighbor_two))
        G.nodes[DP_id].update({'lat': DP.lat, 'lon': DP.lon, 'id': DP.id})
        for neighbor_id in neighbor_list:
            node_neighbor = osm.nodes[neighbor_id]
            pointNeighbor = [node_neighbor.lat, node_neighbor.lon]
            pointDP = [G.nodes[DP_id]['lat'], G.nodes[DP_id]['lon']]
            fwd_azimuth_DPNeighbor, back_azimuth_DPNeighbor, distance_DPNeighbor = get_azimuth(pointDP, pointNeighbor)
            if G.has_edge(DP_id, neighbor_id):
                G.edges[DP_id, neighbor_id].update({'bearing': fwd_azimuth_DPNeighbor, 'distance': distance_DPNeighbor})
            else:
                G.edges[neighbor_id, DP_id].update({'bearing': fwd_azimuth_DPNeighbor, 'distance': distance_DPNeighbor})

    print('Edge Parameter Calculation ...')

    for (node1, node2) in G.edges():
        if 'distance' not in G.edges[node1, node2]:
            G.edges[node1, node2]['distance'] = G.edges[node2, node1]['distance']

    return G


def get_azimuth(point_a, point_b):
    lat1, lat2, long1, long2 = point_a[0], point_b[0], point_a[1], point_b[1]
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth, back_azimuth, distance = geodesic.inv(long1, lat1, long2, lat2)
    return fwd_azimuth, back_azimuth, distance


def assign_edge_bet_centrality_to_digraph(digraph, weight_string):
    edge_bet_centrality = nx.edge_betweenness_centrality(digraph, normalized=True, weight=weight_string)
    for (node1, node2), v in edge_bet_centrality.items():
        digraph.edges[node1, node2]['edge_bet_centrality'] = v
    return digraph


def assign_node_bet_centrality_to_digraph(digraph, weight_string):
    node_bet_centrality = nx.betweenness_centrality(digraph, normalized=True, weight=weight_string, endpoints=False)
    for DP_id, v in node_bet_centrality.items():
        digraph.nodes[DP_id]['node_bet_centrality'] = v
    return digraph


def find_random_origin_destination_pairs(digraph, pairs_number):
    dp_list = list(digraph.nodes)
    od_list = []
    while len(od_list) < pairs_number:
        source, destination = np.random.choice(dp_list, size=2, replace=False)
        while source == destination or digraph.has_edge(source, destination) or not nx.has_path(digraph, source, destination):
            source, destination = np.random.choice(dp_list, size=2, replace=False)
        if (source, destination) not in od_list:
            od_list.append((source, destination))
    return od_list


def path_finder(digraph, source, destination):
    path = nx.dijkstra_path(digraph, source, destination)
    return path
