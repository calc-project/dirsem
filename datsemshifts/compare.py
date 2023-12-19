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
graph = defaultdict(
        lambda : defaultdict(
            lambda : {
                "Directed": 0,
                "Directed_Evidence": [],
                "Directed_Languages": [],
                "Directed_Words": [],
                "Undirected": 0, 
                "Undirected_Evidence": [],
                "Undirected_Languages": [],
                "Undirected_Words": []
                }))

for row in dss_data:
    s, t = row["SOURCE"], row["TARGET"]
    # check if polysemy or shift
    if row["Direction"] in ['—', '↔']:
        graph[s][t]["Undirected"] += 1
        graph[t][s]["Undirected"] += 1
        graph[s][t]["Undirected_Evidence"] += [row["Type"]]
        graph[t][s]["Undirected_Evidence"] += [row["Type"]]
        graph[s][t]["Undirected_Languages"] += [row["Language"]]
        graph[t][s]["Undirected_Languages"] += [row["Language"]]
        graph[s][t]["Undirected_Words"] += [row["Word"]]
        graph[t][s]["Undirected_Words"] += [row["Word"]]

    elif row["Direction"] == "→":
        graph[s][t]["Directed"] += 1
        graph[s][t]["Directed_Evidence"] += [row["Type"]]
        graph[s][t]["Directed_Languages"] += [row["Language"]]
        graph[s][t]["Directed_Words"] += [row["Word"]]
    
    elif row["Direction"] == "←":
        graph[t][s]["Directed"] += 1
        graph[t][s]["Directed_Evidence"] += [row["Type"]]
        graph[t][s]["Directed_Languages"] += [row["Language"]]
        graph[t][s]["Directed_Words"] += [row["Word"]]


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
    "Source", 
    "Target", 
    "Directed", 
    "Directed_Polysemy",
    "Directed_Derivation",
    "Directed_Other",
    "Undirected", 
    "Undirected_Polysemy",
    "Undirected_Derivation",
    "Undirected_Other",
    "OvertMarking_Languages", 
    "OvertMarking_Families", 
    "Polysemy_Languages",
    "Polysemy_Families"
    ]]

for concept, (c1, c2) in concepts.items():
    edges = defaultdict(lambda : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    for edge, vals in c1.items():
        if edge in eng2con:
            edges[eng2con[edge]][0] += vals["Directed"]
            edges[eng2con[edge]][1] += vals["Directed_Evidence"].count("Polysemy")
            edges[eng2con[edge]][2] += vals["Directed_Evidence"].count("Derivation")
            edges[eng2con[edge]][3] += len([x for x in
                                            vals["Directed_Evidence"] if
                                            x not in ["Polysemy",
                                                      "Derivation"]])
            edges[eng2con[edge]][4] += vals["Undirected"]
            edges[eng2con[edge]][5] += vals["Undirected_Evidence"].count("Polysemy")
            edges[eng2con[edge]][6] += vals["Undirected_Evidence"].count("Derivation")
            edges[eng2con[edge]][7] += len([x for x in
                                            vals["Undirected_Evidence"] if
                                            x not in ["Polysemy",
                                                      "Derivation"]])


    for edge in c2.attributes["target_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][8] = edge["AffixLngs"]
            edges[target][9] = edge["AffixFams"]

    for edge in c2.attributes["linked_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][10] = edge["FullLngs"]
            edges[target][11] = edge["FullFams"]


    for edge, vals in edges.items():
        if edge and (vals[0] or vals[1]):
            table += [[concept, edge] + vals]

with UnicodeWriter("dss-clips.tsv", delimiter="\t") as writer:
    writer.writerow(table[0])

    for row in table[1:]:
        writer.writerow(row)

