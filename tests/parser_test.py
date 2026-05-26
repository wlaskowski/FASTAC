import pytest
import tempfile
import gzip
from pathlib import Path
from profact.parser import read_fasta, validate_record, FastaRecord, FastaParseError, validate_file

# Helper to create temporary FASTA content
def write_fasta(content: str, suffix=".fasta"):
    f = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    f.write(content)
    f.close()
    return f.name

def write_gzipped(content: bytes, suffix=".fa.gz"):
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    with gzip.open(f.name, 'wb') as gz:
        gz.write(content)
    f.close()
    return f.name

# ---------- read_fasta tests ----------
def test_read_fasta_normal():
    content = """>sp|P123|PROT_HUMAN My protein
MKTIIALSYIFCLVFA
DYKDDDDK
>tr|A0A123|PROT2
MAPRSSS
"""
    fname = write_fasta(content)
    records = list(read_fasta(fname))
    assert len(records) == 2
    assert records[0].id == "sp|P123|PROT_HUMAN"
    assert records[0].description == "My protein"
    assert records[0].sequence == "MKTIIALSYIFCLVFADYKDDDDK"
    assert records[1].id == "tr|A0A123|PROT2"
    assert records[1].description == ""
    assert records[1].sequence == "MAPRSSS"

def test_read_fasta_gzipped():
    content = b">ID1 desc\nACGT\n>ID2\nXYZW\n"
    fname = write_gzipped(content)
    records = list(read_fasta(fname))
    assert len(records) == 2
    assert records[0].id == "ID1"
    assert records[0].sequence == "ACGT"
    assert records[1].id == "ID2"
    assert records[1].sequence == "XYZW"

def test_read_fasta_extra_whitespace():
    content = """>ID1   description with spaces
    MK TII A LS Y   IF
>ID2
   MAPR  SSS   
"""
    fname = write_fasta(content)
    records = list(read_fasta(fname))
    assert records[0].sequence == "MKTIIALSYIF"
    assert records[1].sequence == "MAPRSSS"

def test_read_fasta_empty_file():
    fname = write_fasta("")
    records = list(read_fasta(fname))
    assert records == []


def test_read_fasta_empty_header():
    content = """>
MKTII
>ID2
MAPR
"""
    fname = write_fasta(content)
    with pytest.raises(FastaParseError, match="Empty header"):
        list(read_fasta(fname))

# ---------- validate_record tests ----------
def test_validate_perfect():
    rec = FastaRecord("ID1", "", "MKTIIALSYIFCLVFA")
    res = validate_record(rec)
    assert res["valid"] is True
    assert res["errors"] == []
    assert res["warnings"] == []
    assert res["has_x"] is False
    assert res["has_stop"] is False
    assert res["invalid_chars"] == set()
    assert res["non_standard"] == set()

def test_validate_with_x_and_stop():
    rec = FastaRecord("ID2", "", "MKTXIIALS*YIF")
    res = validate_record(rec)
    assert res["valid"] is True  # warnings only
    assert res["warnings"] == ["Contains unknown residue 'X'", "Contains stop symbol '*'"]
    assert res["has_x"] is True
    assert res["has_stop"] is True

def test_validate_invalid_chars():
    rec = FastaRecord("ID3", "", "MKTIIALBZJ123")
    res = validate_record(rec)
    assert res["valid"] is False
    assert "Invalid character(s): 1, 2, 3" in res["errors"][0]
    assert res["warnings"] == ["Non-standard amino acid(s): B, J, Z (B=Asx, Z=Glx, J=Xle)"]
    assert res["invalid_chars"] == {"1","2","3"}
    assert res["non_standard"] == {"B","J","Z"}

def test_validate_empty_sequence():
    rec = FastaRecord("ID4", "", "")
    res = validate_record(rec)
    assert res["valid"] is False
    assert "Empty sequence" in res["errors"]
    assert res["is_empty"] is True

def test_validate_lowercase():
    # Lowercase letters are invalid in strict protein FASTA
    rec = FastaRecord("ID5", "", "mktii")
    res = validate_record(rec)
    assert res["valid"] is False
    error_msg = res["errors"][0]
    assert res["invalid_chars"] == {"m", "k", "t", "i"}
    
# ---------- validate_file integration ----------
def test_validate_file(tmp_path):
    content = """>good
MKTIIALSY
>badX
MKTX
>invalid
MKTIIALB123
>empty

>stop
MKT*
"""
    fasta_file = tmp_path / "test.fasta"
    fasta_file.write_text(content)
    records, results = validate_file(str(fasta_file))
    assert len(records) == 5
    assert results[0]["valid"] is True
    assert results[1]["valid"] is True
    assert results[1]["has_x"] is True
    assert results[2]["valid"] is False
    assert "Invalid character(s): 1, 2, 3" in results[2]["errors"][0]
    assert results[3]["valid"] is False
    assert results[3]["is_empty"] is True
    assert results[4]["valid"] is True
    assert results[4]["has_stop"] is True