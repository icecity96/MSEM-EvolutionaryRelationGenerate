

def _adjacency_conditions(condition, labels, text):
    # The two components are directly connected
    obj1, obj2 = labels[condition["obj1"]], labels[condition["obj2"]]
    if obj1[1] == obj2[0]:
        return True
    if "ignore" in condition:
        ignores = [line.strip() for line in open(condition["ignore"], encoding="utf-8").readlines()]
        if text[obj1[1]: obj2[0]] in ignores:
            return True
    return False

def _special_words(condition, labels, text):
    obj1, obj2 = labels[condition["obj1"]], labels[condition["obj2"]]
    spwords = [line.strip() for line in open(condition["words"], encoding="utf-8").readlines()]
    if text[obj1[1]: obj2[0]] in spwords:
        return True

CONDITION_DICT = {
    "adjacency": _adjacency_conditions,
    "special_words": _special_words,
}

def meet_conditions(conditions, labels, text):
    return all([_meets_conditions(condition, labels, text) for condition in conditions])

def _meets_conditions(condition, labels, text):
    return CONDITION_DICT[condition["con"]](condition, labels, text)

