"""Report formatting for ProFACT analysis results."""

import json
from html import escape
from .parser import validate_record, read_fasta
from .duplicates import duplicate_summary
from .stats import stats_summary


def _html_styles():
    """Return shared CSS for HTML reports."""
    return """
body {
    margin: 0;
    background: #f5f7fb;
    color: #1f2937;
    font-family: Arial, Helvetica, sans-serif;
}
main {
    max-width: 1100px;
    margin: 0 auto;
    padding: 32px 24px 48px;
}
header {
    margin-bottom: 24px;
}
h1 {
    margin: 0 0 8px;
    color: #111827;
}
h2 {
    margin-top: 32px;
    color: #111827;
}
.muted {
    color: #6b7280;
}
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin: 20px 0;
}
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
}
.card .label {
    color: #6b7280;
    font-size: 12px;
    text-transform: uppercase;
}
.card .value {
    margin-top: 6px;
    color: #111827;
    font-size: 24px;
    font-weight: 700;
}
table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
}
th, td {
    border-bottom: 1px solid #e5e7eb;
    padding: 8px 10px;
    text-align: left;
}
th {
    background: #eef2f7;
}
tr:last-child td {
    border-bottom: 0;
}
.bar-cell {
    min-width: 180px;
}
.bar {
    height: 10px;
    background: #dbeafe;
    border-radius: 999px;
    overflow: hidden;
}
.bar span {
    display: block;
    height: 100%;
    background: #2563eb;
}
.status-ok {
    color: #047857;
    font-weight: 700;
}
.status-warn {
    color: #b45309;
    font-weight: 700;
}
.validation-table td {
    color: #1f2937;
    font-weight: 400;
}
.validation-table td.status-ok {
    color: #047857;
    font-weight: 700;
}
.validation-table td.status-warn {
    color: #b45309;
    font-weight: 700;
}
.ids {
    line-height: 1.5;
}
.tag {
    display: inline-block;
    margin: 2px 4px 2px 0;
    padding: 2px 6px;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 999px;
    color: #3730a3;
    font-size: 12px;
    white-space: nowrap;
}
.sequence-preview {
    max-width: 320px;
    color: #6b7280;
    font-family: monospace;
    overflow-wrap: anywhere;
}
"""


def _format_metric_name(metric):
    """Make internal metric names easier to read in HTML reports."""
    return metric.replace("_", " ").title()


def _cards(metrics):
    lines = ['<section class="cards">']
    for label, value in metrics:
        lines.extend(
            [
                '<div class="card">',
                f'<div class="label">{escape(str(label))}</div>',
                f'<div class="value">{escape(str(value))}</div>',
                "</div>",
            ]
        )
    lines.append("</section>")
    return lines


def _summary_table(summary):
    lines = [
        "<table>",
        "<tr><th>Metric</th><th>Value</th></tr>",
    ]
    for metric, value in summary.items():
        lines.append(f"<tr><td>{escape(_format_metric_name(metric))}</td>" f"<td>{escape(str(value))}</td></tr>")
    lines.append("</table>")
    return lines


def _composition_table(composition):
    lines = [
        "<table>",
        "<tr><th>AA</th><th>Count</th><th>Percent</th><th>Chart</th></tr>",
    ]
    for aa, values in composition.items():
        percent = values["percent"]
        width = max(0, min(100, percent))
        lines.append(
            "<tr>"
            f"<td>{escape(str(aa))}</td>"
            f"<td>{values['count']}</td>"
            f"<td>{percent:.2f}</td>"
            '<td class="bar-cell">'
            f'<div class="bar"><span style="width: {width:.2f}%"></span></div>'
            "</td>"
            "</tr>"
        )
    lines.append("</table>")
    return lines


def _metric_table(metrics):
    lines = [
        "<table>",
        "<tr><th>Metric</th><th>Value</th></tr>",
    ]
    for metric, value in metrics.items():
        lines.append(f"<tr><td>{escape(_format_metric_name(metric))}</td>" f"<td>{escape(str(value))}</td></tr>")
    lines.append("</table>")
    return lines


