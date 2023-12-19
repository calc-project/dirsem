from pyconcepticon import Concepticon
from itertools import combinations
from collections import defaultdict
from csvw.dsv import UnicodeWriter

con = Concepticon()

dss = con.conceptlists["Zalizniak-2020-2590"]
clips = con.conceptlists["List-2023-1308"]

common_concepts = {c.concepticon_gloss for c in dss.concepts.values() if
                   c.concepticon_gloss in [c2.concepticon_gloss for c2 in
                                        clips.concepts.values()] and
                   c.concepticon_gloss is not None
                   }

# assemble common concepts in a table
concepts = {}
for concept in dss.concepts.values():
    if concept.concepticon_gloss in common_concepts:
        concepts[concept.concepticon_gloss] = [concept]
for concept in clips.concepts.values():
    if concept.concepticon_gloss in common_concepts:
        concepts[concept.concepticon_gloss] += [concept]

table = [[
        "Source", "Target", "DatSemShifts", "CLIPS_Languages", "CLIPS_Families", "PolysemyDSS", "PolysemyCLIPS_Languages", "PolysemyCLIPS_Families"
        ]]
for concept, (c1, c2) in concepts.items():
    edges = defaultdict(lambda : [0, 0, 0, 0, 0, 0])
    for edge in c1.attributes["target_concepts"]:
        target = dss.concepts[edge["ID"]].concepticon_gloss
        weight = edge["Weight"]
        if target in common_concepts:
            edges[target][0] = weight
    for edge in c2.attributes["target_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][1] = edge["AffixLngs"]
            edges[target][2] = edge["AffixFams"]

    for edge in c1.attributes["linked_concepts"]:
        target = dss.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            weight = edge["Weight"]
            edges[target][3] = weight

    for edge in c2.attributes["linked_concepts"]:
        target = clips.concepts[edge["ID"]].concepticon_gloss
        if target in common_concepts:
            edges[target][4] = edge["FullLngs"]
            edges[target][5] = edge["FullFams"]


    for edge, (a, b, c, d, e, f) in edges.items():
        if a or d:
            table += [[concept, edge, a, b, c, d, e, f]]

with UnicodeWriter("dss-clips.tsv", delimiter="\t") as writer:
    writer.writerow(table[0])

    for row in sorted(table[1:]):
        writer.writerow(row)

