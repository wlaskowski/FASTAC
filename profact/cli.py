import argparse
import sys
import json
from pathlib import Path
from .parser import read_fasta, validate_record, FastaParseError
from .duplicates import analyze_duplicates
from .compare import compare_files


def write_output(output_str, output_file):
    if output_file:
        Path(output_file).write_text(output_str)
    else:
        print(output_str)


def as_json(data):
    return json.dumps(data, indent=2)


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
        validated.append({
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
        })

    total = len(validated)
    valid_count = sum(1 for v in validated if v["valid"])
    invalid_count = total - valid_count
    records_with_x = sum(1 for v in validated if v["has_x"])
    records_with_stop = sum(1 for v in validated if v["has_stop"])
    empty_records = sum(1 for v in validated if v["is_empty"])

    if output_format == "json":
        output_str = as_json({
            "file": file_path,
            "summary": {
                "total_records": total,
                "valid_records": valid_count,
                "invalid_records": invalid_count,
                "records_with_X": records_with_x,
                "records_with_stop": records_with_stop,
                "empty_records": empty_records,
            },
            "records": validated,
        })
    elif output_format == "tsv":
        lines = ["id\tvalid\terrors\twarnings\thas_x\thas_stop\tis_empty"]
        for v in validated:
            lines.append(
                f"{v['id']}\t{v['valid']}\t{';'.join(v['errors'])}\t"
                f"{';'.join(v['warnings'])}\t{v['has_x']}\t{v['has_stop']}\t{v['is_empty']}"
            )
        output_str = "\n".join(lines)
    else:
        lines = [
            f"=== Validation report for {file_path} ===",
            f"Total records: {total}",
            f"Valid: {valid_count}, Invalid: {invalid_count}",
            f"Records with 'X': {records_with_x}, with '*': {records_with_stop}, empty: {empty_records}\n",
        ]
        for v in validated:
            if v["errors"] or v["warnings"]:
                lines.append(f"> {v['id']} (len={v['sequence_length']})")
                for err in v["errors"]:
                    lines.append(f"  ERROR: {err}")
                for warn in v["warnings"]:
                    lines.append(f"  WARN:  {warn}")
        output_str = "\n".join(lines)

    write_output(output_str, output_file)
    sys.exit(0 if invalid_count == 0 else 1)


def cmd_duplicates(args):
    try:
        data = analyze_duplicates(args.fasta_file)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        output_str = as_json(data)
    elif args.format == "tsv":
        lines = ["cluster_no\tlength\tcount\tids"]
        for i, cluster in enumerate(data["identical_sequence_clusters"], start=1):
            lines.append(f"{i}\t{cluster['length']}\t{cluster['count']}\t{','.join(cluster['ids'])}")
        output_str = "\n".join(lines)
    else:
        lines = [
            f"=== Duplicate report for {args.fasta_file} ===",
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
        output_str = "\n".join(lines)

    write_output(output_str, args.output)
    sys.exit(0)


def cmd_compare(args):
    try:
        data = compare_files(args.old_fasta, args.new_fasta)
    except (FileNotFoundError, FastaParseError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        output_str = as_json(data)
    elif args.format == "tsv":
        lines = ["type\tid\told_length\tnew_length"]
        for item in data["added_ids"]:
            lines.append(f"added\t{item['id']}\t\t{item['new_length']}")

        for item in data["removed_ids"]:
            lines.append(f"removed\t{item['id']}\t{item['old_length']}\t")

        for item in data["changed_sequences"]:
            lines.append(f"changed\t{item['id']}\t{item['old_length']}\t{item['new_length']}")
            output_str = "\n".join(lines)
    else:
        s = data["summary"]
        lines = [
            f"=== Comparison report ===",
            f"Old records: {s['old_total_records']}",
            f"New records: {s['new_total_records']}",
            f"Added IDs: {s['added_count']}",
            f"Removed IDs: {s['removed_count']}",
            f"Changed sequences: {s['changed_sequence_count']}",
            f"Changed lengths: {s['changed_length_count']}",
            f"Duplicate clusters added/removed/changed: "
            f"{s['added_duplicate_cluster_count']}/{s['removed_duplicate_cluster_count']}/{s['changed_duplicate_cluster_count']}",
        ]
        if data["added_ids"]:
            lines.append("\nAdded IDs: " + ", ".join(item["id"] for item in data["added_ids"]))
        if data["removed_ids"]:
            lines.append("Removed IDs: " + ", ".join(item["id"] for item in data["removed_ids"]))
        if data["changed_sequences"]:
            lines.append("Changed sequences:")
            for item in data["changed_sequences"]:
                lines.append(f"  {item['id']}: {item['old_length']} -> {item['new_length']}")
        output_str = "\n".join(lines)

    write_output(output_str, args.output)
    has_changes = any([
        data["summary"]["added_count"],
        data["summary"]["removed_count"],
        data["summary"]["changed_sequence_count"],
        data["summary"]["added_duplicate_cluster_count"],
        data["summary"]["removed_duplicate_cluster_count"],
        data["summary"]["changed_duplicate_cluster_count"],
    ])
    sys.exit(1 if has_changes else 0)


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
    dup_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv"], default="text", help="Output format")
    dup_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    dup_parser.set_defaults(func=cmd_duplicates)

    cmp_parser = subparsers.add_parser("compare", help="Compare two protein FASTA files")
    cmp_parser.add_argument("-f1", "--file_1", metavar="FILE_1",dest="old_fasta", required=True, help="First FASTA file")
    cmp_parser.add_argument("-f2", "--file_2", metavar="FILE_2", dest="new_fasta", required=True, help="Second FASTA file")
    cmp_parser.add_argument("-fmt", "--format", choices=["text", "json", "tsv"], default="text", help="Output format")
    cmp_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    cmp_parser.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
