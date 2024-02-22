graph-data:
	concepticon graph concept-lists/Zalizniak-2024-4583.tsv --graph-column=TARGET_CONCEPTS --format=tsv --weights=PolysemyByFamily,DerivationByFamily > graphs/dss.tsv
	concepticon graph concept-lists/List-2023-1308.tsv --graph-column=TARGET_CONCEPTS --format=tsv --weights=AffixFams > graphs/clips.tsv
	concepticon graph concept-lists/List-2023-1308.tsv --graph-column=TARGET_CONCEPTS --threshold=4 --threshold-property=AffixFams --format=tsv > graphs/list-2023-affix-colexifications-threshold-4.tsv
	concepticon graph concept-lists/List-2023-1308.tsv --graph-column=LINKED_CONCEPTS --threshold=3 --threshold-property=FullFams --format=tsv > graphs/list-2023-full-colexifications-threshold-3.tsv
	
