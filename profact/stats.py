"""Statistics for protein FASTA records."""

import statistics
from collections import Counter
from typing import Dict, Iterable, Any
from .parser import FastaRecord, read_fasta

# Extra reported symbols: X and * are warnings;
# B, Z and J are non-standard amino acids.
STANDARD_AA = "ACDEFGHIKLMNPQRSTVWY"
EXTRA_AA = "X*BZJ"
REPORTED_AA = STANDARD_AA + EXTRA_AA


def n50(lengths):
    """
    Calculate N50 for protein sequence lengths.

    N50 is the sequence length at which sequences of this length or longer
    cover at least half of the total amino acid count.
    """

    if len(lengths) == 0:
        return 0
    total_length = sum(lengths)
    sorted_lengths = sorted(lengths, reverse=True)
    current_sum = 0
    for record_length in sorted_lengths:
        current_sum += record_length
        if current_sum >= total_length / 2:
            return record_length


def amino_composition(records: Iterable[FastaRecord]):
    """Return amino acid counts for protein FASTA records."""
    composition = {}
    counts = Counter()
    total = 0
    for record in records:
        for char in record.sequence:
            counts[char] += 1
            total += 1
    for char in REPORTED_AA:
        count = counts[char]
        if total > 0:
            percent = (count / total) * 100
        else:
            percent = 0
        composition[char] = {"count": count, "percent": percent}

    return composition


def stats_summary(records: Iterable[FastaRecord]) -> Dict[str, Any]:
    """Return basic summary statistics for sequence lengths."""
    summary_dict = {
        "sequence_count": 0,
        "total_length": 0,
        "min_length": 0,
        "max_length": 0,
        "mean_length": 0,
        "median_length": 0,
        "n50": 0,
    }

    records_list = list(records)
    lengths = []
    for record in records_list:
        lengths.append(len(record.sequence))

    if len(records_list) != 0:
        summary_dict["sequence_count"] = len(lengths)
        summary_dict["total_length"] = sum(lengths)
        summary_dict["min_length"] = min(lengths)
        summary_dict["max_length"] = max(lengths)
        summary_dict["mean_length"] = sum(lengths) / len(lengths)
        summary_dict["median_length"] = statistics.median(lengths)
        summary_dict["n50"] = n50(lengths)

    result = {
        "summary": summary_dict,
        "lengths": lengths,
        "amino_acid_composition": amino_composition(records_list),
    }

    return result


def analyze_stats(file_path: str) -> Dict[str, Any]:
    """Read a FASTA file and return statistics analysis."""
    return stats_summary(read_fasta(file_path))
