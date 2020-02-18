import json
from mapping import generate
from operations import *

if __name__ == '__main__':
    rules_p = json.load(open("configure/Preprocess.json", encoding="utf8"))["preprocess"]
    rules_c = json.load(open("configure/Rule.json", encoding="utf8"))["rules"]
    samples = open("data/sharing_bike.json", encoding="utf8").readlines()
    sample = samples[34]
    sample = format_json(json.loads(sample))
    print(generate(sample, rules_p, rules_c))
