"""
Code compares inferred and proposed links for various collections on overt marking and semantic shift.

"""
from pyconcepticon import Concepticon, models
from tabulate import tabulate
from collections import defaultdict
from scipy.stats import kendalltau, spearmanr, binomtest
import itertools
from pathlib import Path

def get_conceptlists():
    path = Path(__file__).parent / "concept-lists"
    return {
            "Urban-Overt-Marking": [
                "OvertMarking", "Polysemy",
                models.Conceptlist.from_file(path / "Urban-2011-160.tsv")],
            "Urban-Indo-Aryan": [
                "IndoAryanShift", "Polysemy",
                models.Conceptlist.from_file(path / "Urban-2011-160.tsv")],
            "Winter-Overt-Marking": [
                "OvertMarking", "Polysemy",
                models.Conceptlist.from_file(path / "Winter-2022-98.tsv")],
            "List-Partial-Colexifications": [
                "AffixFams", "FullFams",
                models.Conceptlist.from_file(path / "List-2023-1308.tsv")],
            "Zalizniak-Derivation": [
                "DerivationByFamily", "PolysemyByFamily",
                models.Conceptlist.from_file(path / "Zalizniak-2024-4583.tsv")],
            "Zalizniak-Polysemy": [
                "PolysemyByFamily", "PolysemyByFamily",
                models.Conceptlist.from_file(path / "Zalizniak-2024-4583.tsv")],
            }


def get_links(
        lists 
        ):
    """
    Compute links from the concept lists.

    Returns: links (dictionary), table (list)
    """
    table = []
    linkd = defaultdict(lambda : {
        k: [0, 0] for k in lists})
    for lst, (target_concept, linked_concept, cl) in lists.items():
        linked = [c for c in cl.concepts.values() if c.concepticon_id]
        links = set()
        for c in cl.concepts.values():
            for t in c.attributes["target_concepts"]:
                c2 = cl.concepts[t["ID"]]
                weight = t[target_concept]
                if weight:
                    links.add((c.id, t["ID"]))
                if c.concepticon_id and c2.concepticon_id:
                    linkd[c.concepticon_gloss, c2.concepticon_gloss][lst][0] = weight
            for t in c.attributes["linked_concepts"]:
                c2 = cl.concepts[t["ID"]]
                weight = t[linked_concept]
                if c.concepticon_id and c2.concepticon_id:
                    linkd[c.concepticon_gloss, c2.concepticon_gloss][lst][1] = weight
        table += [[
            lst,
            len(cl.concepts),
            len(linked),
            len(set(links))
            ]]
    return linkd, table


def compare_lists(
        lists, 
        links, 
        list_a, 
        list_b, 
        threshold_a=2, 
        threshold_b=2,
        smooth=0.001,):
    # assemble data for list vs. zalizniak
    visited = set()
    predictions = []
    
    glosses_1 = {c.concepticon_gloss for c in
                     lists[list_a][2].concepts.values()}
    glosses_2 = {c.concepticon_gloss for c in
                 lists[list_b][2].concepts.values()}
    selected_glosses = {c for c in glosses_1 if c in glosses_2}
    
    matches = 0
    corrsA, corrsB = [], []
    prediction_idx = 0
    for (c1, c2), vals in list(links.items()):
        if c1 in selected_glosses and c2 in selected_glosses:
            if (c1, c2) not in visited:
                visited.add((c2, c1))
                directed_a1, undirected_a = vals[list_a]
                directed_a2 = links[c2, c1][list_a][0]
    
                directed_b1, undirected_b = vals[list_b]
                directed_b2 = links[c2, c1][list_b][0]
    
                if (directed_a1 >= threshold_a or directed_a2 >= threshold_a) and \
                        (directed_b1 >= threshold_b or directed_b2 >= threshold_b):
                    if directed_a1 > directed_a2 and (directed_a1 + smooth) / \
                            (directed_a2 + smooth) > 1.1: 
                        direction_a = 1
                    elif directed_a1 < directed_a2 and (directed_a2 + smooth) / \
                            (directed_a1 + smooth) > 1.1:
                        direction_a = -1
                    else:
                        direction_a = 0
    
                    if directed_b1 > directed_b2 and (directed_b1 + smooth) / (directed_b2 + smooth) > 1.1:
                        direction_b = 1
                    elif directed_b1 < directed_b2 and (directed_b2 + smooth) / (directed_b1 + smooth) > 1.1:
                        direction_b = -1
                    else:
                        direction_b = 0
                    
                    prediction_idx += 1
                    predictions += [[prediction_idx, c1, c2, direction_a, direction_b, directed_a1, directed_a2,
                                     directed_b1, directed_b2]]
                    if direction_a == direction_b:
                        matches += 1
                    corrsA += [(directed_a1 + smooth) / (directed_a2 + smooth)]
                    corrsB += [(directed_b1 + smooth) / (directed_b2 + smooth)]
    
    r, p = spearmanr(corrsA, corrsB)
    if len(predictions) == 0:
        summary = []
    else:
        summary = [
            ["Match Accuracy", matches / len(predictions)],
            ["Number of Tests", len(predictions)],
            ["Spearman's R", "{0:.4f}".format(r)],
            ["Significance", "{0:.4f}".format(p)]]
    return predictions, summary

concept_lists = get_conceptlists()
linked_data, summary_table = get_links(concept_lists)

print("# Summary on the Concept Lists")
print(
        tabulate(
            summary_table, 
            tablefmt="pipe", 
            headers=["Dataset", "Glosses", "Concepts (Linked to Concepticon)",
                     "Shifts"]))

paired_comparisons = [
        [
            "Urban-Overt-Marking", 1,
            "Urban-Indo-Aryan", 1],
        [
            "Urban-Overt-Marking", 1,
            "Zalizniak-Polysemy", 1],
        [
            "Winter-Overt-Marking", 1,
            "Urban-Indo-Aryan", 1],
        [
            "Winter-Overt-Marking", 1,
            "Zalizniak-Polysemy", 1],
        [
            "List-Partial-Colexifications", 2,
            "Urban-Indo-Aryan", 1],
        [
            "List-Partial-Colexifications", 3,
            "Zalizniak-Polysemy", 2],
        [
            "List-Partial-Colexifications", 3,
            "Zalizniak-Derivation", 2],
        [
            "Zalizniak-Derivation", 2,
            "Zalizniak-Polysemy", 2],
        ]
general_summary = []
for list_a, threshold_a, list_b, threshold_b in paired_comparisons:
    predictions, summary = compare_lists(
            concept_lists,
            linked_data,
            list_a,
            list_b,
            threshold_a=threshold_a,
            threshold_b=threshold_b
            )
    if summary:
        general_summary += [[list_a, list_b] + [row[1] for row in summary]]
print("# Summary on Dataset Comparisons")
print(tabulate(
    general_summary,
    tablefmt="pipe",
    headers = ["List_A", "List_B", "Match Accuracy", "Test Items", "Spearman's R", "Significance"]
    ))



