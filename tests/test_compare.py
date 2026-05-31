from profact.compare import compare_records, compare_duplicate_clusters
from profact.parser import FastaRecord


def test_compare_records_detects_added_removed_and_changed_sequences():
    old = [
        FastaRecord("keep", "", "AAAA"),
        FastaRecord("changed", "", "MMMM"),
        FastaRecord("removed", "", "RRRR"),
    ]
    new = [
        FastaRecord("keep", "", "AAAA"),
        FastaRecord("changed", "", "MMMMK"),
        FastaRecord("added", "", "DDDD"),
    ]

    result = compare_records(old, new)

    assert result["added_ids"] == [{"id": "added", "new_length": 4}]
    assert result["removed_ids"] == [{"id": "removed", "old_length": 4}]
    assert result["changed_sequences"] == [{"id": "changed", "old_length": 4, "new_length": 5}]
    assert result["changed_lengths"] == [{"id": "changed", "old_length": 4, "new_length": 5}]
    assert result["summary"]["added_count"] == 1
    assert result["summary"]["removed_count"] == 1
    assert result["summary"]["changed_sequence_count"] == 1


def test_compare_records_detects_same_length_sequence_change():
    old = [FastaRecord("p1", "", "AAAA")]
    new = [FastaRecord("p1", "", "CCCC")]

    result = compare_records(old, new)

    assert result["changed_sequences"] == [{"id": "p1", "old_length": 4, "new_length": 4}]
    assert result["changed_lengths"] == []


def test_compare_duplicate_clusters_added_removed_and_changed():
    old = [
        FastaRecord("a", "", "SEQ1"),
        FastaRecord("b", "", "SEQ1"),
        FastaRecord("x", "", "OLD"),
        FastaRecord("y", "", "OLD"),
    ]
    new = [
        FastaRecord("a", "", "SEQ1"),
        FastaRecord("b", "", "SEQ1"),
        FastaRecord("c", "", "SEQ1"),
        FastaRecord("m", "", "NEW"),
        FastaRecord("n", "", "NEW"),
    ]

    changes = compare_duplicate_clusters(old, new)

    assert changes["removed_clusters"] == [{"sequence": "OLD", "length": 3, "ids": ["x", "y"]}]
    assert changes["added_clusters"] == [{"sequence": "NEW", "length": 3, "ids": ["m", "n"]}]
    assert changes["changed_clusters"] == [{
        "sequence": "SEQ1",
        "length": 4,
        "old_ids": ["a", "b"],
        "new_ids": ["a", "b", "c"],
        "added_ids": ["c"],
        "removed_ids": [],
    }]
