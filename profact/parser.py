"""FASTA parsing and validation for protein sequences."""
import gzip
import sys
from pathlib import Path
from typing import Iterator, Dict, Set, List, Tuple, Optional
import re

# Standard 20 amino acids
STD_AA = set("ACDEFGHIKLMNPQRSTVWY")
# Allowed with warnings
WARN_AA = {"X", "*"}   # X = unknown, * = stop
# Non-standard or ambiguous but sometimes seen (U) selenocysteine, (O) pyrrolysine, (B) either aspartic acid or asparagine
# (Z) either glutamic acid or glutamine, (J) either leucine or isoleucine
NON_STD = {"U", "O", "B", "Z", "J"}
# All characters that are not immediately rejected
VALID_CHARS = STD_AA | WARN_AA | NON_STD

class FastaRecord:
    __slots__ = ("id", "description", "sequence")
    def __init__(self, id: str, description: str, sequence: str):
        self.id = id
        self.description = description
        self.sequence = sequence

    def __repr__(self):
        return f"FastaRecord(id={self.id!r}, seq_len={len(self.sequence)})"

class FastaParseError(Exception):
    """Raised when FASTA format is malformed."""
    pass

def read_fasta(file_path: str) -> Iterator[FastaRecord]:
    """
    Yield FastaRecord objects from a FASTA file (plain or .gz).
    Raises FastaParseError if a record header does not start with '>'.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    open_func = gzip.open if path.suffix == '.gz' else open
    mode = 'rt' if path.suffix == '.gz' else 'r'

    with open_func(path, mode) as f:
        current_id = None
        current_desc = ""
        current_seq_lines = []
        line_num = 0

        for line in f:
            line_num += 1
            line = line.rstrip('\n\r')
            if not line:
                continue
            if line[0] == '>':
                # yield previous record
                if current_id is not None:
                    seq = ''.join(current_seq_lines)
                    yield FastaRecord(current_id, current_desc, seq)
                # parse header
                header = line[1:].strip()
                if not header:
                    raise FastaParseError(f"Empty header after '>' at line {line_num}")
                parts = header.split(maxsplit=1)
                current_id = parts[0]
                current_desc = parts[1] if len(parts) > 1 else ""
                current_seq_lines = []
            else:
                # sequence line – remove all whitespace
                current_seq_lines.append(re.sub(r'\s+', '', line))

        # last record
        if current_id is not None:
            seq = ''.join(current_seq_lines)
            yield FastaRecord(current_id, current_desc, seq)
        elif line_num == 0:
            # empty file
            return
        else:
            raise FastaParseError("File ended without a record (missing '>'?)")

def validate_record(record: FastaRecord) -> Dict[str, any]:
    """
    Validate a single protein FASTA record.
    Returns dict with:
        valid (bool)
        errors (list of str)
        warnings (list of str)
        has_x (bool)
        has_stop (bool)
        invalid_chars (set)
        non_standard (set)
        is_empty (bool)
    """
    errors = []
    warnings = []
    seq = record.sequence
    has_x = 'X' in seq
    has_stop = '*' in seq
    is_empty = len(seq) == 0

    # Find invalid characters (anything not in VALID_CHARS)
    invalid_chars = set(seq) - VALID_CHARS
    if invalid_chars:
        errors.append(f"Invalid character(s): {', '.join(sorted(invalid_chars))}")

    if is_empty:
        errors.append("Empty sequence")

    # Warnings
    if has_x:
        warnings.append("Contains unknown residue 'X'")
    if has_stop:
        warnings.append("Contains stop symbol '*'")

    non_standard = set(seq) & NON_STD
    if non_standard:
        warnings.append(f"Non-standard amino acid(s): {', '.join(sorted(non_standard))} (B=Asx, Z=Glx, J=Xle)")

    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "has_x": has_x,
        "has_stop": has_stop,
        "invalid_chars": invalid_chars,
        "non_standard": non_standard,
        "is_empty": is_empty,
    }

def validate_file(file_path: str) -> Tuple[List[FastaRecord], List[Dict]]:
    """
    Parse all records from a FASTA file and validate each.
    Returns (records, validation_results) where validation_results[i] corresponds to records[i].
    """
    records = list(read_fasta(file_path))
    results = [validate_record(rec) for rec in records]
    return records, results
