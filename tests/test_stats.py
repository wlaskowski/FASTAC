from profact.stats import n50, amino_composition, stats_summary, analyze_stats
from profact.parser import FastaRecord


def test_n50_multiple_lengths():
    lengths = [6, 4, 4, 2]
    expected = 4

    result = n50(lengths)

    assert result == expected
    assert isinstance(result, int)


def test_n50_empty_lengths():
    lengths = []
    expected = 0

    result = n50(lengths)

    assert result == expected
    assert result == 0


def test_amino_composition_counts_standard_amino_acids():
    records = [
        FastaRecord("p1", "", "AACC"),
        FastaRecord("p2", "", "AD"),
    ]

    composition = amino_composition(records)

    assert composition["A"]["count"] == 3
    assert composition["A"]["percent"] == 50.0
    assert composition["C"]["count"] == 2
    assert composition["D"]["count"] == 1


def test_amino_composition_counts_extra_symbols():
    records = [
        FastaRecord("p1", "", "X*BZJ"),
    ]

    composition = amino_composition(records)

    assert composition["X"]["count"] == 1
    assert composition["*"]["count"] == 1
    assert composition["B"]["count"] == 1
    assert composition["Z"]["count"] == 1
    assert composition["J"]["count"] == 1


def test_stats_summary_basic_lengths():
    records = [
        FastaRecord("p1", "", "AAAA"),
        FastaRecord("p2", "", "CCCCCC"),
        FastaRecord("p3", "", "DD"),
    ]

    result = stats_summary(records)
    summary = result["summary"]

    assert result["lengths"] == [4, 6, 2]
    assert summary["sequence_count"] == 3
    assert summary["total_length"] == 12
    assert summary["min_length"] == 2
    assert summary["max_length"] == 6
    assert summary["mean_length"] == 4.0
    assert summary["median_length"] == 4
    assert summary["n50"] == 6


def test_stats_summary_empty_records():
    records = []

    result = stats_summary(records)
    summary = result["summary"]

    assert result["lengths"] == []
    assert summary["sequence_count"] == 0
    assert summary["total_length"] == 0
    assert summary["min_length"] == 0
    assert summary["max_length"] == 0
    assert summary["mean_length"] == 0
    assert summary["median_length"] == 0
    assert summary["n50"] == 0


def test_analyze_stats_reads_fasta_file(tmp_path):
    content = """>p1
AAAA
>p2
CC
>p3
DX*
"""
    fasta_file = tmp_path / "proteins.fasta"
    fasta_file.write_text(content)

    result = analyze_stats(str(fasta_file))
    summary = result["summary"]
    composition = result["amino_acid_composition"]

    assert result["lengths"] == [4, 2, 3]
    assert summary["sequence_count"] == 3
    assert summary["total_length"] == 9
    assert summary["min_length"] == 2
    assert summary["max_length"] == 4
    assert summary["n50"] == 3
    assert composition["A"]["count"] == 4
    assert composition["C"]["count"] == 2
    assert composition["D"]["count"] == 1
    assert composition["X"]["count"] == 1
    assert composition["*"]["count"] == 1
