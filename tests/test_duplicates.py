from profact.duplicates import duplicate_summary, find_duplicate_ids, cluster_identical_sequences
from profact.parser import FastaRecord


def test_find_duplicate_ids():
    records = [
        FastaRecord("p1", "", "AAA"),
        FastaRecord("p1", "second", "BBB"),
        FastaRecord("p2", "", "AAA"),
    ]

    assert find_duplicate_ids(records) == {"p1": 2}


def test_cluster_identical_sequences_groups_exact_matches():
    records = [
        FastaRecord("p1", "", "MKT"),
        FastaRecord("p2", "", "MKT"),
        FastaRecord("p3", "", "AAAA"),
    ]

    clusters = cluster_identical_sequences(records)

    assert clusters == [{"sequence": "MKT", "length": 3, "count": 2, "ids": ["p1", "p2"]}]


def test_duplicate_summary_counts_records_in_clusters():
    records = [
        FastaRecord("p1", "", "MKT"),
        FastaRecord("p2", "", "MKT"),
        FastaRecord("p3", "", "AAAA"),
        FastaRecord("p3", "duplicate id", "CCCC"),
    ]

    summary = duplicate_summary(records)

    assert summary["total_records"] == 4
    assert summary["duplicate_ids"] == {"p3": 2}
    assert summary["identical_sequence_cluster_count"] == 1
    assert summary["records_in_identical_sequence_clusters"] == 2
