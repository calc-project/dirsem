graph-data:
	concepticon graph concept-lists/Zalizniak-2024-4853.tsv --graph-column=TARGET_CONCEPTS --format=tsv --weights=PolysemyByFamily,DerivationByFamily > graphs/dss.tsv
	concepticon graph concept-lists/List-2023-1308.tsv --graph-column=TARGET_CONCEPTS --format=tsv --weights=AffixFams > graphs/clips.tsv