def _duplicates_summary_table(duplicates):
    summary_keys = [
        "total_records",
        "duplicate_id_count",
        "identical_sequence_cluster_count",
        "records_in_identical_sequence_clusters",
    ]
    summary = {key: duplicates[key] for key in summary_keys if key in duplicates}
    return _metric_table(summary)


def _duplicate_ids_table(duplicate_ids):
    if not duplicate_ids:
        return ['<p class="muted">No duplicate IDs found.</p>']

    lines = [
        "<h3>Duplicate IDs</h3>",
        "<table>",
        "<tr><th>ID</th><th>Occurrences</th></tr>",
    ]
    for seq_id, count in sorted(duplicate_ids.items()):
        lines.append(f"<tr><td>{escape(str(seq_id))}</td><td>{escape(str(count))}</td></tr>")
    lines.append("</table>")
    return lines


def _duplicate_clusters_table(clusters):
    if not clusters:
        return ['<p class="muted">No identical sequence clusters found.</p>']

    lines = [
        "<h3>Identical sequence clusters</h3>",
        "<table>",
        "<tr><th>#</th><th>Length</th><th>Records</th><th>IDs</th><th>Sequence preview</th></tr>",
    ]
    for index, cluster in enumerate(clusters, start=1):
        ids = " ".join(f'<span class="tag">{escape(str(seq_id))}</span>' for seq_id in cluster["ids"])
        sequence = cluster.get("sequence", "")
        preview = sequence[:60] + ("..." if len(sequence) > 60 else "")
        lines.append(
            "<tr>"
            f"<td>{index}</td>"
            f"<td>{cluster['length']}</td>"
            f"<td>{cluster['count']}</td>"
            f'<td class="ids">{ids}</td>'
            f'<td class="sequence-preview">{escape(preview)}</td>'
            "</tr>"
        )
    lines.append("</table>")
    return lines


