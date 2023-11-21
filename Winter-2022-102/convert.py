from csvw.dsv import UnicodeDictReader
from pysem import to_concepticon
from collections import defaultdict
import json

check = defaultdict(list)
with UnicodeDictReader("asymmetry/data/asymmetry.csv") as reader:
    for row in reader:
        idx = row["ID"]
        polysemy, oma, omar = row["Polysemy"], row["OvertMarking"], row["OvertMarkingReverse"]
        check[idx] += [(int(polysemy), int(oma), int(omar))]


# must correct for error in data
correct = {
        "soil": "soil/earth",
        "Milky Way": "milky way"
        }

data = defaultdict(list)
with UnicodeDictReader("asymmetry/data/asymmetry.csv") as reader:
    for row in reader:
        concept = row["ConceptComplete"]
        data[correct.get(concept, concept)] += [row]

# populate the table
# give an identifier to the concept
row2idx = {}
for i, (concept, row) in enumerate(data.items()):
    idx = i+1
    row2idx[concept] = idx

graph = defaultdict(lambda: {"sources": [], "targets": []})
for concept, rows in data.items():
    # add info on 
    for row in rows:
        oma, omar, polysemy = (
                int(row["OvertMarking"]),
                int(row["OvertMarkingReverse"]),
                int(row["Polysemy"]))
        source, target = row["PairName"].split("~")

        if concept == source:
            graph[concept]["targets"] += [
                    {
                        "name": target,
                        "id": "Winter-2022-102-{0}".format(row2idx[target]),
                        "overt_marking": oma,
                        "polysemy": polysemy
                        }]
            # if reverse marking exists, add it to sources
            if omar:
                graph[concept]["sources"] += [
                        {
                            "name": target,
                            "id": "Winter-2022-102-{0}".format(row2idx[target]),
                            "overt_marking": omar,
                            "polysemy": polysemy
                            }]
        elif concept == target:
            graph[concept]["sources"] += [
                    {
                        "name": source,
                        "id": "Winter-2022-102-{0}".format(row2idx[target]),
                        "overt_marking": oma,
                        "polysemy": polysemy
                        }]
            # if reverse marking exists, add it to sources
            if omar:
                graph[concept]["targets"] += [
                        {
                            "name": source,
                            "id": "Winter-2022-102-{0}".format(row2idx[target]),
                            "overt_marking": omar,
                            "polysemy": polysemy
                            }]

with open("edges.tsv", "w") as f:
    f.write("Source\tTarget\tPolysemy\tOvertMarking\n")
    for node in graph:
        if graph[node]["targets"]:
            for target in graph[node]["targets"]:
                f.write("{0}\t{1}\t{2}\t{3}\n".format(
                    node,
                    target["name"],
                    target["polysemy"],
                    target["overt_marking"]))

with open("Winter-2022-102.tsv", "w") as f:
    f.write("ID\tENGLISH\tCONCEPTICON_ID\tCONCEPTICON_GLOSS\tSOURCES\tTARGETS\n")
    table = []
    for concept in graph:
        # get concept mappings
        mappings = to_concepticon([{"gloss": concept}])[concept]
        if mappings:
            cid, cgl = mappings[0][0], mappings[0][1]
        else:
            cid, cgl = "", ""
        table += [[
            "Winter-2022-102-{0}".format(row2idx[concept]),
            concept,
            cid, 
            cgl,
            json.dumps(graph[concept]["sources"]),
            json.dumps(graph[concept]["targets"]),
            ]]
    for row in sorted(table):
        f.write("\t".join(row)+"\n")
