import json

QUOTATIONS = ["\"", "「", "“", "‘", "’", "”"]


def convert_single_line(sample, predict=True) -> tuple:
    """Convert a single line into a subgraph.
    Args:
        sample: A json string.
    Returns:
        tuple: (nodes, edges)
    """
    if predict:
        text, labels, relation = sample['text'], sample['labels'], sample['relation']
    else:
        text, labels = sample['text'], sample['labels']
        labels = sorted(labels, key=lambda x: x[0], reverse=True)
        labels, relation = labels[:-1], labels[-1][2]
    timestamp = text.split(',')[-1].strip()
    labels = sorted(labels, key=lambda x: x[0])
    nodes, edges = [], []
    # Rule 1: find if there exists <Object><Actor|Recipient>
    merged_labels = []
    for label_i, label_j in zip(labels[:-1], labels[1:]):
        if label_i[2] == 'Object' and label_j[2] in ['Recipient', 'Actor']:
            if label_i[1] == label_j[0] or (label_i[1] + 1 == label_j[0] and text[label_i[1]] in QUOTATIONS):
                feature_id, stakeholder_id = text[label_i[0]: label_i[1]], text[label_j[0]: label_j[1]]
                nodes.append((feature_id, {"node_type": "feature"}))
                nodes.append((stakeholder_id, {"node_type": "stakeholder"}))
                edges.append(
                    (stakeholder_id, feature_id, {"edge_type": "provide", "created_at": timestamp, "text": text}))
                merged_labels.append(label_i)
        if label_i[2] == label_j[2] and text[label_i[1]:label_j[0]] == '（': ## BOE （京东方）
            stakeholder1, stakeholder2 = text[label_i[0]: label_i[1]], text[label_j[0]: label_j[1]]
            nodes.append((stakeholder1, {"node_type": "stakeholder"}))
            nodes.append((stakeholder2, {"node_type": "stakeholder"}))
            edges.append((stakeholder1, stakeholder2, {"edge_type": "equal", "created_at": timestamp, "text": text}))

        # TODO: How to handle Attribute more properly? Now I simply remove it.
        if label_i[2] == 'Attribute':
            merged_labels.append(label_i)
    for label in merged_labels:
        labels.remove(label)
    # ==================================================================================================================

    if relation == "non" or relation == "res":
        comma_index = text.index(',')
        label_1, label_2 = [], []
        for label in labels:
            if label[0] < comma_index:
                label_1.append(list(label))
            else:
                label_2.append(list(label))
        if relation == "non":
            labels = [label_1, label_2]
        else:
            labels = [label_2 + label_1]
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

        # Rule5
        if relation == "Ori" and '-'.join(
                [label[2] for label in labels_item]) == "Actor-Action-Object-Action-Object":
            flags += 1
            stakeholder, action1, feature1, action2, feature2 = tuple(labels_item)
            stakeholder = text[stakeholder[0]: stakeholder[1]]
            action1, action2 = text[action1[0]: action1[1]], text[action2[0]: action2[1]]
            feature1, feature2 = text[feature1[0]: feature1[1]], text[feature2[0]: feature2[1]]
            nodes.append((stakeholder, {"node_type": "stakeholder"}))
            nodes.append((feature1, {"node_type": "feature"}))
            nodes.append((feature2, {"node_type": "feature"}))
            edges.append((stakeholder, feature1, {"edge_type": action1, "created_at": timestamp, "text": text}))
            edges.append((stakeholder, feature2, {"edge_type": action2, "created_at": timestamp, "text": text}))
            continue

        # Rule6:
        if relation == "Ori" and '-'.join(
                [label[2] for label in labels_item]) == "Actor-Action-Recipient-Object-Action-Object":
            flags += 1
            stakeholder, action1, stakeholder2, feature1, action2, feature2 = tuple(labels_item)
            stakeholder = text[stakeholder[0]: stakeholder[1]]
            stakeholder2 = text[stakeholder2[0]: stakeholder2[1]]
            action1, action2 = text[action1[0]: action1[1]], text[action2[0]: action2[1]]
            feature1, feature2 = text[feature1[0]: feature1[1]], text[feature2[0]: feature2[1]]
            nodes.append((stakeholder, {"node_type": "stakeholder"}))
            nodes.append((stakeholder2, {"node_type": "stakeholder"}))
            nodes.append((feature1, {"node_type": "feature"}))
            nodes.append((feature2, {"node_type": "feature"}))
            edges.append((stakeholder, feature1, {"edge_type": action1, "created_at": timestamp, "text": text}))
            edges.append((stakeholder, feature2, {"edge_type": action2, "created_at": timestamp, "text": text}))
            edges.append((stakeholder, stakeholder2, {"edge_type": action1, "created_at": timestamp, "text": text}))
            edges.append((stakeholder2, feature1, {"edge_type": action1, "created_at": timestamp, "text": text}))
            edges.append((stakeholder2, feature2, {"edge_type": action2, "created_at": timestamp, "text": text}))
            continue

        # TODO: Other Format
        pattern = '-'.join([label[2] for label in labels_item])
        stakeholders, features = [], []
        for label in labels_item:
            if label[2] == 'Actor' or label[2] == 'Recipient':
                stakeholders.append(text[label[0]: label[1]])
                nodes.append((text[label[0]: label[1]], {"node_type": "stakeholder"}))
            elif label[2] == 'Object':
                features.append(text[label[0]: label[1]])
                nodes.append((text[label[0]: label[1]], {"node_type": "feature"}))
        for index, stakeholder in enumerate(stakeholders[:-1]):
            for node2 in stakeholders[index + 1:]:
                edges.append((stakeholder, node2,
                              {"edge_type": "uf1", "created_at": timestamp, "text": text, "pattern": pattern}))
            for node2 in features:
                edges.append((stakeholder, node2,
                              {"edge_type": "uf2", "created_at": timestamp, "text": text, "pattern": pattern}))
        # =============================================================================================================

        # Rule 7: 并列句处理 、 和 及
        # FIXME: Find Right Way
        '''
        paralleling_chars = ['、', '和', '及']
        new_edges = []
        for labels_item in labels:
            for index, label in enumerate(labels_item[:-1]):
                if label[2] == labels_item[index + 1][2] and label[2] in ["Actor", "Recipient"]:
                    if label[1] < labels_item[index + 1][1] and text[label[1]: labels_item[index + 1][1]] in paralleling_chars:
                        node1, node2 = text[label[0]: label[1]], text[labels_item[index + 1][0]: labels_item[index + 1][1]]
                        for edge in edges:
                            if edge[0] == node1 and edge[1] == node2:
                                continue
                            new_edges.append(edge)
        edges = new_edges
        '''
    return nodes, edges
