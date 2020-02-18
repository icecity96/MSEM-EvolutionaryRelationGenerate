import json
from conditions import meet_conditions

def get_Twords(Twords):
    """return trigger words. If trigger words are not restricted, a null value is returned
    :param Twords: trigger words (None|string|list)
    :return trigger words (None|list)
    """
    if type(Twords) == str:   # str: filename
        if Twords.endswith("json"): # json file
            triggers = json.load(open(Twords,encoding="utf8"))
            return triggers["trigger"]
        else:
            triggers = [line.strip() for line in open(Twords,encoding="utf8").readlines()]
            return triggers
    else:
        return Twords

def matched(sample, rule, mode="convert"):
    """
    Judge whether a sample is matched to a rule
    :param sample:
    :param rule:
    :param mode: convert or preprocess
    :return: boolean, edges, optional labels
    """
    if mode == "preprocess":
        return _matched_preprocess(sample, rule)
    else:
        return _matched_convert(sample, rule)


def _matched_preprocess(sample, rule):
    twords = get_Twords(rule["Twords"])
    labels = [label for label in sample["labels"]]
    edges = []
    pattern_r = rule["Pattern"]
    if twords is None: # which means no replace needed
        pattern_s = '-'.join([label[2] for label in labels])
        index = pattern_s.find(pattern_r)
        edges = []
        while index != -1:
            start = len([x for x in pattern_s[0:index].split('-') if len(x) > 0]) if index != 0 else 0
            end = start + len(pattern_r.split('-'))
            # meet meet_requirement?
            meet_requirement = meet_conditions(rule["Required"], labels[start: end], sample["text"]) if "Required" in rule else True
            if not meet_requirement:
                index = pattern_s.find(pattern_r, index + 1)
                continue
            # generate relations
            edges.extend(_generate_relations(rule["Edge"], labels[start: end], sample["text"]))
            # Return
            labels = labels[0:start] + [labels[start+i] for i in rule["Return"]] + labels[end:]
            pattern_s = '-'.join([label[2] for label in labels])
            index = pattern_s.find(pattern_r, index)
        if len(edges) > 0:
            return True, edges, labels
    # TODO: if Twords is not None
    return False, None, sample["labels"]

def _matched_convert(sample, rule):
    twords = get_Twords(rule["Twords"])
    text = sample["text"]
    edges = []
    labels = [[x for x in label] for label in sample["labels"]]
    if twords is not None:
        # replace trigger into T
        for index, label in enumerate(labels):
            if text[label[0]: label[1]] in twords:
                labels[index][2] = 'T'
    # TODO: SUPPORT REGEX? OR WRITE A FUNCTION TO EXPAND REGEX TO NORMAL?
    pattern_s = '-'.join([label[2] for label in labels])
    if pattern_s != rule["Pattern"]:
        return False, edges
    meet_requirement = meet_conditions(rule["Required"], labels, text) if "Required" in rule else True
    if not meet_requirement:
        return False, edges
    edges.extend(_generate_relations(rule["Edge"], labels, text))
    return True, edges


def _generate_relations(Edges, labels, text):
    edges = []
    for Edge in Edges:
        edge = {}
        for source in _get_edge_components_info(Edge, "source", labels, text):
            for target in _get_edge_components_info(Edge, "target", labels, text):
                if source == target:
                    continue
                for relation in _get_edge_components_info(Edge, "r", labels, text):
                    edge["source"] = source
                    edge["target"] = target
                    edge["r"] = relation
                    edge["attr"] = _get_edge_components_info(Edge, "attr", labels, text)[0]
                    edge["time"] = Edge["time"]
                    edges.append(edge)
    return edges


def _get_edge_components_info(Edge, field, labels, text):
    if type(Edge[field]) == int:
        try:
            component = labels[Edge[field]]
            if type(component[0]) == int:
                return [text[component[0]: component[1]]]
            else:
                return [text[c[0]: c[1]] for c in component]
        except:
            print(text)
    else:
        return [Edge[field]]


def format_json(sample):
    temp = {}
    temp["text"], temp["time"] = sample["text"].strip().rsplit(',', 1)
    labels = sorted(sample["labels"], key=lambda x: x[0])
    if "score" not in sample:
        temp["labels"], temp["relation"] = labels[:-1], labels[-1][2]
    else:
        temp["labels"] = labels
        temp["relation"] = sample["relation"]
    return temp
