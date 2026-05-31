"""Comparison of two protein FASTA files."""
from collections import defaultdict
from typing import Dict, Iterable, List, Any, Tuple

from .parser import FastaRecord, read_fasta
from .duplicates import duplicate_summary


def records_by_id(records: Iterable[FastaRecord]) -> Dict[str, FastaRecord]:
    """
    Build an ID -> record mapping.

    If the same ID appears multiple times, the last record wins. Duplicate IDs
    are still reported separately by duplicate_summary().
    """
    return {record.id: record for record in records}


def sequence_cluster_signature(records: Iterable[FastaRecord]) -> Dict[str, Tuple[str, ...]]:
    """Return exact sequence -> tuple(sorted IDs) for all duplicated sequences."""
    by_sequence = defaultdict(list)
    for record in records:
        by_sequence[record.sequence].append(record.id)
    return {
        sequence: tuple(sorted(ids))
        for sequence, ids in by_sequence.items()
        if len(ids) > 1
    }


def compare_duplicate_clusters(
    old_records: Iterable[FastaRecord],
    new_records: Iterable[FastaRecord],
) -> Dict[str, Any]:
    """Detect exact duplicate sequence clusters added, removed or changed."""
    old_sig = sequence_cluster_signature(old_records)
    new_sig = sequence_cluster_signature(new_records)

    old_sequences = set(old_sig)
    new_sequences = set(new_sig)
    common_sequences = old_sequences & new_sequences

    changed = []
    for sequence in sorted(common_sequences):
        if old_sig[sequence] != new_sig[sequence]:
            old_ids = set(old_sig[sequence])
            new_ids = set(new_sig[sequence])
            changed.append({
                "sequence": sequence,
                "length": len(sequence),
                "old_ids": list(old_sig[sequence]),
                "new_ids": list(new_sig[sequence]),
                "added_ids": sorted(new_ids - old_ids),
                "removed_ids": sorted(old_ids - new_ids),
            })

    return {
        "added_clusters": [
            {"sequence": seq, "length": len(seq), "ids": list(new_sig[seq])}
            for seq in sorted(new_sequences - old_sequences)
        ],
        "removed_clusters": [
            {"sequence": seq, "length": len(seq), "ids": list(old_sig[seq])}
            for seq in sorted(old_sequences - new_sequences)
        ],
        "changed_clusters": changed,
    }


def compare_records(old_records: Iterable[FastaRecord], new_records: Iterable[FastaRecord]) -> Dict[str, Any]:
    """Compare two FASTA record collections by ID and exact sequence content."""
    old_list = list(old_records)
    new_list = list(new_records)
    old_by_id = records_by_id(old_list)
    new_by_id = records_by_id(new_list)

    old_ids = set(old_by_id)
    new_ids = set(new_by_id)
    common_ids = old_ids & new_ids

    changed_sequences = []
    changed_lengths = []
    for seq_id in sorted(common_ids):
        old_seq = old_by_id[seq_id].sequence
        new_seq = new_by_id[seq_id].sequence
        if old_seq != new_seq:
            item = {
                "id": seq_id,
                "old_length": len(old_seq),
                "new_length": len(new_seq),
            }
            changed_sequences.append(item)
            if len(old_seq) != len(new_seq):
                changed_lengths.append(item)

    duplicate_changes = compare_duplicate_clusters(old_list, new_list)

    return {
        "summary": {
            "old_total_records": len(old_list),
            "new_total_records": len(new_list),
            "added_count": len(new_ids - old_ids),
            "removed_count": len(old_ids - new_ids),
            "changed_sequence_count": len(changed_sequences),
            "changed_length_count": len(changed_lengths),
            "added_duplicate_cluster_count": len(duplicate_changes["added_clusters"]),
            "removed_duplicate_cluster_count": len(duplicate_changes["removed_clusters"]),
            "changed_duplicate_cluster_count": len(duplicate_changes["changed_clusters"]),
        },
        "added_ids": [
            {"id": seq_id, "new_length": len(new_by_id[seq_id].sequence)}
            for seq_id in sorted(new_ids - old_ids)
        ],
        "removed_ids": [
            {"id": seq_id, "old_length": len(old_by_id[seq_id].sequence)}
            for seq_id in sorted(old_ids - new_ids)
        ],
        "changed_sequences": changed_sequences,
        "changed_lengths": changed_lengths,
        "old_duplicates": duplicate_summary(old_list),
        "new_duplicates": duplicate_summary(new_list),
        "duplicate_cluster_changes": duplicate_changes,
    }


def compare_files(old_file: str, new_file: str) -> Dict[str, Any]:
    """Read and compare two FASTA files."""
    return compare_records(read_fasta(old_file), read_fasta(new_file))
