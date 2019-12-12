import json

QUOTATIONS = ["\"", "「", "“", "‘", "’", "”"]


def convert_single_line(sample) -> tuple:
    """Convert a single line into a subgraph.
    Args:
        sample: A json string.
    Returns:
        tuple: (nodes, edges)
    """
    text, labels, relation = sample['text'], sample['labels'], sample['relation']
    timestamp = text.split(',')[-1].strip()
    labels = sorted(labels, key=lambda x: x[0])
    nodes, edges = [], []
    # Rule 1: find if there exists <Object><Actor|Recipient>
    merged_labels = []
    for label_i, label_j in zip(labels[:-1], labels[1:]):
        if label_i[2] == 'Object' and label_j[2] in ['Recipient', 'Actor']:
            if label_i[1] == label_j[0] or (label_i[1]+1 == label_j[0] and text[label_i[1]] in QUOTATIONS) :
                feature_id, stakeholder_id = text[label_i[0]: label_i[1]], text[label_j[0]: label_j[1]]
                nodes.append((feature_id, {"node_type": "service_feature"}))
                nodes.append((stakeholder_id, {"node_type": "stakeholder"}))
                edges.append((stakeholder_id, feature_id, {"edge_type": "provide", "created_at": timestamp, "text": text}))
                merged_labels.append(label_i)
    for label in merged_labels:
        labels.remove(label)
    # ==================================================================================================================

    if relation == "non":
        comma_index = text.index(',')
        label_1, label_2 = [], []
        for label in labels:
            if label[0] < comma_index:
                label_1.append(list(label))
            else:
                label_2.append(list(label))
        labels = [label_1, label_2]
    else:
        labels = [list(labels)]
    flags = 0
    for labels_item in labels:
        # Rule 2: If less than one entity ignores
        if len(labels_item) < 2:
            flags += 1
            continue
        # Rule 3: Most simple Pattern <Actor> <Action> <Recipient>
        if '-'.join([label[2] for label in labels_item]) == "Actor-Action-Recipient":
            flags += 1
            stakeholder_i, stakeholder_j, action = labels_item[0], labels_item[2], labels_item[1]
            stakeholder_i = text[stakeholder_i[0]: stakeholder_i[1]]
            stakeholder_j = text[stakeholder_j[0]: stakeholder_j[1]]
            action = text[action[0]: action[1]]
            # No self-loops
            if stakeholder_i == stakeholder_j:
                continue
            nodes.append((stakeholder_i, {"node_type": "stakeholder"}))
            nodes.append((stakeholder_j, {"node_type": "stakeholder"}))
            edges.append((stakeholder_i, stakeholder_j, {"edge_type": action, "created_at": timestamp, "text": text}))
            continue
        # Rule 4: Basic Pattern <Actor> <Action> <Recipient>
        if '-'.join([label[2] for label in labels_item]) == "Actor-Action-Object":
            flags += 1
            stakeholder, feature, action = labels_item[0], labels_item[2], labels_item[1]
            stakeholder = text[stakeholder[0]: stakeholder[1]]
            feature = text[feature[0]: feature[1]]
            action = text[action[0]: action[1]]
            nodes.append((stakeholder, {"node_type": "stakeholder"}))
            nodes.append((feature, {"node_type": "feature"}))
            edges.append((stakeholder, feature, {"edge_type": action, "created_at": timestamp, "text": text}))
            continue
        # =============================================================================================================
    return nodes, edges, len(labels) == flags
