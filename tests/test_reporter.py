import json

from profact.reporter import (
    build_full_report_data,
    full_report_to_html,
    full_report_to_json,
    full_report_to_text,
    full_report_to_tsv,
    stats_to_html,
    stats_to_json,
    stats_to_text,
    stats_to_tsv,
)

STATS_DATA = {
    "summary": {"sequence_count": 2, "total_length": 6, "n50": 4},
    "lengths": [4, 2],
    "amino_acid_composition": {
        "A": {"count": 4, "percent": 66.6666666667},
        "C": {"count": 2, "percent": 33.3333333333},
    },
}


FULL_REPORT_DATA = {
    "file": "proteins.fasta",
    "stats": STATS_DATA,
    "validation": {
        "total_records": 2,
        "valid_records": 2,
        "invalid_records": 0,
        "records_with_X": 0,
        "records_with_stop": 0,
        "empty_records": 0,
    },
    "duplicates": {
        "total_records": 2,
        "duplicate_id_count": 0,
        "duplicate_ids": {},
        "identical_sequence_cluster_count": 0,
        "records_in_identical_sequence_clusters": 0,
        "identical_sequence_clusters": [],
    },
}


def test_stats_text_and_tsv_reports_contain_expected_sections():
    text_report = stats_to_text(STATS_DATA)
    tsv_report = stats_to_tsv(STATS_DATA)

    assert "=== Statistics report ===" in text_report
    assert "Summary statistics:" in text_report
    assert "A: count=4, percent=66.67" in text_report
    assert "summary_statistics\tsequence_count\t2" in tsv_report
    assert "amino_acid_composition\tC\t2\t33.33" in tsv_report


def test_stats_json_and_html_reports_contain_expected_data():
    json_report = stats_to_json(STATS_DATA)
    html_report = stats_to_html(STATS_DATA)
    parsed = json.loads(json_report)

    assert parsed["summary"]["n50"] == 4
    assert parsed["amino_acid_composition"]["A"]["count"] == 4
    assert "<html>" in html_report
    assert "Statistics report" in html_report
    assert "Amino acid composition" in html_report


def test_build_full_report_data_reads_fasta_file(tmp_path):
    content = """>p1
AAAA
>p2
CC
"""
    fasta_file = tmp_path / "proteins.fasta"
    fasta_file.write_text(content)

    data = build_full_report_data(str(fasta_file))

    assert data["file"] == str(fasta_file)
    assert data["stats"]["summary"]["sequence_count"] == 2
    assert data["stats"]["summary"]["total_length"] == 6
    assert data["validation"]["valid_records"] == 2
    assert data["duplicates"]["duplicate_id_count"] == 0


def test_full_text_and_tsv_reports_contain_all_sections():
    text_report = full_report_to_text(FULL_REPORT_DATA)
    tsv_report = full_report_to_tsv(FULL_REPORT_DATA)

    assert "=== ProFACT full report ===" in text_report
    assert "File: proteins.fasta" in text_report
    assert "Validation:" in text_report
    assert "file\tpath\tproteins.fasta" in tsv_report
    assert "duplicates\tduplicate_id_count\t0" in tsv_report


def test_full_json_report_can_be_parsed():
    report = full_report_to_json(FULL_REPORT_DATA)
    parsed = json.loads(report)

    assert parsed["file"] == "proteins.fasta"
    assert parsed["stats"]["summary"]["n50"] == 4
    assert parsed["validation"]["invalid_records"] == 0
    assert parsed["duplicates"]["duplicate_id_count"] == 0


def test_full_html_report_contains_all_sections():
    report = full_report_to_html(FULL_REPORT_DATA)

    assert "<html>" in report
    assert "ProFACT full report" in report
    assert "File: proteins.fasta" in report
    assert "Summary statistics" in report
    assert "Validation" in report
    assert "Duplicates" in report
