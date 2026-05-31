"""Duplicate detection for protein FASTA records."""
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Any

from .parser import FastaRecord, read_fasta


def find_duplicate_ids(records: Iterable[FastaRecord]) -> Dict[str, int]:
    """Return IDs that occur more than once with their occurrence counts."""
    counts = Counter(record.id for record in records)
    return {seq_id: count for seq_id, count in counts.items() if count > 1}


def cluster_identical_sequences(records: Iterable[FastaRecord]) -> List[Dict[str, Any]]:
    """
    Group records by exact sequence content.

    Only clusters with at least two records are returned. IDs are sorted to keep
    output stable in tests and CLI reports.
    """
    by_sequence = defaultdict(list)
    for record in records:
        by_sequence[record.sequence].append(record.id)

    clusters = []
    for sequence, ids in by_sequence.items():
        if len(ids) > 1:
            clusters.append({
                "sequence": sequence,
                "length": len(sequence),
                "count": len(ids),
                "ids": sorted(ids),
            })

    return sorted(clusters, key=lambda cluster: (cluster["length"], cluster["ids"]))


def duplicate_summary(records: Iterable[FastaRecord]) -> Dict[str, Any]:
    """Return duplicate-ID and identical-sequence cluster summary."""
    materialized = list(records)
    duplicate_ids = find_duplicate_ids(materialized)
    clusters = cluster_identical_sequences(materialized)
    ids_in_clusters = sorted({seq_id for cluster in clusters for seq_id in cluster["ids"]})

    return {
        "total_records": len(materialized),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_ids": duplicate_ids,
        "identical_sequence_cluster_count": len(clusters),
        "records_in_identical_sequence_clusters": len(ids_in_clusters),
        "identical_sequence_clusters": clusters,
    }


def analyze_duplicates(file_path: str) -> Dict[str, Any]:
    """Read a FASTA file and return duplicate analysis."""
    return duplicate_summary(read_fasta(file_path))
