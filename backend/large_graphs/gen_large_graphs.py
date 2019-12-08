"""
generate large graph with clusters
"""

import typing
import random
import json
import codecs


def load_names() -> typing.List[str]:
    """
    load names from two specified csv files for node names
    :return: list of names
    """
    names = []
    for i in range(1, 3):
        with codecs.open('D:\wyxData\data\citation\scopus_visual_analytics_part{}.csv'.format(i),
                         'r', 'utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == 'Authors':
                    continue
                authors = line.split(',')[0].strip('"')
                names.extend([name.strip() for name in authors.split(',')])
    return names


def gen_inner_cluster(cluster_id: int, n_nodes: int, edge_density: float, begin_idx: int, names: typing.List[str]) \
        -> (typing.List[typing.Dict], typing.List[typing.Dict]):
    """
    generate a node cluster and edges in the cluster
    :param cluster_id: index of the generated cluster
    :param n_nodes: number of nodes in the cluster
    :param edge_density: probability of an edge between two nodes in the cluster
    :param begin_idx: beginning index for `num` of first node in the cluster
    :param names: whole name list
    :return: list of node dict & list of edge dict
        node dict: {"num": number_id, "id": node_name, "group": cluster_id}
        edge dict: {"source": source_node_number_id, "target": target_node_number_id, "value": edge weight}
    """
    nodes, edges = [], []
    n_names = len(names)
    for num in range(begin_idx, begin_idx + n_nodes):
        nodes.append({"num": num, "id": names[num % n_names], "group": cluster_id})
    for src_nid in range(n_nodes):
        for dst_nid in range(src_nid):
            if random.random() < edge_density:
                edges.append({"source": nodes[src_nid]['num'], "target": nodes[dst_nid]["num"], "value": 1})
    return nodes, edges


def gen_inter_cluster(src_node_cluster: typing.List[typing.Dict], dst_node_cluster: typing.List[typing.Dict],
                      edge_density: float) -> typing.List[typing.Dict]:
    """
    generate edges between two clusters
    :param src_node_cluster:
    :param dst_node_cluster:
    :param edge_density:
    :return: list of edge dict
    """
    edges = []
    for src_node in src_node_cluster:
        for dst_node in dst_node_cluster:
            if random.random() < edge_density:
                edges.append({"source": src_node['num'], "target": dst_node['num'], "value": 1})
    return edges


def gen_large_graph_with_clusters(n_clusters: int, cluster_nodes_lower: int, cluster_nodes_upper: int,
                                  inner_density_lower: float, inner_density_upper: float,
                                  skip_connection: float,
                                  inter_density_lower: float, inter_density_upper: float) \
        -> (typing.List[typing.Dict], typing.List[typing.Dict]):
    """
    generate large graph with clusters
    :param n_clusters: number of clusters
    :param cluster_nodes_lower: lower bound of number of nodes in a cluster
    :param cluster_nodes_upper: uppper bound of number of nodes in a cluster
    :param inner_density_lower: lower bound of edge density in a cluster
    :param inner_density_upper: upper bound of edge density in a cluster
    :param skip_connection: probability of no connection between two clusters
    :param inter_density_lower: lower bound of edge density between two clusters
    :param inter_density_uppper: upper bound of edge density between two clusters
    :return:
    """
    names = load_names()
    print('# of names: {}'.format(len(names)))
    node_num = 0
    node_clusters = []
    edges = []
    for cluster_id in range(n_clusters):
        tmp_n_nodes = random.randint(cluster_nodes_lower, cluster_nodes_upper)
        tmp_nodes, tmp_edges = gen_inner_cluster(cluster_id, tmp_n_nodes,
                                                 random.uniform(inner_density_lower, inner_density_upper),
                                                 node_num, names)
        node_num += tmp_n_nodes
        node_clusters.append(tmp_nodes)
        edges.extend(tmp_edges)
    for src_cid in range(n_clusters):
        for dst_cid in range(src_cid):
            if random.random() < skip_connection:
                edges.extend(gen_inter_cluster(node_clusters[src_cid],
                                                node_clusters[dst_cid],
                                                random.uniform(inter_density_lower, inter_density_upper)))
    nodes = []
    for cluster in node_clusters:
        nodes.extend(cluster)
    return nodes, edges


if __name__ == '__main__':
    nodes, edges = gen_large_graph_with_clusters(n_clusters=20,
                                                 cluster_nodes_lower=5,
                                                 cluster_nodes_upper=20,
                                                 inner_density_lower=.2,
                                                 inner_density_upper=.6,
                                                 skip_connection=.4,
                                                 inter_density_lower=.01,
                                                 inter_density_upper=.05)
    with open('../../jsons/large_graph.json', 'w') as f:
        json.dump({"nodes": nodes, "links": edges}, f, indent=4)


