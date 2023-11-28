from pyconcepticon import Concepticon, models
from tabulate import tabulate
from pynorare import NoRaRe
import json
# path to concepticon
con = Concepticon()
nor = NoRaRe('repos/norare-data', concepticon=con)

# get mappings to brysbaert
id2ratings = {v["concepticon_id"]:
              "{0:.2f}".format(v["english_concreteness_mean"]) for k, v in
               nor.datasets["Brysbaert-2014-Concreteness"].concepts.items()}


clist = models.Conceptlist.from_file("Winter-2022-100/Winter-2022-100.tsv")

# get concept to concepticon ID to have all data at hand
concept2id = {}
for concept in clist.concepts.values():
    concept2id[concept.english] = int(concept.concepticon_id)


table = []
for concept in clist.concepts.values():
    targets = json.loads(concept.attributes["target_concepts"])
    for target in targets:
        print(target["name"])
        table += [[
            concept.number,
            concept.english,
            concept.concepticon_id,
            id2ratings.get(int(concept.concepticon_id), ""),
            clist.concepts[target["id"]].english,
            clist.concepts[target["id"]].concepticon_id,
            id2ratings.get(int(clist.concepts[target["id"]].concepticon_id), ""),
            target["polysemy"],
            target["overt_marking"]
            ]]

header = ["Number", "Source", "Source_ID", "Source_Con", "Target", "Target_ID",
          "Target_Con", "Polysemies", "OvertMarkings"]


print(tabulate(sorted(table, key=lambda x: int(x[0])), tablefmt="pipe",
               headers=header))

with open("relations-winter-2022.tsv", "w") as f:
    f.write("\t".join(header)+"\n")
    for row in sorted(table):
        f.write("\t".join([str(x) for x in row])+"\n")

