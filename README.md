# ProFACT - Protein FASTA Analysis and Comparison Tool

> A pip-installable Python CLI for protein FASTA quality control, duplicate detection and dataset comparison.

## Subject

Bioinformatics workflows often use protein FASTA files after downloading data from UniProt, Swiss-Prot, RefSeq or Ensembl/NCBI, filtering protein datasets, or running protein prediction pipelines. Checking what changed between two versions of such files usually requires custom scripts, shell commands and separate tools.

**ProFACT** provides one small Python package for a focused protein FASTA workflow:

1. **Inspect** - compute statistics for protein FASTA files: sequence count, total/min/max/mean/median length, N50 and amino acid composition.
2. **Validate** - detect empty records, unknown residues (`X`), stop symbols (`*`) and non-standard or invalid amino acid characters.
3. **Find duplicates** - detect repeated IDs and group identical protein sequences found under different IDs.
4. **Compare** - report IDs added, removed and changed between two FASTA files, including changed lengths and duplicate cluster changes.
5. **Report** - generate a combined single-file report with statistics, validation summary and duplicate analysis.

---

## Features

- Plain and gzipped protein FASTA support (`.fa`, `.fasta`, `.faa`, `.fa.gz`, `.fasta.gz`, `.faa.gz`)
- Protein-specific statistics: length distribution, N50 and amino acid composition
- Quality checks: `X`, `*`, invalid amino acid characters and empty records
- Duplicate detection: repeated IDs and identical sequences under different IDs
- Exact duplicate clustering
- Comparison of two protein FASTA files:
  - added IDs
  - removed IDs
  - changed sequences
  - changed sequence lengths
  - changed duplicate clusters
- Output formats: text, TSV and JSON for all commands; HTML for statistics and full reports
- Pure Python, no heavy bioinformatics dependencies
- Local installation via `pip install -e .`

---

## Installation

```bash
pip install -e .
```

For running tests:

```bash
pip install -e ".[test]"
python3 -m pytest -q
```

---

## Usage

```bash
# Inspect a protein FASTA file
profact stats -i swissprot_subset.fasta

# Export statistics as JSON
profact stats -i swissprot_subset.fasta -fmt json -o stats.json

# Validate protein records
profact validate -i proteins.fasta.gz

# Detect identical protein sequences
profact duplicates -i proteins.fasta

# Compare raw and filtered protein datasets
profact compare -f1 raw_proteins.fasta -f2 filtered_proteins.fasta

# Export comparison as JSON
profact compare -f1 old_uniprot.fasta -f2 new_uniprot.fasta -fmt json -o compare.json

# Generate a full HTML report
profact report -i proteins.fasta -fmt html -o output/report.html

# Generate a full text report
profact report -i proteins.fasta
```

Generated files can be kept in `output/`, for example:

```bash
profact stats -i data/proteins.fasta -fmt json -o output/stats.json
profact validate -i data/proteins.fasta -fmt tsv -o output/validation.tsv
profact compare -f1 data/old.fasta -f2 data/new.fasta -fmt json -o output/compare.json
```

---

## Scope and Limitations

ProFACT works with **protein FASTA files**, not FASTQ files, raw sequencing reads or nucleotide QC.

The first version is intended for small and medium protein datasets, such as custom FASTA files, proteomes, Swiss-Prot subsets or filtered UniProt downloads. Very large databases such as full UniProt or NCBI NR are outside the main scope of the first version.

The comparison is based on sequence IDs and exact sequence content. ProFACT does not perform BLAST searches, multiple sequence alignment or similarity-based clustering. Duplicate clustering means exact grouping of identical protein sequences.

The `report` command generates a combined report for one FASTA file. Pairwise dataset comparison is handled separately by the `compare` command.

---

## Similar Tools

Similar tools already exist, including `seqkit`, `pyfastx`, BioPython and FastQC. ProFACT does not aim to replace them or introduce a new algorithm.

The goal is to build a small, focused and testable protein FASTA tool with one consistent CLI for validation, statistics, exact duplicate detection, comparison and report generation.

---

## Team Members

| Name | GitHub |
|------|--------|
| Wojciech Laskowski | [@wlaskowski](https://github.com/wlaskowski) |
| Wojciech Moryl | [@wojciech-moryl](https://github.com/Fair0n) |
| Karolina Winczewska | [@KarolinaWinczewska](https://github.com/KaWinczewska) |

---

## Novelty Statement

ProFACT's novelty lies in **integration and architecture**, not in a new bioinformatics algorithm. It combines common protein FASTA quality-control tasks into one pip-installable Python package with a consistent CLI, structured outputs and automated tests.
