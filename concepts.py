from pyconcepticon import Concepticon
from tabulate import tabulate
# path to concepticon
con = Concepticon()

urban = con.conceptlists["Urban-2011-160"]

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
                target,
                polysemies,
                overt
                ]]
print(tabulate(sorted(table, key=lambda x: int(x[0])), tablefmt="pipe", headers=["Number", "Source", "Target", "Polysemies", "OvertMarkings"]))

with open("relations-urban-2011.tsv", "w") as f:
    f.write("\t".join(["Number", "Source", "Target", "Polysemies",
                       "OvertMarkings"])+"\n")
    for row in sorted(table):
        f.write("\t".join(row)+"\n")

