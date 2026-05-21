# FASTAC - Protein FASTA Quality Control and Comparison Tool

> A pip-installable Python CLI for protein FASTA quality control, duplicate detection and dataset comparison.



## Subject

Bioinformatics workflows often use protein FASTA files after downloading data from UniProt, Swiss-Prot, RefSeq or Ensembl/NCBI, filtering protein datasets, or running protein prediction pipelines. Checking what changed between two versions of such files usually requires custom scripts, shell commands and separate tools.

**FASTAC** provides one small Python package for a focused protein FASTA workflow:

1. **Inspect** - compute statistics for protein FASTA files: sequence count, total/min/max/mean/median length, N50 and amino acid composition.
2. **Validate** - detect empty records, duplicated IDs, unknown residues (`X`), stop symbols (`*`) and non-standard amino acid characters.
3. **Find duplicates** - group identical protein sequences found under different IDs.
4. **Compare** - report IDs added, removed and changed between two FASTA files, with side-by-side summary statistics.
5. **Report** - export results in text, TSV, JSON or simple HTML format.

---

## Features

- Plain and gzipped protein FASTA support (`.fa`, `.fasta`, `.faa`, `.fa.gz`, `.fasta.gz`, `.faa.gz`)
- Protein-specific statistics: length distribution, N50, amino acid composition
- Quality checks: `X`, `*`, invalid amino acid characters, empty records
- Duplicate detection: repeated IDs and identical sequences under different IDs
- Exact duplicate clustering
- Comparison of two protein FASTA files:
  - added IDs
  - removed IDs
  - changed sequences
  - changed sequence lengths
  - changed duplicate clusters
- Output formats: text, TSV, JSON, HTML
- Pure Python, no heavy bioinformatics dependencies
- Planned installation via `pip install fastac`

---

## Planned Usage

```bash
# Inspect a protein FASTA file
fastac stats swissprot_subset.fasta

# Validate protein records
fastac validate proteins.fasta.gz

# Detect identical protein sequences
fastac duplicates proteins.fasta

# Compare raw and filtered protein datasets
fastac compare raw_proteins.fasta filtered_proteins.fasta

# Export comparison as JSON
fastac compare old_uniprot.fasta new_uniprot.fasta --format json --output report.json

# Generate an HTML report
fastac report proteins.fasta --output report.html
```

---

## Scope and Limitations

FASTAC works with **protein FASTA files**, not FASTQ files, raw sequencing reads or nucleotide QC.

The first version is intended for small and medium protein datasets, such as custom FASTA files, proteomes, Swiss-Prot subsets or filtered UniProt downloads. Very large databases such as full UniProt or NCBI NR are outside the main scope of the first version.

The comparison is based on sequence IDs and exact sequence content. FASTAC does not perform BLAST searches, multiple sequence alignment or similarity-based clustering. Duplicate clustering means exact grouping of identical protein sequences.

---

## Similar Tools

Similar tools already exist, including `seqkit`, `pyfastx`, BioPython and FastQC. FASTAC does not aim to replace them or introduce a new algorithm.

The goal is to build a small, focused and testable protein FASTA tool with one consistent CLI for validation, statistics, exact duplicate detection, comparison and report generation.

---

## Project Structure

```
fastac/
├── fastac/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── parser.py       # FASTA reading, gzip support, validation
│   ├── stats.py        # Protein statistics and amino acid composition
│   ├── duplicates.py   # Duplicate IDs and exact sequence clusters
│   ├── compare.py      # Comparison of two protein FASTA files
│   └── reporter.py     # Text/TSV/JSON/HTML reports
├── tests/
│   ├── test_parser.py
│   ├── test_stats.py
│   ├── test_duplicates.py
│   ├── test_compare.py
│   └── test_reporter.py
├── .github/workflows/
│   └── ci.yml          # GitHub Actions: run pytest on every push
├── README.md
├── pyproject.toml
└── LICENSE
```

---

## Team Members

| Name | GitHub |
|------|--------|
| Wojciech Laskowski | [@wlaskowski](https://github.com/wlaskowski) |
| Wojciech Moryl | [@wojciech-moryl](https://github.com/Fair0n) |
| Karolina Winczewska | [@KarolinaWinczewska](https://github.com/KaWinczewska) |

---

## Progress Log

| Date | Milestone |
|------|-----------|
| 2026-05-07 | Project concept defined, README created, repository set up |
| 2026-05-17 | Scope clarified: protein FASTA QC, comparison and exact duplicate clustering |

---

## Novelty Statement

FASTAC's novelty lies in **integration and architecture**, not in a new bioinformatics algorithm. It combines common protein FASTA quality-control tasks into one pip-installable Python package with a consistent CLI, structured outputs and automated tests.

