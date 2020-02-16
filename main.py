import json
from operations import *

def preprocess(sample, rules):
    """
    Generic operations to simplify the complexity of the pattern
    :param sample: sample need to be process
    :param rules: preprocess rules
    :return: clearned information # TODO: What is it exactly
    """
    edges = []
    for rule in rules:
        flag, edges_tmp, labels = matched(sample, rule, "preprocess")
        if flag:
            sample["labels"] = labels
            edges.extend(edges_tmp)
    return sample, edges

def convert(sample, rules):
    edges = []
    for rule in rules:
        flag, edges_temp = matched(sample, rule)
        if flag:
            edges.append((rule, edges_temp))
    if len(edges) == 0:
        return False, []
    edges = sorted(edges, key=lambda x: x[0]["level"], reverse=True)
    return True, edges[0][1]

def generate(sample, rules_p, rules_c):
    edges = []
    sample, edges_temp = preprocess(sample, rules_p)
    edges.extend(edges_temp)
    flag, edges_temp = convert(sample, rules_c)
    if flag:
        edges.extend(edges_temp)
    for index, edge in enumerate(edges):
        if edge["time"]:
            edge["time"] = sample["time"]
        else:
            edge["time"] = "1990-01-01"
    return flag, edges