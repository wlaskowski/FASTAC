# ProFACT - Protein FASTA Analysis and Comparison Tool

> A pip-installable Python CLI for protein FASTA quality control, duplicate detection and dataset comparison.

<p align="center">
  <img width="300" height="300" alt="ProFACT logo" src="https://github.com/user-attachments/assets/0e32c2e5-2076-451b-b036-18cb15cb10f3" />
</p>

## Overview

Bioinformatics workflows often use protein FASTA files after downloading data from UniProt, Swiss-Prot, RefSeq or Ensembl/NCBI, filtering protein datasets, or running protein prediction pipelines. Checking quality and comparing two FASTA datasets often requires separate shell commands or custom scripts.

ProFACT combines common protein FASTA quality-control tasks into one small, testable Python CLI tool.

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
- Installation from GitHub via `pip install git+https://github.com/wlaskowski/ProFACT.git`

---

## Installation

```bash
pip install git+https://github.com/wlaskowski/ProFACT.git
```

After installation, the `profact` command is available globally.

For development in editable mode:

```bash
git clone https://github.com/wlaskowski/ProFACT.git
cd ProFACT
pip install -e .
```

For running tests:

```bash
pip install -e ".[test]"
python3 -m pytest -q
```

---

## Quick Start With Included Data

The repository includes two sample UniProt proteome FASTA files in `data/`.

The commands below assume that the repository was cloned locally:

```bash
git clone https://github.com/wlaskowski/ProFACT.git
cd ProFACT
```

To run tests and generate all example outputs:

```bash
bash scripts/run_examples.sh
```

This writes text, TSV, JSON and HTML outputs to `output/`.

You can also run selected analyses manually:

```bash
python3 -m profact.cli stats \
  -i data/uniprotkb_proteome_UP000000625_2026_06_06.fasta \
  -fmt html \
  -o output/stats_UP000000625.html

python3 -m profact.cli report \
  -i data/uniprotkb_proteome_UP000000625_2026_06_06.fasta \
  -fmt html \
  -o output/report_UP000000625.html

python3 -m profact.cli compare \
  -f1 data/uniprotkb_proteome_UP000000625_2026_06_06.fasta \
  -f2 data/uniprotkb_proteome_UP000001570_2026_06_06.fasta \
  -fmt json \
  -o output/compare_UP000000625_vs_UP000001570.json
```

---

## Usage

```bash
# Inspect a protein FASTA file
profact stats -i swissprot_subset.fasta

# Export statistics as JSON
profact stats -i swissprot_subset.fasta -fmt json -o output/stats.json

# Validate protein records
profact validate -i proteins.fasta.gz

# Detect identical protein sequences
profact duplicates -i proteins.fasta

# Compare raw and filtered protein datasets
profact compare -f1 raw_proteins.fasta -f2 filtered_proteins.fasta

# Export comparison as JSON
profact compare -f1 old_uniprot.fasta -f2 new_uniprot.fasta -fmt json -o output/compare.json

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

The `validate` command exits with status code `1` when invalid records are found.
The `compare` command exits with status code `1` when the two files differ.
In both cases this is expected behavior and reports are still written to `output/`.

---

## Project Structure

```text
profact/      Python package and CLI implementation
tests/        Automated tests
data/         Sample FASTA datasets
output/       Generated reports and command outputs
scripts/      Helper scripts for reproducible example runs
```

---

## What We Implemented

We created ProFACT as a new bioinformatics-related Python CLI project for protein FASTA quality control and comparison.

The implementation includes FASTA parsing, validation, sequence statistics, duplicate detection, pairwise dataset comparison, report generation, automated tests, sample FASTA datasets and a reproducible example script.

The tool was needed because common FASTA quality checks are often done with separate commands or custom scripts. ProFACT provides these checks in one consistent package.

---

## Scope and Limitations

ProFACT works with **protein FASTA files**, not FASTQ files, raw sequencing reads or nucleotide QC.

The first version is intended for small and medium protein datasets, such as custom FASTA files, proteomes, Swiss-Prot subsets or filtered UniProt downloads. Very large databases such as full UniProt or NCBI NR are outside the main scope of the first version.

The comparison is based on sequence IDs and exact sequence content. ProFACT does not perform BLAST searches, multiple sequence alignment or similarity-based clustering. Duplicate clustering means exact grouping of identical protein sequences.

The `report` command generates a combined report for one FASTA file. Pairwise dataset comparison is handled separately by the `compare` command.

---

## Similar Tools

Similar tools already exist, including `seqkit`, `pyfastx`, BioPython and FastQC. ProFACT does not aim to replace them or introduce a new bioinformatics algorithm.

Its value is integration: it combines common protein FASTA checks into one small, focused and testable CLI with structured outputs and automated tests.

---

## Team Members

| Name | GitHub |
|------|--------|
| Wojciech Laskowski | [@wlaskowski](https://github.com/wlaskowski) |
| Wojciech Moryl | [@wojciech-moryl](https://github.com/Fair0n) |
| Karolina Winczewska | [@KarolinaWinczewska](https://github.com/KaWinczewska) |