import igraph
import networkx as nx
from pyconcepticon import Concepticon
from csvw.dsv import UnicodeDictReader, UnicodeWriter
from tabulate import tabulate

# we first load the affix colexification graph and then prepare it in such
# a form that we can retrieve the colexifications

# get index from concepticon gloss to concepticon ID
gloss2id = {c.gloss: c.id for c in Concepticon().conceptsets.values()}
id2gloss = {v: k for k, v in gloss2id.items()}

graph_ = igraph.read("data/colexification-affix.gml")

graph = nx.DiGraph()
id2node = {}

for idx in graph_.vs.indices:
    node = graph_.vs[idx]
    data = dict(node.attributes().items())
    graph.add_node(data["label"], **data)
    id2node[idx] = data["label"]

for edge in graph_.es:
    source, target = id2node[edge.source], id2node[edge.target]
    data = dict(edge.attributes().items())
    graph.add_edge(source, target, **data)

with open("affix-colexifications.tsv", "w") as f:
    f.write("Source\tSource_Concepticon_ID\tTarget\tTarget_Concepticon_ID\tAffix_Col_Families\tAffix_Col_Languages\n")
    for nA, nB, data in graph.edges(data=True):
        f.write("\t".join([
            nA,
            gloss2id[nA],
            nB,
            gloss2id[nB],
            str(data["family_count"]),
            str(data["language_count"])])+"\n")

# now check against the data by Urban
table = [[
    "Number",
    "Source",
    "Source_ID",
    "Source_Con",
    "Target",
    "Target_ID",
    "Target_Con",
    "Polysemies_Urban",
    "OvertMarkings_Urban",
    "Polysemies_CLICS",
    "OvertMarkingsFamily",
    "OppositeOvertMarkingsFamily",
    "OvertMarkingsLanguage",
    "OppositeOvertMarkingsLanguage"
    ]]
with UnicodeDictReader('relations-urban-2011.tsv', delimiter="\t") as reader:
    for row in reader:
        sgloss, tgloss = id2gloss[row["Source_ID"]], id2gloss[row["Target_ID"]]
        try:
            overt_fam = graph[sgloss][tgloss]["family_count"]
            overt_lang = graph[sgloss][tgloss]["language_count"]
        except:
            overt_fam = 0
            overt_lang = 0
            print(sgloss, tgloss)

        try:
            opp_fam = graph[tgloss][sgloss]["family_count"]
            opp_lang = graph[tgloss][sgloss]["language_count"]
        except:
            opp_fam = 0
            opp_lang = 0
            print(tgloss, sgloss)


        new_row = [
                row["Number"],
                row["Source"],
                row["Source_ID"],
                row["Source_Con"],
                row["Target"],
                row["Target_ID"],
                row["Target_Con"],
                row["Polysemies"],
                row["OvertMarkings"],
                "",
                int(overt_fam),
                int(overt_lang),
                int(opp_fam),
                int(opp_lang)]
        table += [new_row]

with UnicodeWriter("urban-vs-clips.tsv", delimiter="\t") as writer:
    writer.writerows(table)
