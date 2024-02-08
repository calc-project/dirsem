from pyconcepticon import Concepticon, models
from tabulate import tabulate
from collections import defaultdict

lists = {
        "Urban-2011-160": "",
        "Winter-2022-98": "",
        "List-2023-1308": "",
        "Zalizniak-2024-4583": ""
        }
for k in lists:
    lists[k] = models.Conceptlist.from_file("lists/" + k + ".tsv")

name2id = {}
cl = lists["Zalizniak-2024-4583"]
for c in cl.concepts.values():
    name2id[c.english] = c.id
# correct the jsons
for c in cl.concepts.values():
    for t in c.attributes["target_concepts"]:
        t["ID"] = name2id[t["NAME"]]
    for t in c.attributes["linked_concepts"]:
        t["ID"] = name2id[t["NAME"]]



table = []

linkd = defaultdict(lambda : {
    "Urban-2011-160": [0, 0],
    "List-2023-1308": [0, 0],
    "Winter-2022-98": [0, 0],
    "Zalizniak-2024-4583": [0, 0]
    })

for lst, cl in lists.items():
    linked = [c for c in cl.concepts.values() if c.concepticon_id]
    links = set()
    for c in cl.concepts.values():
        for t in c.attributes["target_concepts"]:
            links.add((c.id, t["ID"]))
            c2 = cl.concepts[t["ID"]]
            weight = t[{
                    "List-2023-1308": "AffixFams",
                    "Urban-2011-160": "OvertMarking",
                    "Winter-2022-98": "OvertMarking",
                    "Zalizniak-2024-4583": "Polysemy"
                    }[lst]]
            if c.concepticon_id and c2.concepticon_id:
                linkd[c.concepticon_gloss, c2.concepticon_gloss][lst][0] = weight
        for t in c.attributes["linked_concepts"]:
            c2 = cl.concepts[t["ID"]]
            weight = t[{
                    "List-2023-1308": "FullFams",
                    "Urban-2011-160": "Polysemy",
                    "Winter-2022-98": "Polysemy",
                    "Zalizniak-2024-4583": "Polysemy"
                    }[lst]]
            if c.concepticon_id and c2.concepticon_id:
                linkd[c.concepticon_gloss, c2.concepticon_gloss][lst][1] = weight
                      #linkd[c.concepticon_gloss, c2.concepticon_gloss[lst][1] = weight


    table += [[
        lst,
        len(cl.concepts),
        len(linked),
        len(set(links))
        ]]
print(tabulate(table))

# assemble data for list vs. zalizniak
visited = set()
predictions = []

glosses_1= {c.concepticon_gloss for c in
                 lists["List-2023-1308"].concepts.values()}
glosses_2 = {c.concepticon_gloss for c in
             lists["Zalizniak-2024-4583"].concepts.values()}

selected_glosses = {c for c in glosses_1 if c in glosses_2}

matches = 0
for (c1, c2), vals in list(linkd.items()):
    if c1 in selected_glosses and c2 in selected_glosses:
        if (c1, c2) not in visited:
            visited.add((c2, c1))
            dc, fc = vals["List-2023-1308"]
            dco, fco = linkd[c2, c1]["List-2023-1308"]

            dz, fz = vals["Zalizniak-2024-4583"]
            dzo, fzo = linkd[c2, c1]["Zalizniak-2024-4583"]

            if dc and fc and (dc > 3 or dco > 3):
                if dc > dco and (dc + 0.001) / (dco + 0.001) > 1.5: 
                    direction = 1
                elif dc < dco and (dco + 0.001) / (dc + 0.001) > 1.5:
                    direction = -1
                else:
                    direction = 0
            # get the "true" value
            if (dz and fz) or (dzo and fzo):
                if dz > dzo and (dz + 0.001) / (dzo + 0.001) > 1.5:
                    direction2 = 1
                elif dz < dzo and (dzo + 0.001) / (dz + 0.001) > 1.5:
                    direction2 = -1
                else:
                    direction2 = 0

                # check for prediction
                if dz > 3 or dzo > 3:
                    predictions += [[c1, c2, direction, direction2, dc, dco,
                                     dz, dzo]]
                    if direction == direction2:
                        matches += 1
print(tabulate(predictions))
print(matches / len(predictions))

