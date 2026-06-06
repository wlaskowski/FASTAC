#!/usr/bin/env bash
set -u

OLD_FASTA="data/uniprotkb_proteome_UP000000625_2026_06_06.fasta"
NEW_FASTA="data/uniprotkb_proteome_UP000001570_2026_06_06.fasta"
COMPARE_NAME="UP000000625_vs_UP000001570"

mkdir -p output

python3 -m pytest -q

python3 -m profact.cli stats -i "$OLD_FASTA" -o output/stats_UP000000625.txt
python3 -m profact.cli stats -i "$OLD_FASTA" -fmt json -o output/stats_UP000000625.json
python3 -m profact.cli stats -i "$OLD_FASTA" -fmt tsv -o output/stats_UP000000625.tsv
python3 -m profact.cli stats -i "$OLD_FASTA" -fmt html -o output/stats_UP000000625.html
python3 -m profact.cli validate -i "$OLD_FASTA" -o output/validation_UP000000625.txt || true
python3 -m profact.cli duplicates -i "$OLD_FASTA" -o output/duplicates_UP000000625.txt
python3 -m profact.cli report -i "$OLD_FASTA" -fmt html -o output/report_UP000000625.html

python3 -m profact.cli stats -i "$NEW_FASTA" -o output/stats_UP000001570.txt
python3 -m profact.cli stats -i "$NEW_FASTA" -fmt json -o output/stats_UP000001570.json
python3 -m profact.cli stats -i "$NEW_FASTA" -fmt tsv -o output/stats_UP000001570.tsv
python3 -m profact.cli stats -i "$NEW_FASTA" -fmt html -o output/stats_UP000001570.html
python3 -m profact.cli validate -i "$NEW_FASTA" -o output/validation_UP000001570.txt || true
python3 -m profact.cli duplicates -i "$NEW_FASTA" -o output/duplicates_UP000001570.txt
python3 -m profact.cli report -i "$NEW_FASTA" -fmt html -o output/report_UP000001570.html

python3 -m profact.cli compare -f1 "$OLD_FASTA" -f2 "$NEW_FASTA" -o "output/compare_${COMPARE_NAME}.txt" || true
python3 -m profact.cli compare -f1 "$OLD_FASTA" -f2 "$NEW_FASTA" -fmt json -o "output/compare_${COMPARE_NAME}.json" || true
python3 -m profact.cli compare -f1 "$OLD_FASTA" -f2 "$NEW_FASTA" -fmt tsv -o "output/compare_${COMPARE_NAME}.tsv" || true

echo "Example outputs written to output/"
