#!/usr/bin/env bash
set -euo pipefail

OLD_FASTA="data/uniprotkb_proteome_UP000000625_2026_06_06.fasta"
NEW_FASTA="data/uniprotkb_proteome_UP000001570_2026_06_06.fasta"
COMPARE_NAME="UP000000625_vs_UP000001570"

mkdir -p output

allow_status_one() {
    if "$@"; then
        return 0
    fi

    status=$?
    if [ "$status" -eq 1 ]; then
        return 0
    fi
    return "$status"
}

python3 -m pytest -q

for dataset in \
    "UP000000625:$OLD_FASTA" \
    "UP000001570:$NEW_FASTA"
do
    name="${dataset%%:*}"
    fasta="${dataset#*:}"

    for format in text tsv json html
    do
        extension="$format"
        if [ "$format" = "text" ]; then
            extension="txt"
        fi

        python3 -m profact.cli stats -i "$fasta" -fmt "$format" -o "output/stats_${name}.${extension}"
        allow_status_one python3 -m profact.cli validate -i "$fasta" -fmt "$format" -o "output/validation_${name}.${extension}"
        python3 -m profact.cli duplicates -i "$fasta" -fmt "$format" -o "output/duplicates_${name}.${extension}"
        python3 -m profact.cli report -i "$fasta" -fmt "$format" -o "output/report_${name}.${extension}"
    done
done

for format in text tsv json html
do
    extension="$format"
    if [ "$format" = "text" ]; then
        extension="txt"
    fi

    allow_status_one python3 -m profact.cli compare -f1 "$OLD_FASTA" -f2 "$NEW_FASTA" -fmt "$format" -o "output/compare_${COMPARE_NAME}.${extension}"
done

echo "Example outputs written to output/"
