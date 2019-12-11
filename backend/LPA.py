import pandas as pd
import numpy as np
import string
import codecs
import sys, json


def loadData(p):
    if sys.version_info.major > 2:
        f = open(p, 'r', encoding='utf-8')
    else:
        f = open(p, 'r')
    dict_data = json.load(f)

    links = dict_data['all']['links']
    nodes = dict_data['all']['nodes']

    node_dic = {}
    index = 0
    for node in nodes:
        node_dic[node['id']] = str(index)
        index += 1

    vector_dict = {}
    edge_dict = {}
    for link in links:
        lines = [node_dic[link['source']], node_dic[link['target']], str(link['value'])]
        for i in range(2):
            if lines[i] not in vector_dict:
                vector_dict[lines[i]] = int(lines[i])
                edge_list = []
                if len(lines) == 3:
                    edge_list.append(lines[1 - i] + ":" + lines[2])
                else:
                    edge_list.append(lines[1 - i] + ":" + "1")
                edge_dict[lines[i]] = edge_list
            else:
                edge_list = edge_dict[lines[i]]
                if len(lines) == 3:
                    edge_list.append(lines[1 - i] + ":" + lines[2])
                else:
                    edge_list.append(lines[1 - i] + ":" + "1")
                edge_dict[lines[i]] = edge_list
    return vector_dict, edge_dict


def get_max_community_label(vector_dict, adjacency_node_list):
    label_dict = {}
    for node in adjacency_node_list:
        node_id_weight = node.strip().split(":")
        node_id = node_id_weight[0]
        node_weight = int(node_id_weight[1])

        # 按照label为group维度，统计每个label的weight累加和
        if vector_dict[node_id] not in label_dict:
            label_dict[vector_dict[node_id]] = node_weight
        else:
            label_dict[vector_dict[node_id]] += node_weight

    sort_list = sorted(label_dict.items(), key=lambda d: d[1], reverse=True)
    return sort_list[0][0]


def check(vector_dict, edge_dict):
    for node in vector_dict.keys():
        adjacency_node_list = edge_dict[node]  # 获取该节点的邻居节点
        node_label = vector_dict[node]  # 获取该节点当前label
        label = get_max_community_label(vector_dict, adjacency_node_list)  # 从邻居节点列表中选择weight累加和最大的label
        if node_label >= label:
            continue
        else:
            return 0  # 找到weight权重累加和更大的label
    return 1


def label_propagation(vector_dict, edge_dict):
    t = 0
    print('First Label: ')
    while True:
        if (check(vector_dict, edge_dict) == 0):
            t = t + 1
            print('iteration: ', t)
            # 每轮迭代都更新一遍所有节点的社区label
            for node in vector_dict.keys():
                adjacency_node_list = edge_dict[node]
                vector_dict[node] = get_max_community_label(vector_dict, adjacency_node_list)
        else:
            break
    return vector_dict


def get_afterLPA_json(input_fn, output_fn, cluster_group):
    if sys.version_info.major > 2:
        f = open(input_fn, 'r', encoding='utf-8')
    else:
        f = open(input_fn, 'r')
    dict_data = json.load(f)
    nodes = dict_data['all']['nodes']

    m_node_id_cluster_id = dict()   # node_name -> cluster_id

    for cluster_id, value in cluster_group.items():
        for person_id in value:
            nodes[int(person_id)]['cluster'] = cluster_id
            m_node_id_cluster_id[nodes[int(person_id)]['id']] = cluster_id

    dict_data['all']['nodes'] = nodes

    for sid, scene in enumerate(dict_data['scenes']):
        for nid, node in enumerate(scene['nodes']):
            dict_data['scenes'][sid]['nodes'][nid]['cluster'] = m_node_id_cluster_id[node['id']]
    
    for did, dialog in enumerate(dict_data['dialogs']):
        for phase in ('source', 'target'):
            dict_data['dialogs'][did][phase] = {'id': dialog[phase], 'cluster': m_node_id_cluster_id[dialog[phase]]}

    json.dump(dict_data, codecs.open(output_fn, 'w', encoding='utf-8'), separators=(',', ':'),
              sort_keys=True,
              indent=4)


if __name__ == '__main__':
    filePath = '../jsons/10things_dialogs_scenes_all.json'
    vector, edge = loadData(filePath)
    print(vector)
    print(edge)

    print("start lpa clustering....")

    vector_dict = label_propagation(vector, edge)
    print("ending lpa clustering....")
    print("the finnal cluster result....")
    print(vector_dict)

    cluster_group = dict()
    for node in vector_dict.keys():
        cluster_id = vector_dict[node]
        print("cluster_id, node", cluster_id, node)

        if cluster_id not in cluster_group.keys():
            cluster_group[cluster_id] = [node]
        else:
            cluster_group[cluster_id].append(node)

    print(cluster_group)

    get_afterLPA_json(filePath, "../jsons/10tings_dialogs_scenes_all_LPA.json", cluster_group)
