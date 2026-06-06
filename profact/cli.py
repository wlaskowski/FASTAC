import argparse
import sys
from pathlib import Path
from .parser import read_fasta, validate_record, FastaParseError
from .duplicates import analyze_duplicates
from .compare import compare_files
from .stats import analyze_stats
from .reporter import (
    stats_to_text,
    stats_to_tsv,
    stats_to_json,
    stats_to_html,
    format_validation_report,
    build_full_report_data,
    full_report_to_text,
    full_report_to_tsv,
    full_report_to_json,
    full_report_to_html,
    format_duplicates_report,
    format_compare_report,
)


def write_output(output_str, output_file):
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_str)
    else:
        print(output_str)



def cmd_validate(args):
    file_path = args.fasta_file
    output_format = args.format
    output_file = args.output

    try:
        records = list(read_fasta(file_path))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except FastaParseError as e:
        print(f"ERROR: Invalid FASTA format: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    validated = []
    for rec in records:
        res = validate_record(rec)
        validated.append(
            {
                "id": rec.id,
                "description": rec.description,
                "sequence_length": len(rec.sequence),
                "valid": res["valid"],
                "errors": res["errors"],
                "warnings": res["warnings"],
                "has_x": res["has_x"],
                "has_stop": res["has_stop"],
                "is_empty": res["is_empty"],
                "invalid_chars": sorted(res["invalid_chars"]),
                "non_standard": sorted(res["non_standard"]),
            }
        )

    total = len(validated)
    valid_count = sum(1 for v in validated if v["valid"])
    invalid_count = total - valid_count
    records_with_x = sum(1 for v in validated if v["has_x"])
    records_with_stop = sum(1 for v in validated if v["has_stop"])
    empty_records = sum(1 for v in validated if v["is_empty"])

    summary = {
        "total_records": total,
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "records_with_X": records_with_x,
        "records_with_stop": records_with_stop,
        "empty_records": empty_records,
    }

    # Use the reporter function
    output_str = format_validation_report(file_path, validated, summary, output_format)

    write_output(output_str, output_file)
    sys.exit(0 if invalid_count == 0 else 1)


def cmd_duplicates(args):
    try:
        data = analyze_duplicates(args.fasta_file)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    output_str = format_duplicates_report(data, args.fasta_file, args.format)

    write_output(output_str, args.output)
    sys.exit(0)


def cmd_compare(args):
    try:
        data = compare_files(args.old_fasta, args.new_fasta)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    output_str = format_compare_report(data, args.format)

    write_output(output_str, args.output)
    has_changes = any(
        [
            data["summary"]["added_count"],
            data["summary"]["removed_count"],
            data["summary"]["changed_sequence_count"],
            data["summary"]["added_duplicate_cluster_count"],
            data["summary"]["removed_duplicate_cluster_count"],
            data["summary"]["changed_duplicate_cluster_count"],
        ]
    )
    sys.exit(1 if has_changes else 0)


def cmd_stats(args):
    try:
        data = analyze_stats(args.fasta_file)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        output_str = stats_to_json(data)
    elif args.format == "tsv":
        output_str = stats_to_tsv(data)
    elif args.format == "html":
        output_str = stats_to_html(data)
    else:
        output_str = stats_to_text(data)

    write_output(output_str, args.output)
    sys.exit(0)


def cmd_report(args):
    try:
        data = build_full_report_data(args.fasta_file)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        output_str = full_report_to_json(data)
    elif args.format == "tsv":
        output_str = full_report_to_tsv(data)
    elif args.format == "html":
        output_str = full_report_to_html(data)
    else:
        output_str = full_report_to_text(data)

    write_output(output_str, args.output)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog="profact", description="Protein FASTA analysis tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    val_parser = subparsers.add_parser("validate", help="Validate protein FASTA records")
    val_parser.add_argument("-i", "--input", dest="fasta_file", required=True, help="Input FASTA file (.fa, .fasta, .faa, .gz)")
    val_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv"], default="text", help="Output format")
    val_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    val_parser.set_defaults(func=cmd_validate)

    dup_parser = subparsers.add_parser("duplicates", help="Detect duplicate IDs and identical sequences")
    dup_parser.add_argument("-i", "--input", dest="fasta_file", required=True, help="Input FASTA file (.fa, .fasta, .faa, .gz)")
    dup_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv", "html"], default="text", help="Output format")
    dup_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    dup_parser.set_defaults(func=cmd_duplicates)

    cmp_parser = subparsers.add_parser("compare", help="Compare two protein FASTA files")
    cmp_parser.add_argument("-f1", "--file_1", metavar="FILE_1", dest="old_fasta", required=True, help="First FASTA file")
    cmp_parser.add_argument("-f2", "--file_2", metavar="FILE_2", dest="new_fasta", required=True, help="Second FASTA file")
    cmp_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv", "html"], default="text", help="Output format")
    cmp_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    cmp_parser.set_defaults(func=cmd_compare)

    stats_parser = subparsers.add_parser("stats", help="Compute protein FASTA statistics")
    stats_parser.add_argument("-i", "--input", dest="fasta_file", required=True, help="Input FASTA file (.fa, .fasta, .faa, .gz)")
    stats_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv", "html"], default="text", help="Output format")
    stats_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    stats_parser.set_defaults(func=cmd_stats)

    report_parser = subparsers.add_parser("report", help="Generate full protein FASTA report")
    report_parser.add_argument("-i", "--input", dest="fasta_file", required=True, help="Input FASTA file (.fa, .fasta, .faa, .gz)")
    report_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv", "html"], default="text", help="Output format")
    report_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
