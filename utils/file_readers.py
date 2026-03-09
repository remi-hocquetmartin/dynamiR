"""
================================================================================
FILE I/O UTILITIES - SEQUENCE FILE READERS
================================================================================

PURPOSE:
    Provides functions for reading nucleotide sequence files in common
    bioinformatics formats (FASTA, GenBank).

SUPPORTED FORMATS:
    - FASTA (.fa, .fasta): Simple sequence format
    - GenBank (.gb, .gbk): Annotated sequence format with metadata
================================================================================
"""

from Bio import SeqIO
import os


def read_sequence_from_file(path):
    """
    Read the first sequence from a FASTA or GenBank format file.
    
    Automatically detects format based on file extension.
    Converts DNA to RNA (T→U) and normalizes to uppercase.
    
    Args:
        path (str): Path to sequence file (.fa, .fasta, .gb, or .gbk)
    
    Returns:
        tuple: (sequence_string, metadata_dict)
               - sequence_string: Uppercase RNA sequence
               - metadata_dict: Contains {"id": record_id, "description": description}
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is unsupported or empty
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    # Detect format based on file extension
    ext = os.path.splitext(path)[1].lower()
    fmt = "fasta" if ext in [".fa", ".fasta"] else "genbank"

    # Read first sequence record
    with open(path) as f:
        rec = next(SeqIO.parse(f, fmt))
    
    # Convert to uppercase RNA
    sequence = str(rec.seq).upper().replace("T", "U")
    
    # Extract metadata
    metadata = {
        "id": rec.id, 
        "description": rec.description
    }
    
    return sequence, metadata