def _duplicates_section(duplicates):
    lines = []
    lines.extend(_duplicates_summary_table(duplicates))
    lines.extend(_duplicate_ids_table(duplicates.get("duplicate_ids", {})))
    lines.extend(_duplicate_clusters_table(duplicates.get("identical_sequence_clusters", [])))
    return lines


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
        _html_styles(),
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        "<header>",
        "<h1>Statistics report</h1>",
        '<p class="muted">Protein FASTA summary statistics and amino acid composition.</p>',
        "</header>",
    ]

    lines.extend(
        _cards(
            [
                ("Sequences", summary["sequence_count"]),
                ("Total length", summary["total_length"]),
                ("N50", summary["n50"]),
                ("Median length", summary.get("median_length", "n/a")),
            ]
        )
    )

    lines.extend(
        [
            "<h2>Summary statistics</h2>",
        ]
    )
    lines.extend(_summary_table(summary))

    lines.extend(
        [
            "<h2>Amino acid composition</h2>",
        ]
    )
    lines.extend(_composition_table(composition))

    lines.extend(
        [
            "</main>",
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
    lines.append(f"total_records: {duplicates['total_records']}")
    lines.append(f"duplicate_id_count: {duplicates['duplicate_id_count']}")
    lines.append(f"identical_sequence_cluster_count: {duplicates['identical_sequence_cluster_count']}")
    lines.append("records_in_identical_sequence_clusters: " f"{duplicates['records_in_identical_sequence_clusters']}")
    if duplicates["duplicate_ids"]:
        lines.append("duplicate_ids:")
        for seq_id, count in sorted(duplicates["duplicate_ids"].items()):
            lines.append(f"  {seq_id}: {count} records")
    if duplicates["identical_sequence_clusters"]:
        lines.append("identical_sequence_clusters:")
        for index, cluster in enumerate(duplicates["identical_sequence_clusters"], start=1):
            lines.append(f"  Cluster {index}: len={cluster['length']}, " f"count={cluster['count']}, ids={', '.join(cluster['ids'])}")
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
        _html_styles(),
        "</style>",
        "</head>",
        "<body>",
        "<main>",
        "<header>",
        "<h1>ProFACT full report</h1>",
        f"<p class=\"muted\">File: {escape(str(data['file']))}</p>",
        "</header>",
    ]

    validation_status = "OK" if validation["invalid_records"] == 0 else "Issues found"
    duplicate_status = duplicates["identical_sequence_cluster_count"]
    lines.extend(
        _cards(
            [
                ("Sequences", summary["sequence_count"]),
                ("Total length", summary["total_length"]),
                ("N50", summary["n50"]),
                ("Validation", validation_status),
                ("Duplicate clusters", duplicate_status),
            ]
        )
    )

    lines.extend(
        [
            "<h2>Summary statistics</h2>",
        ]
    )
    lines.extend(_summary_table(summary))

    lines.extend(
        [
            "<h2>Amino acid composition</h2>",
        ]
    )
    lines.extend(_composition_table(composition))

    lines.extend(
        [
            "<h2>Validation</h2>",
        ]
    )
    lines.extend(_metric_table(validation))

    lines.extend(
        [
            "<h2>Duplicates</h2>",
        ]
    )
    lines.extend(_duplicates_section(duplicates))

    lines.extend(
        [
            "</main>",
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


def format_validation_report(file_path, validated, summary, output_format):
    """Format validation results into text, tsv, json, or html."""
    if output_format == "json":
        return json.dumps(
            {
                "file": file_path,
                "summary": summary,
                "records": validated,
            },
            indent=2,
        )
    elif output_format == "tsv":
        lines = ["id\tvalid\terrors\twarnings\thas_x\thas_stop\tis_empty"]
        for v in validated:
            lines.append(f"{v['id']}\t{v['valid']}\t{';'.join(v['errors'])}\t{';'.join(v['warnings'])}\t{v['has_x']}\t{v['has_stop']}\t{v['is_empty']}")
        return "\n".join(lines)
    elif output_format == "html":
        # Use the same CSS and card layout as stats and full report
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Validation report</title>",
            "<style>",
            _html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header>",
            "<h1>Validation report</h1>",
            f'<p class="muted">File: {escape(str(file_path))}</p>',
            "</header>",
        ]
        # Summary cards
        lines.extend(
            _cards(
                [
                    ("Total records", summary["total_records"]),
                    ("Valid records", summary["valid_records"]),
                    ("Invalid records", summary["invalid_records"]),
                    ("Records with X", summary["records_with_X"]),
                    ("Records with *", summary["records_with_stop"]),
                    ("Empty records", summary["empty_records"]),
                ]
            )
        )
        # Per-record table
        lines.extend(
            [
                "<h2>Per‑record details</h2>",
                '<table class="validation-table">',
                "<thead>",
                "<tr><th>ID</th><th>Length</th><th>Valid</th><th>Errors</th><th>Warnings</th></tr>",
                "</thead>",
                "<tbody>",
            ]
        )
        for v in validated:
            valid_class = "status-ok" if v["valid"] else "status-warn"
            errors_str = escape("<br>".join(v["errors"])) if v["errors"] else "-"
            warnings_str = escape("<br>".join(v["warnings"])) if v["warnings"] else "-"
            lines.append(
                "<tr>"
                f"<td>{escape(v['id'])}</td>"
                f"<td>{v['sequence_length']}</td>"
                f'<td class="{valid_class}">{v["valid"]}</td>'
                f"<td>{errors_str}</td>"
                f"<td>{warnings_str}</td>"
                "</tr>"
            )
        lines.extend(
            [
                "</tbody>",
                "</table>",
                "</main>",
                "</body>",
                "</html>",
            ]
        )
        return "\n".join(lines)
    else:  # text
        lines = [
            f"=== Validation report for {file_path} ===",
            f"Total records: {summary['total_records']}",
            f"Valid: {summary['valid_records']}, Invalid: {summary['invalid_records']}",
            f"Records with 'X': {summary['records_with_X']}, with '*': {summary['records_with_stop']}, empty: {summary['empty_records']}\n",
        ]
        for v in validated:
            if v["errors"] or v["warnings"]:
                lines.append(f"> {v['id']} (len={v['sequence_length']})")
                for err in v["errors"]:
                    lines.append(f"  ERROR: {err}")
                for warn in v["warnings"]:
                    lines.append(f"  WARN:  {warn}")
        return "\n".join(lines)


def format_duplicates_report(data, file_path, output_format):
    """Format duplicate analysis results into text, tsv, json, or html."""
    if output_format == "json":
        return json.dumps(data, indent=2)
    elif output_format == "tsv":
        lines = ["section\tmetric\tvalue"]
        summary_keys = [
            "total_records",
            "duplicate_id_count",
            "identical_sequence_cluster_count",
            "records_in_identical_sequence_clusters",
        ]
        for key in summary_keys:
            lines.append(f"summary\t{key}\t{data[key]}")

        lines.append("")
        lines.append("section\tid\toccurrences")
        for seq_id, count in sorted(data["duplicate_ids"].items()):
            lines.append(f"duplicate_ids\t{seq_id}\t{count}")

        lines.append("")
        lines.append("section\tcluster_no\tlength\tcount\tids")
        for i, cluster in enumerate(data["identical_sequence_clusters"], start=1):
            lines.append("identical_sequence_clusters\t" f"{i}\t{cluster['length']}\t{cluster['count']}\t" f"{','.join(cluster['ids'])}")
        return "\n".join(lines)
    elif output_format == "html":
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Duplicate report</title>",
            "<style>",
            _html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header>",
            "<h1>Duplicate report</h1>",
            f'<p class="muted">File: {escape(str(file_path))}</p>',
            "</header>",
        ]
        lines.extend(
            _cards(
                [
                    ("Records", data["total_records"]),
                    ("Duplicate IDs", data["duplicate_id_count"]),
                    ("Sequence clusters", data["identical_sequence_cluster_count"]),
                    (
                        "Records in clusters",
                        data["records_in_identical_sequence_clusters"],
                    ),
                ]
            )
        )
        lines.extend(["<h2>Summary</h2>"])
        lines.extend(_duplicates_section(data))
        lines.extend(["</main>", "</body>", "</html>"])
        return "\n".join(lines)
    else:
        lines = [
            f"=== Duplicate report for {file_path} ===",
            f"Total records: {data['total_records']}",
            f"Duplicate IDs: {data['duplicate_id_count']}",
            f"Identical sequence clusters: {data['identical_sequence_cluster_count']}",
        ]
        if data["duplicate_ids"]:
            lines.append("\nDuplicate IDs:")
            for seq_id, count in sorted(data["duplicate_ids"].items()):
                lines.append(f"  {seq_id}: {count} records")
        if data["identical_sequence_clusters"]:
            lines.append("\nIdentical sequence clusters:")
            for i, cluster in enumerate(data["identical_sequence_clusters"], start=1):
                lines.append(f"  Cluster {i}: len={cluster['length']}, ids={', '.join(cluster['ids'])}")
        return "\n".join(lines)


def _compare_items_table(items, headers, row_builder, empty_message):
    """Return an HTML table for comparison items."""
    if not items:
        return [f'<p class="muted">{escape(empty_message)}</p>']

    lines = [
        "<table>",
        "<tr>" + "".join(f"<th>{escape(header)}</th>" for header in headers) + "</tr>",
    ]
    for item in items:
        cells = row_builder(item)
        lines.append("<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in cells) + "</tr>")
    lines.append("</table>")
    return lines


def _duplicate_cluster_changes_section(changes):
    """Return an HTML section for duplicate cluster changes."""
    lines = ["<h2>Duplicate cluster changes</h2>"]

    lines.extend(["<h3>Added clusters</h3>"])
    lines.extend(
        _compare_items_table(
            changes["added_clusters"],
            ["Length", "IDs", "Sequence preview"],
            lambda item: [
                item["length"],
                ", ".join(item["ids"]),
                item["sequence"][:60] + ("..." if len(item["sequence"]) > 60 else ""),
            ],
            "No added duplicate clusters.",
        )
    )

    lines.extend(["<h3>Removed clusters</h3>"])
    lines.extend(
        _compare_items_table(
            changes["removed_clusters"],
            ["Length", "IDs", "Sequence preview"],
            lambda item: [
                item["length"],
                ", ".join(item["ids"]),
                item["sequence"][:60] + ("..." if len(item["sequence"]) > 60 else ""),
            ],
            "No removed duplicate clusters.",
        )
    )

    lines.extend(["<h3>Changed clusters</h3>"])
    lines.extend(
        _compare_items_table(
            changes["changed_clusters"],
            ["Length", "Old IDs", "New IDs", "Added IDs", "Removed IDs"],
            lambda item: [
                item["length"],
                ", ".join(item["old_ids"]),
                ", ".join(item["new_ids"]),
                ", ".join(item["added_ids"]) or "-",
                ", ".join(item["removed_ids"]) or "-",
            ],
            "No changed duplicate clusters.",
        )
    )
    return lines


def format_compare_report(data, output_format):
    """Format comparison results into text, tsv, json, or html."""
    if output_format == "json":
        return json.dumps(data, indent=2)
    elif output_format == "tsv":
        lines = ["type\tid\told_length\tnew_length"]
        for item in data["added_ids"]:
            lines.append(f"added\t{item['id']}\t\t{item['new_length']}")

        for item in data["removed_ids"]:
            lines.append(f"removed\t{item['id']}\t{item['old_length']}\t")

        for item in data["changed_sequences"]:
            lines.append(f"changed\t{item['id']}\t{item['old_length']}\t{item['new_length']}")
        return "\n".join(lines)
    elif output_format == "html":
        summary = data["summary"]
        lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Comparison report</title>",
            "<style>",
            _html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<main>",
            "<header>",
            "<h1>Comparison report</h1>",
            '<p class="muted">Protein FASTA dataset comparison.</p>',
            "</header>",
        ]
        lines.extend(
            _cards(
                [
                    ("Old records", summary["old_total_records"]),
                    ("New records", summary["new_total_records"]),
                    ("Added IDs", summary["added_count"]),
                    ("Removed IDs", summary["removed_count"]),
                    ("Changed sequences", summary["changed_sequence_count"]),
                    (
                        "Changed clusters",
                        summary["changed_duplicate_cluster_count"],
                    ),
                ]
            )
        )
        lines.extend(
            [
                "<h2>Summary</h2>",
            ]
        )
        lines.extend(_metric_table(summary))
        lines.extend(
            [
                "<h2>Added IDs</h2>",
            ]
        )
        lines.extend(
            _compare_items_table(
                data["added_ids"],
                ["ID", "New length"],
                lambda item: [item["id"], item["new_length"]],
                "No added IDs.",
            )
        )
        lines.extend(
            [
                "<h2>Removed IDs</h2>",
            ]
        )
        lines.extend(
            _compare_items_table(
                data["removed_ids"],
                ["ID", "Old length"],
                lambda item: [item["id"], item["old_length"]],
                "No removed IDs.",
            )
        )
        lines.extend(
            [
                "<h2>Changed sequences</h2>",
            ]
        )
        lines.extend(
            _compare_items_table(
                data["changed_sequences"],
                ["ID", "Old length", "New length"],
                lambda item: [item["id"], item["old_length"], item["new_length"]],
                "No changed sequences.",
            )
        )
        lines.extend(_duplicate_cluster_changes_section(data["duplicate_cluster_changes"]))
        lines.extend(["</main>", "</body>", "</html>"])
        return "\n".join(lines)
    else:
        summary = data["summary"]
        lines = [
            "=== Comparison report ===",
            f"Old records: {summary['old_total_records']}",
            f"New records: {summary['new_total_records']}",
            f"Added IDs: {summary['added_count']}",
            f"Removed IDs: {summary['removed_count']}",
            f"Changed sequences: {summary['changed_sequence_count']}",
            f"Changed lengths: {summary['changed_length_count']}",
            "Duplicate clusters added/removed/changed: "
            f"{summary['added_duplicate_cluster_count']}/"
            f"{summary['removed_duplicate_cluster_count']}/"
            f"{summary['changed_duplicate_cluster_count']}",
        ]
        if data["added_ids"]:
            lines.append("\nAdded IDs: " + ", ".join(item["id"] for item in data["added_ids"]))
        if data["removed_ids"]:
            lines.append("Removed IDs: " + ", ".join(item["id"] for item in data["removed_ids"]))
        if data["changed_sequences"]:
            lines.append("Changed sequences:")
            for item in data["changed_sequences"]:
                lines.append(f"  {item['id']}: {item['old_length']} -> {item['new_length']}")
        return "\n".join(lines)
