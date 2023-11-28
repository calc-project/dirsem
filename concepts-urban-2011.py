from pyconcepticon import Concepticon
from tabulate import tabulate
from pynorare import NoRaRe
# path to concepticon
con = Concepticon()
nor = NoRaRe('repos/norare-data', concepticon=con)

# get mappings to brysbaert
id2ratings = {v["concepticon_id"]:
              "{0:.2f}".format(v["english_concreteness_mean"]) for k, v in
               nor.datasets["Brysbaert-2014-Concreteness"].concepts.items()}

urban = con.conceptlists["Urban-2011-160"]

# get concept to concepticon ID to have all data at hand
concept2id = {}
for concept in urban.concepts.values():
    concept2id[concept.english] = int(concept.concepticon_id)

reps = {
        "mirrow": "mirror",
        "straw/hay": "straw",
        "cheeck": "cheek",
        }

table = []
for concept in urban.concepts.values():
    if concept.attributes["semantic_change"]:
        print(concept.attributes["semantic_change"])
        # get the information, split by space
        for text in concept.attributes["semantic_change"].split("; "):
            # parse the data now
            data_a, data_b = text.split("» (")
            number = data_a.split(" ")[0][1:-1]
            source = data_a.split(">")[0].split("«")[1][:-2]
            target = data_a.split(">")[1].strip()[1:]

            polysemies = data_b.split(" ")[0]
            overt = data_b.split(", ")[1].split(" ")[0]
            table += [[
                number,
                source,
                str(concept2id[source]),
                id2ratings.get(concept2id[source], ""),
                reps.get(target, target),
                str(concept2id[reps.get(target, target)]),
                id2ratings.get(concept2id[reps.get(target, target)], ""),
                polysemies,
                overt
                ]]

header = ["Number", "Source", "Source_ID", "Source_Con", "Target", "Target_ID",
          "Target_Con", "Polysemies", "OvertMarkings"]


print(tabulate(sorted(table, key=lambda x: int(x[0])), tablefmt="pipe",
               headers=header))

with open("relations-urban-2011.tsv", "w") as f:
    f.write("\t".join(header)+"\n")
    for row in sorted(table):
        f.write("\t".join(row)+"\n")

