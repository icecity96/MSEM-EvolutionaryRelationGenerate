import json
from operations import *
from collections import Counter

DEBUG = True
debug_pattern = []
def preprocess(sample, rules):
    """
    Generic operations to simplify the complexity of the pattern
    :param sample: sample need to be process
    :param rules: preprocess rules
    :return: clearned information # TODO: What is it exactly
    """
    edges = []
    rules_flag = [True]
    # TODO: Optimize
    while any(rules_flag):
        rules_flag = []
        edges_temp = []
        for rule in rules:
            flag, edges_tmp, labels = matched(sample, rule, "preprocess")
            if flag:
                edges_temp.append((rule, edges_tmp, labels))
            rules_flag.append(flag)
        if len(edges_temp) != 0:
            edges_temp = sorted(edges_temp, key=lambda x: x[0]["level"], reverse=True)
            edges.extend(edges_temp[0][1])
            sample["labels"] = [[l for l in label]for label in edges_temp[0][2]]
    return sample, edges

def convert(sample, rules):
    edges = []
    if len(sample["labels"]) <= 1:
        return True, []
    for rule in rules:
        flag, edges_temp = matched(sample, rule)
        if flag:
            edges.append((rule, edges_temp))
    if len(edges) == 0:
        if DEBUG:
            if '-'.join([label[2] for label in sample["labels"]]) == "Actor-Object":
                print(sample)
            debug_pattern.append('-'.join([label[2] for label in sample["labels"]]))
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

def generate_nodes_Sedges(sample):
    nodes, edges = [], []
    nodes.append({"id": sample["text"], "label": sample["text"], "type": "event"})
    for label in sample["labels"]:
        if label[2] in ["Actor", "Recipient"]:
            nodes.append({"id": sample["text"][label[0]: label[1]], "label": sample["text"][label[0]: label[1]], "type": "stakeholder"})
            edges.append({"source": sample["text"], "target": sample["text"][label[0]: label[1]], "r": "Has{}".format(label[2]), "attr": None, "time": sample["time"]})
        elif label[2] == "Object":
            nodes.append({"id": sample["text"][label[0]: label[1]], "label": sample["text"][label[0]: label[1]],
                          "type": "service"})
            edges.append(
                {"source": sample["text"], "target": sample["text"][label[0]: label[1]], "r": "Has{}".format(label[2]),
                 "attr": None, "time": sample["time"]})
    return nodes, edges

def generate_file(input_file, rules_p, rules_c, output_node, output_edge, write_bakfile, ensured_file, score=5.0):
    rules_p = json.load(open(rules_p, encoding="utf-8"))["preprocess"]
    rules_c = json.load(open(rules_c, encoding="utf-8"))["rules"]
    samples = open(input_file, encoding="utf-8").readlines()
    output_node = open(output_node, 'a', encoding="utf-8")
    output_edge = open(output_edge, 'a', encoding="utf-8")
    wb = open(write_bakfile, 'w', encoding="utf-8")
    es = open(ensured_file, 'a', encoding="utf-8")
    for sample in samples:
        sample_json = json.loads(sample)
        if "score" in sample_json and sample_json["score"] < score:
            wb.write(sample)
            continue
        sample_json = format_json(sample_json)
        flag, edges = generate(sample_json, rules_p, rules_c)
        if not flag:
            wb.write(sample)
        else:
            es.write(sample)
            nodes, Sedges = generate_nodes_Sedges(sample_json)
            output_node.writelines([json.dumps(n, ensure_ascii=False) + '\n' for n in nodes])
            output_edge.writelines([json.dumps(e, ensure_ascii=False) + '\n' for e in edges + Sedges])


if __name__ == '__main__':
    rules_p = "configure/Preprocess.json"
    rules_c = "configure/Rule.json"
    input_file = "/home/lmy/EventTraining/EventExtraction/data/data/test.txt"
    output_node = "/home/lmy/EventTraining/EventExtraction/data/Confirmed/nodes.json"
    output_edge = "/home/lmy/EventTraining/EventExtraction/data/Confirmed/edges.json"
    ensured_file = "/home/lmy/EventTraining/EventExtraction/data/Confirmed/ensure.txt"
    write_bakfile = input_file
    generate_file(input_file=input_file,
                  rules_p=rules_p,
                  rules_c=rules_c,
                  output_node=output_node,
                  output_edge=output_edge,
                  write_bakfile=write_bakfile,
                  ensured_file=ensured_file,
                  score=5.5,
    )
    if DEBUG:
        print(Counter(debug_pattern).most_common(10))


