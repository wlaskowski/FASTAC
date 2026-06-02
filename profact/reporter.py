"""Report formatting for ProFACT analysis results."""

import json
from .parser import validate_record, read_fasta
from .duplicates import duplicate_summary
from .stats import stats_summary


def stats_to_text(data):
    """Return a text report for sequence statistics."""
    summary = data["summary"]
    composition = data["amino_acid_composition"]

    lines = ["=== Statistics report ==="]

    lines.append("")
    lines.append("Summary statistics:")
    for metric, value in summary.items():
        lines.append(f"{metric}: {value}")

    lines.append("")
    lines.append("Amino acid composition:")
    for char, values in composition.items():
        lines.append(f"{char}: count={values['count']}, percent={values['percent']:.2f}")

    return "\n".join(lines)


def stats_to_tsv(data):
    """Return a TSV report for sequence statistics."""
    summary = data["summary"]
    composition = data["amino_acid_composition"]

    lines = ["section\tmetric\tvalue"]
    for metric, value in summary.items():
        lines.append(f"summary_statistics\t{metric}\t{value}")

    lines.append("")
    lines.append("section\tamino_acid\tcount\tpercent")
    for char, values in composition.items():
        lines.append(f"amino_acid_composition\t{char}\t{values['count']}\t{values['percent']:.2f}")

    return "\n".join(lines)


def stats_to_json(data):
    """Return a JSON report for sequence statistics."""
    return json.dumps(data, indent=2)


def stats_to_html(data):
    """Return an HTML report for sequence statistics."""
    summary = data["summary"]
    composition = data["amino_acid_composition"]

    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>Statistics report</title>",
        "<style>",
        "table { border-collapse: collapse; }",
        "th, td { border: 1px solid black; padding: 4px; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Statistics report</h1>",
        "<h2>Summary statistics</h2>",
        "<table>",
        "<tr><th>Metric</th><th>Value</th></tr>",
    ]

    for metric, value in summary.items():
        lines.append(f"<tr><td>{metric}</td><td>{value}</td></tr>")

    lines.extend(
        [
            "</table>",
            "<h2>Amino acid composition</h2>",
            "<table>",
            "<tr><th>AA</th><th>Count</th><th>Percent</th></tr>",
        ]
    )

    for aa, values in composition.items():
        lines.append(f"<tr><td>{aa}</td><td>{values['count']}</td><td>{values['percent']:.2f}</td></tr>")

    lines.extend(
        [
            "</table>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(lines)


def build_full_report_data(file_path):
    """Read a FASTA file and return data for a full report."""
    records = list(read_fasta(file_path))

    validation_results = []
    for record in records:
        validation_results.append(validate_record(record))

    total = len(validation_results)
    valid_count = sum(1 for v in validation_results if v["valid"])
    invalid_count = total - valid_count
    records_with_x = sum(1 for v in validation_results if v["has_x"])
    records_with_stop = sum(1 for v in validation_results if v["has_stop"])
    empty_records = sum(1 for v in validation_results if v["is_empty"])

    stats = stats_summary(records)
    duplicates = duplicate_summary(records)

    return {
        "file": file_path,
        "stats": stats,
        "validation": {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "records_with_X": records_with_x,
            "records_with_stop": records_with_stop,
            "empty_records": empty_records,
        },
        "duplicates": duplicates,
    }


def full_report_to_text(data):
    """Return a text report with statistics, validation and duplicates."""
    stats = data["stats"]
    summary = stats["summary"]
    composition = stats["amino_acid_composition"]
    validation = data["validation"]
    duplicates = data["duplicates"]

    lines = ["=== ProFACT full report ==="]

    lines.append("")
    lines.append(f"File: {data['file']}")

    lines.append("")
    lines.append("Summary statistics:")
    for metric, value in summary.items():
        lines.append(f"{metric}: {value}")

    lines.append("")
    lines.append("Amino acid composition:")
    for char, values in composition.items():
        lines.append(f"{char}: count={values['count']}, percent={values['percent']:.2f}")

    lines.append("")
    lines.append("Validation:")
    for metric, value in validation.items():
        lines.append(f"{metric}: {value}")

    lines.append("")
    lines.append("Duplicates:")
    for metric, value in duplicates.items():
        lines.append(f"{metric}: {value}")
    return "\n".join(lines)


def full_report_to_json(data):
    """Return a JSON report with statistics, validation and duplicates."""
    return json.dumps(data, indent=2)


def full_report_to_html(data):
    """Return an HTML report with statistics, validation and duplicates."""
    stats = data["stats"]
    summary = stats["summary"]
    composition = stats["amino_acid_composition"]
    validation = data["validation"]
    duplicates = data["duplicates"]

    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>ProFACT full report</title>",
        "<style>",
        "table { border-collapse: collapse; }",
        "th, td { border: 1px solid black; padding: 4px; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>ProFACT full report</h1>",
        f"<p>File: {data['file']}</p>",
        "<h2>Summary statistics</h2>",
        "<table>",
        "<tr><th>Metric</th><th>Value</th></tr>",
    ]

    for metric, value in summary.items():
        lines.append(f"<tr><td>{metric}</td><td>{value}</td></tr>")

    lines.extend(
        [
            "</table>",
            "<h2>Amino acid composition</h2>",
            "<table>",
            "<tr><th>AA</th><th>Count</th><th>Percent</th></tr>",
        ]
    )

    for aa, values in composition.items():
        lines.append(f"<tr><td>{aa}</td><td>{values['count']}</td><td>{values['percent']:.2f}</td></tr>")

    lines.extend(
        [
            "</table>",
            "<h2>Validation</h2>",
            "<table>",
            "<tr><th>Metric</th><th>Value</th></tr>",
        ]
    )

    for metric, value in validation.items():
        lines.append(f"<tr><td>{metric}</td><td>{value}</td></tr>")

    lines.extend(
        [
            "</table>",
            "<h2>Duplicates</h2>",
            "<table>",
            "<tr><th>Metric</th><th>Value</th></tr>",
        ]
    )

    for metric, value in duplicates.items():
        lines.append(f"<tr><td>{metric}</td><td>{value}</td></tr>")

    lines.extend(
        [
            "</table>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(lines)


def full_report_to_tsv(data):
    """Return a TSV report with statistics, validation and duplicates."""
    stats = data["stats"]
    summary = stats["summary"]
    composition = stats["amino_acid_composition"]
    validation = data["validation"]
    duplicates = data["duplicates"]

    lines = ["section\tmetric\tvalue"]
    lines.append(f"file\tpath\t{data['file']}")
    for metric, value in summary.items():
        lines.append(f"summary_statistics\t{metric}\t{value}")

    lines.append("")
    lines.append("section\tamino_acid\tcount\tpercent")
    for char, values in composition.items():
        lines.append(f"amino_acid_composition\t{char}\t{values['count']}\t{values['percent']:.2f}")

    lines.append("")
    lines.append("section\tmetric\tvalue")
    for metric, value in validation.items():
        lines.append(f"validation\t{metric}\t{value}")

    lines.append("")
    lines.append("section\tmetric\tvalue")
    for metric, value in duplicates.items():
        lines.append(f"duplicates\t{metric}\t{value}")

    return "\n".join(lines)
