# Data and Code Accompanying the Study "Direction of Semantic Change"

When using the data, please quote the original paper (currently under review):

> Bocklage, Katja; Di Natale, Anna; Tjuka, Annika; and List, Johann-Mattis (2024): Directional Tendencies in Semantic Change. [paper currently under review]

## Installation
To install all relevant software packages needed to repeat the analyzes described in the paper, please install all Python packages with `pip`:

```shell
pip install -r requirements.txt
```

## Running the Code

We provide one main script that carries out all analyses described in the paper. This script can be run from the commandline:

```shell
python compare-shifts.py
```

The output will be displayed on the terminal (results from there are reported in the paper).

## Exploratory Data Analysis

For the exploratory data analysis, we used the TSV file [`semantic-shifts/frequent-shifts.tsv`](semantic-shifts/frequent-shifts.tsv), which we analyzed with the help of [Cytoscape](https://cytoscape.org). See [Tjuka (2024)](https://doi.org/10.15475/calcip.2024.1.2) for a detailed tutorial illustrating how data can be analyzed with Cytoscape.
