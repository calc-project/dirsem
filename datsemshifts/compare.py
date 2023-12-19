from pyconcepticon import Concepticon
from itertools import combinations
from collections import defaultdict
from csvw.dsv import UnicodeWriter, UnicodeDictReader


con = Concepticon()

dss = con.conceptlists["Zalizniak-2020-2590"]
clips = con.conceptlists["List-2023-1308"]

common_concepts = {c.concepticon_gloss for c in dss.concepts.values() if
                   c.concepticon_gloss in [c2.concepticon_gloss for c2 in
                                        clips.concepts.values()] and
                   c.concepticon_gloss is not None
                   }




with UnicodeDictReader("big-table.tsv", delimiter="\t") as reader:
    dss_data = []
    for row in reader:
        dss_data += [row]

# unify representation to one graph
graph = defaultdict(lambda : defaultdict(lambda : {"Languages": [], "Words": [], "Directed": 0,
                              "Undirected": 0, "Polysemy": 0, "Derivation": 0,
                              "Other": 0}))
for row in dss_data:
    # check if polysemy or shift
    if row["Direction"] in ['—', '↔']:
        directed = 0
        undirected = 1
    elif row["Direction"] == "→":
        directed = 1
        undirected = 0
    elif row["Direction"] == "←":
        directed = 1
        undirected = 0
        row["SOURCE"], row["TARGET"] = row["TARGET"], row["SOURCE"]

    if row["Type"] == "Polysemy":
        polysemy = 1
        derivation = 0
        other = 1
    elif row["Type"] == "Derivation":
        polysemy = 0
        derivation = 1
        other = 1
    else:
        polysemy, derivation = 0, 0
        other = 1
    
    graph[row["SOURCE"]][row["TARGET"]]["Directed"] += directed
    graph[row["SOURCE"]][row["TARGET"]]["Undirected"] += undirected
    graph[row["SOURCE"]][row["TARGET"]]["Polysemy"] += undirected
    graph[row["SOURCE"]][row["TARGET"]]["Derivation"] += undirected
    graph[row["SOURCE"]][row["TARGET"]]["Other"] += undirected
    graph[row["SOURCE"]][row["TARGET"]]["Languages"] += [row["Language"]]
    graph[row["SOURCE"]][row["TARGET"]]["Words"] += [row["Word"]]


eng2con = {c.english: c.concepticon_gloss for c in dss.concepts.values() if
           c.english in graph}

common_concepts = {c for c in common_concepts if c in eng2con.values()}


# assemble common concepts in a table
concepts = {}
for concept in dss.concepts.values():
    if concept.concepticon_gloss in common_concepts:
        concepts[concept.concepticon_gloss] = [graph[concept.english]]
for concept in clips.concepts.values():
    if concept.concepticon_gloss in common_concepts:
        concepts[concept.concepticon_gloss] += [concept]

table = [[
    "Source", "Target", "Directed", "Undirected", "Derivation", "Polysemy",
    "Other",
    "OvertMarking_Languages", "OvertMarking_Families", "Polysemy_Languages",
    "Polysemy_Families"]]

for concept, (c1, c2) in concepts.items():
    edges = defaultdict(lambda : [0, 0, 0, 0, 0, 0, 0, 0, 0])
    for edge, vals in c1.items():
        if edge in eng2con:
            edges[eng2con[edge]][0] += vals["Directed"]
            edges[eng2con[edge]][1] += vals["Undirected"]
            edges[eng2con[edge]][2] += vals["Derivation"]
            edges[eng2con[edge]][3] += vals["Polysemy"]
            edges[eng2con[edge]][4] += vals["Other"]

    for edge in c2.attributes["target_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][5] = edge["AffixLngs"]
            edges[target][6] = edge["AffixFams"]

    for edge in c2.attributes["linked_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][7] = edge["FullLngs"]
            edges[target][8] = edge["FullFams"]


    for edge, vals in edges.items():
        if vals[0] or vals[1]:
            table += [[concept, edge] + vals]

with UnicodeWriter("dss-clips.tsv", delimiter="\t") as writer:
    writer.writerow(table[0])

    for row in table[1:]:
        writer.writerow(row)

