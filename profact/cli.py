import argparse
import sys
import json
from pathlib import Path
from .parser import read_fasta, validate_record, FastaParseError

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

    # Validate each record
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
            "invalid_chars": list(res["invalid_chars"]),
            "non_standard": list(res["non_standard"])
        })

    # Summary
    total = len(validated)
    valid_count = sum(1 for v in validated if v["valid"])
    invalid_count = total - valid_count
    records_with_x = sum(1 for v in validated if v["has_x"])
    records_with_stop = sum(1 for v in validated if v["has_stop"])
    empty_records = sum(1 for v in validated if v["is_empty"])

    # Prepare output
    if output_format == "json":
        out_data = {
            "file": file_path,
            "summary": {
                "total_records": total,
                "valid_records": valid_count,
                "invalid_records": invalid_count,
                "records_with_X": records_with_x,
                "records_with_stop": records_with_stop,
                "empty_records": empty_records
            },
            "records": validated
        }
        output_str = json.dumps(out_data, indent=2)
    elif output_format == "tsv":
        lines = ["id\tvalid\terrors\twarnings\thas_x\thas_stop\tis_empty"]
        for v in validated:
            errors_str = ";".join(v["errors"])
            warnings_str = ";".join(v["warnings"])
            lines.append(f"{v['id']}\t{v['valid']}\t{errors_str}\t{warnings_str}\t{v['has_x']}\t{v['has_stop']}\t{v['is_empty']}")
        output_str = "\n".join(lines)
    else:  # text (default)
        lines = []
        lines.append(f"=== Validation report for {file_path} ===")
        lines.append(f"Total records: {total}")
        lines.append(f"Valid: {valid_count}, Invalid: {invalid_count}")
        lines.append(f"Records with 'X': {records_with_x}, with '*': {records_with_stop}, empty: {empty_records}\n")
        for v in validated:
            if v["errors"] or v["warnings"]:
                lines.append(f"> {v['id']} (len={v['sequence_length']})")
                for err in v["errors"]:
                    lines.append(f"  ERROR: {err}")
                for warn in v["warnings"]:
                    lines.append(f"  WARN:  {warn}")
        output_str = "\n".join(lines)

    # Write output
    if output_file:
        Path(output_file).write_text(output_str)
    else:
        print(output_str)

    # Exit with error code if any invalid record
    sys.exit(0 if invalid_count == 0 else 1)

def main():
    parser = argparse.ArgumentParser(prog="profact", description="Protein FASTA analysis tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate command
    val_parser = subparsers.add_parser("validate", help="Validate protein FASTA records")
    val_parser.add_argument("fasta_file", help="Input FASTA file (.fa, .fasta, .faa, .gz)")
    val_parser.add_argument("--format", choices=["text", "json", "tsv"], default="text", help="Output format")
    val_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    val_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()