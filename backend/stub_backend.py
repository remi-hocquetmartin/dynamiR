"""
================================================================================
DynamiR - MICRORINA BINDING SITE ANALYSIS ALGORITHMS - BACKEND
================================================================================

PURPOSE:
    Implements core algorithms for identifying microRNA binding sites on
    target mRNA sequences. Supports two analysis modes:
    
    1. MATCHING MODE (backend_match_micro_to_mrna):
       Direct alignment of a user-provided microRNA against a user-provided mRNA
       to identify binding sites within a specified seed region.
    
    2. DYNAMITE MODE (backend_dynamite_on_mrna):
       High-throughput scanning of the entire microRNA database against a
       user-provided mRNA to identify all binding microRNAs.

KEY CONCEPTS:
    - Seed Region: Initial pairing region (typically nucleotides 2-7 of microRNA)
                   where Watson-Crick base pairing is essential for binding.
    - Watson-Crick Pairing: Canonical base pairs (A-U, C-G) with strong stability.
    - Wobble Pairing: Non-canonical G-U pair with reduced but significant stability.
    - Reverse Complement: microRNA sequence is reverse-complemented to form duplex.
    - Target Site: Position in mRNA where microRNA reverse complement matches.

SEQUENCE PROCESSING:
    - All sequences are converted to uppercase
    - DNA (T) is converted to RNA (U)
    - Handles both raw sequences and BioPython SeqRecord objects
    - Database sequences are extracted from EMBL format (.dat files)

RESULT SCORING:
    - Counts Watson-Crick pairs (full score)
    - Counts wobble pairs (half score)
    - Calculates binding percentage relative to microRNA length
    - Reports positions of supplementary pairings outside seed region
================================================================================
"""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO, Entrez
import sys
import ssl
import urllib.request

"""
SSL CERTIFICATE HANDLING FOR NCBI ENTREZ REQUESTS:
    
    Bio.Entrez internally uses urllib which verifies SSL certificates.
    NCBI servers occasionally present self-signed certificates that cause
    verification failures in strict SSL mode.
    
    Solution: Bypass SSL verification for NCBI connections.
    This is acceptable in research/academic context for public databases.
"""

# Create unverified SSL context for NCBI connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create HTTPS handler with unverified context
https_handler = urllib.request.HTTPSHandler(context=ssl_context)

# Install custom opener that uses unverified SSL for all urllib requests
opener = urllib.request.build_opener(https_handler)
urllib.request.install_opener(opener)

# File I/O utilities
from utils.file_readers import read_sequence_from_file


# ================================================================================
# PYINSTALLER PATH HANDLING
# ================================================================================

def get_resource_path(relative_path):
    """
    Get correct path to resource files for both development and PyInstaller builds.
    
    When running as PyInstaller executable, bundled files are in sys._MEIPASS.
    When running from source, files are in normal project directories.
    
    Args:
        relative_path (str): Path relative to project root (e.g., 'data/miRNA.dat')
    
    Returns:
        str: Absolute path to the resource file
    """
    import os
    
    # Check if running as PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundles files in _MEIPASS directory
        base_path = sys._MEIPASS
    else:
        # Running from source - use project root
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

def get_miRNA(mirna_id, filepath="data/miRNA.dat"):
    """
    Retrieve a mature microRNA sequence from the microRNA database (EMBL format).
    
    The miRNA database contains hairpin precursors with mature regions
    annotated as "miRNA" features. This function locates the mature sequence
    corresponding to the provided accession ID.
    
    Args:
        mirna_id (str): Mature microRNA accession ID (e.g., "MIMAT0000062")
        filepath (str): Path to miRNA.dat database file (relative to project root)
    
    Returns:
        Bio.SeqRecord.SeqRecord: Sequence record containing:
            - id: microRNA accession ID
            - seq: RNA sequence (T→U converted)
            - annotations: species, hairpin ID, hairpin sequence
        or None if ID not found
    """
    # Get correct path for PyInstaller bundles and source execution
    filepath = get_resource_path(filepath)
    
    for record in SeqIO.parse(filepath, "embl"):
        for feature in record.features:
            if feature.type == "miRNA" and "accession" in feature.qualifiers:
                if feature.qualifiers["accession"][0] == mirna_id:
                    # Extract mature microRNA sequence from feature location
                    seq = record.seq[feature.location.start:feature.location.end]
                    
                    # Extract metadata
                    name = feature.qualifiers.get("product", ["?"])[0]
                    species = " ".join(record.description.split()[:2])
                    
                    # Create SeqRecord for mature microRNA
                    mature_record = SeqRecord(
                        Seq(str(seq).replace('T', 'U')),
                        id=mirna_id,
                        name=name,
                        description=record.description,
                    )
                    
                    # Store hairpin information for reference
                    mature_record.annotations["species"] = species
                    mature_record.annotations["hairpin_id"] = record.id
                    mature_record.annotations["hairpin_sequence"] = str(record.seq.replace('T', 'U'))
                    
                    return mature_record
    
    return None


def get_3utr_record_from_file(genbank_file):
    """
    Extract 3' UTR (untranslated region) sequence from a GenBank file.
    
    The 3'UTR is the target region for microRNA binding in eukaryotic cells.
    This function identifies the coding region (CDS) and extracts the sequence
    following the stop codon.
    
    Args:
        genbank_file (str): Path to GenBank format file (.gb or .gbk)
    
    Returns:
        Bio.SeqRecord.SeqRecord: Sequence record containing:
            - id: Accession ID with "_3UTR" suffix
            - seq: 3'UTR sequence (T→U converted)
            - annotations: Gene name, organism, product, protein ID, etc.
    """
    record = SeqIO.read(genbank_file, "genbank")

    # Find first CDS feature (main protein-coding gene)
    cds_feature = next(f for f in record.features if f.type == "CDS")
    
    cds_start = int(cds_feature.location.start)
    cds_end = int(cds_feature.location.end)
    
    # Extract 3'UTR (sequence after stop codon)
    utr3_seq = record.seq[cds_end:]
    
    # Extract gene metadata
    gene_name = cds_feature.qualifiers.get("gene", ["unknown_gene"])[0]
    product = cds_feature.qualifiers.get("product", ["unknown_protein"])[0]
    protein_id = cds_feature.qualifiers.get("protein_id", ["?"])[0]
    organism = record.annotations.get("organism", "?")
    accession = record.id
    description = record.description

    # Create SeqRecord for 3'UTR
    utr_record = SeqRecord(
        Seq(str(utr3_seq).replace('T', 'U')),
        id=f"{accession}_3UTR",
        name=gene_name,
        description=f"3'UTR of {gene_name} ({organism})",
    )
    
    # Store rich metadata for reference
    utr_record.annotations["organism"] = organism
    utr_record.annotations["source_accession"] = accession
    utr_record.annotations["gene_name"] = gene_name
    utr_record.annotations["product"] = product
    utr_record.annotations["protein_id"] = protein_id
    utr_record.annotations["cds_location"] = (cds_start, cds_end)
    utr_record.annotations["utr_length"] = len(utr3_seq)
    utr_record.annotations["source_description"] = description
    utr_record.annotations["date"] = record.annotations.get("date", "?")
    utr_record.annotations["taxonomy"] = record.annotations.get("taxonomy", [])
    
    return utr_record


def get_3utr_from_id(genbank_id):
    """
    Fetch 3'UTR sequence from NCBI database using GenBank accession ID.
    
    Connects to NCBI Entrez service to download GenBank record for the
    specified accession, then extracts the 3'UTR.
    
    Args:
        genbank_id (str): NCBI GenBank accession ID (e.g., "NM_000546.6")
    
    Returns:
        Bio.SeqRecord.SeqRecord: 3'UTR sequence record with annotations
    
    Requires:
        - Active internet connection to NCBI
        - Entrez.email set to valid email address
    """
    Entrez.email = "xxx@gmail.com"
    
    # Download GenBank record from NCBI
    handle = Entrez.efetch(
        db="nucleotide",
        id=genbank_id,
        rettype="gb",
        retmode="text"
    )
    record = SeqIO.read(handle, "genbank")
    handle.close()

    # Find first CDS feature
    cds_feature = next(f for f in record.features if f.type == "CDS")
    cds_start = int(cds_feature.location.start)
    cds_end = int(cds_feature.location.end)

    # Extract 3'UTR
    utr3_seq = record.seq[cds_end:]

    # Extract metadata
    gene_name = cds_feature.qualifiers.get("gene", ["unknown_gene"])[0]
    product = cds_feature.qualifiers.get("product", ["unknown_protein"])[0]
    protein_id = cds_feature.qualifiers.get("protein_id", ["?"])[0]
    organism = record.annotations.get("organism", "?")
    accession = record.id
    description = record.description

    # Create SeqRecord for 3'UTR
    utr_record = SeqRecord(
        Seq(str(utr3_seq).replace("T", "U")),
        id=f"{accession}_3UTR",
        name=gene_name,
        description=f"3'UTR of {gene_name} ({organism})",
    )

    # Store metadata
    utr_record.annotations["organism"] = organism
    utr_record.annotations["source_accession"] = accession
    utr_record.annotations["gene_name"] = gene_name
    utr_record.annotations["product"] = product
    utr_record.annotations["protein_id"] = protein_id
    utr_record.annotations["cds_location"] = (cds_start, cds_end)
    utr_record.annotations["utr_length"] = len(utr3_seq)
    utr_record.annotations["source_description"] = description
    utr_record.annotations["date"] = record.annotations.get("date", "?")
    utr_record.annotations["taxonomy"] = record.annotations.get("taxonomy", [])

    return utr_record


# ================================================================================
# MATCHING FUNCTIONS: Find binding sites between two sequences
# ================================================================================

def find_mrna_binding_sites(miRNA, mRNA, start_index, end_index):
    """
    Identify all exact matching positions of microRNA reverse complement in mRNA.
    
    Implements seed-based matching where only the seed region (specified by
    start_index and end_index) must match perfectly.
    
    Args:
        miRNA (SeqRecord or Seq or str): microRNA sequence
        mRNA (SeqRecord or Seq or str): Target mRNA sequence
        start_index (int): Start position of seed region (1-based)
        end_index (int): End position of seed region (1-based)
    
    Returns:
        list: Positions (1-based) in mRNA where seed region reverse complement matches
              (Converted from 0-based .find() results for biological convention)
    """
    positions = []
    start = 0

    # Handle different input types
    if isinstance(miRNA, SeqRecord):
        miRNA = miRNA.seq[start_index-1:end_index]
    if isinstance(mRNA, SeqRecord):
        mRNA = mRNA.seq

    # Ensure both are Seq objects
    if not isinstance(miRNA, Seq):
        miRNA = Seq(str(miRNA)[start_index-1:end_index])
    if not isinstance(mRNA, Seq):
        mRNA = Seq(str(mRNA))

    # Get reverse complement (for RNA pairing)
    miRNA_rc = miRNA.reverse_complement_rna()

    # Find all binding sites (exact matches of reverse complement)
    while True:
        idx = str(mRNA).find(str(miRNA_rc), start)
        if idx == -1:
            break
        # Convert from 0-based (Python indexing) to 1-based (biological convention)
        positions.append(idx + 1)
        start = idx + 1

    return positions


# ================================================================================
# ALIGNMENT VISUALIZATION FUNCTIONS
# ================================================================================

def plot_alignment(miRNA, mRNA, seed_start, seed_end, binding_position, window=30):
    """
    Visualize microRNA-mRNA duplex alignment at a specific binding position.
    
    Creates a formatted text representation showing:
    - microRNA sequence (reverse orientation)
    - Base pairing symbols (| for Watson-Crick, : for wobble, space for mismatch)
    - mRNA sequence
    - Seed region markers (*)
    - Pairing statistics
    
    Args:
        miRNA (SeqRecord): microRNA sequence record
        mRNA (SeqRecord): mRNA sequence record
        seed_start (int): Start position of seed region (1-based)
        seed_end (int): End position of seed region (1-based)
        binding_position (int): Position in mRNA where binding starts (1-based, biological convention)
        window (int): Nucleotides to show beyond seed region on each side
    
    Returns:
        str: Formatted alignment string
    """
    output = []
    
    # Complement mapping for RNA
    complement = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G'}
    
    # Get uppercase sequences
    mirna_seq = str(miRNA.seq).upper()
    mrna_seq = str(mRNA.seq).upper()
    
    seed_length = seed_end - seed_start + 1
    
    # Convert 1-based binding_position to 0-based for internal calculations
    binding_pos_0 = binding_position - 1
    
    # Calculate display region coordinates
    mirna_display_start = max(0, seed_start - window - 1)
    mirna_display_end = min(len(mirna_seq) - 1, seed_end + window - 1)
    
    # Calculate corresponding mRNA region
    mirna_align_for_mirna_0 = binding_pos_0 + seed_end
    mrna_align_for_mirna_0 = binding_pos_0 + seed_end - 1
    
    mrna_end_pos = mrna_align_for_mirna_0 - mirna_display_start
    mrna_start_pos = mrna_align_for_mirna_0 - mirna_display_end
    
    # Adjust if display region exceeds mRNA boundaries
    if mrna_start_pos < 0:
        diff = -mrna_start_pos
        mrna_start_pos = 0
        mirna_display_end -= diff
        mrna_end_pos = mrna_align_for_mirna_0 - mirna_display_start
    
    if mrna_end_pos >= len(mrna_seq):
        diff = mrna_end_pos - len(mrna_seq) + 1
        mrna_end_pos = len(mrna_seq) - 1
        mirna_display_start += diff
        mrna_start_pos = mrna_align_for_mirna_0 - mirna_display_end
    
    # Extract display sequences
    mirna_display = mirna_seq[mirna_display_start:mirna_display_end + 1]
    mrna_display = mrna_seq[mrna_start_pos:mrna_end_pos + 1]
    
    # Reverse microRNA for visualization (since it pairs in reverse orientation)
    mirna_display_rev = mirna_display[::-1]
    
    # Generate base pairing line
    match_line = []
    for i in range(len(mirna_display_rev)):
        if i < len(mrna_display):
            mirna_nt = mirna_display_rev[i]
            mrna_nt = mrna_display[i]
            
            if mirna_nt in complement and complement[mirna_nt] == mrna_nt:
                match_line.append('|')  # Watson-Crick
            elif (mirna_nt == 'G' and mrna_nt == 'U') or (mirna_nt == 'U' and mrna_nt == 'G'):
                match_line.append(':')  # Wobble
            else:
                match_line.append(' ')  # Mismatch
        else:
            match_line.append(' ')
    
    match_string = ''.join(match_line)
    
    # Mark seed region in mRNA
    seed_marker_string = []
    for i in range(len(mrna_display)):
        mirna_original_idx = mirna_display_end - i
        
        if seed_start <= (mirna_original_idx + 1) <= seed_end:
            seed_marker_string.append('*')
        else:
            seed_marker_string.append(' ')
    
    seed_marker_string = ''.join(seed_marker_string)

    # Format output with coordinates
    mirna_coord_left = mirna_display_end + 1
    mirna_coord_right = mirna_display_start + 1 
    
    mrna_coord_left = mrna_start_pos + 1
    mrna_coord_right = mrna_end_pos + 1
    
    # Build display strings with coordinate padding
    raw_lbl_mir_left = f"3' ({mirna_coord_left})"
    raw_lbl_mr_left = f"5' ({mrna_coord_left})"
    
    max_len_left = max(len(raw_lbl_mir_left), len(raw_lbl_mr_left))
    
    prefix_mirna = raw_lbl_mir_left.ljust(max_len_left) + "  "
    prefix_mrna = raw_lbl_mr_left.ljust(max_len_left) + "  "
    
    padding_left = " " * len(prefix_mirna)

    raw_coord_mir_right = f"({mirna_coord_right})"
    raw_coord_mr_right = f"({mrna_coord_right})"
    
    max_len_coords_right = max(len(raw_coord_mir_right), len(raw_coord_mr_right))
    
    suffix_mirna = f"  {raw_coord_mir_right.ljust(max_len_coords_right)} 5' (microRNA): {miRNA.id}"
    suffix_mrna = f"  {raw_coord_mr_right.ljust(max_len_coords_right)} 3' (mRNA): {mRNA.id}"

    # Build output lines - display binding_position directly (now 1-based)
    output.append(f"mRNA binding position: {binding_position}")
    output.append(f"microRNA region: {mirna_display_start+1:>4}-{mirna_display_end+1:<4}")
    output.append(f"mRNA region:     {mrna_start_pos+1:>4}-{mrna_end_pos+1:<4}")
    output.append("")
    
    # Alignment block
    output.append(f"{prefix_mirna}{mirna_display_rev}{suffix_mirna}")
    output.append(f"{padding_left}{match_string}")
    output.append(f"{prefix_mrna}{mrna_display}{suffix_mrna}")
    output.append(f"{padding_left}{seed_marker_string} (seed)")

    # Compute and display statistics
    total_matches = match_string.count('|') + match_string.count(':')
    watson_crick = match_string.count('|')
    wobble = match_string.count(':')
    
    seed_region_matches = 0
    for i, marker in enumerate(seed_marker_string):
        if marker == '*' and i < len(match_string) and match_string[i] in '|:':
            seed_region_matches += 1

    output.append("\n")
    output.append("Statistics:")
    output.append(f"  - Watson-Crick pairs: {watson_crick}")
    output.append(f"  - Wobble pairs (G-U): {wobble}")
    output.append(f"  - Total pairs: {total_matches}/{len(match_string)}")
    output.append(f"  - Seed region pairs: {seed_region_matches}/{seed_length}")
    output.append("\n")
    output.append("—" * 30)
    output.append("\n")
    
    return "\n".join(output)


# ================================================================================
# MATCHING MODE: Direct microRNA-to-mRNA Analysis
# ================================================================================

def backend_match_micro_to_mrna(micro_seq, mrna_seq, rng, meta):
    """
    Direct matching of microRNA to mRNA within specified seed region.
    
    This is the "Matching" analysis mode where user provides both sequences
    and we find binding sites between them.
    
    Args:
        micro_seq (str): microRNA sequence
        mrna_seq (str): Target mRNA sequence
        rng (tuple): Seed region (start, end) as 1-based positions
        meta (dict): Metadata containing source information for each sequence
                    Structure: {
                        "micro": {"source": "dbid|file|sequence", "data": {...}},
                        "mrna": {"source": "dbid|file|sequence", "data": {...}},
                        "range": rng
                    }
    
    Returns:
        str: Formatted results including alignment visualizations
             or message if no binding sites found
    """
    
    output = ''
    
    # Retrieve microRNA sequence based on source
    mi_rna_source = meta["micro"]["source"]

    if mi_rna_source == "dbid":        
        mi_rna_db_id = meta["micro"]["data"]["dbid"]
        mi_RNA = get_miRNA(mi_rna_db_id, filepath="data/miRNA.dat")
    elif mi_rna_source == "file":
        micro_meta = meta["micro"].get("data", {})
        micro_filepath = micro_meta.get("file") or micro_meta.get("filepath")
        if not micro_filepath:
            raise ValueError("microRNA filepath missing")
        seq_str, info = read_sequence_from_file(micro_filepath)
        mi_RNA = SeqRecord(Seq(seq_str.replace('T','U')), id=info.get('id','micro'), description=info.get('description',''))
        output += f"microRNA from file: {micro_filepath}\n"
    elif mi_rna_source == "sequence":
        mi_RNA = SeqRecord(Seq(micro_seq))
    else:
        raise ValueError(f"Unknown microRNA source: {mi_rna_source}")

    # Retrieve mRNA sequence based on source
    mrna_source = meta["mrna"]["source"]

    if mrna_source == "dbid":        
        mrna_db_id = meta["mrna"]["data"]["dbid"]
        mRNA = get_3utr_from_id(mrna_db_id)     
    elif mrna_source == "file":
        mrna_meta = meta["mrna"].get("data", {})
        mrna_filepath = mrna_meta.get("file") or mrna_meta.get("filepath")
        if not mrna_filepath:
            raise ValueError("mRNA filepath missing")
        
        # Check if file is GenBank format (.gb, .gbk extension)
        file_ext = mrna_filepath.lower().split('.')[-1]
        if file_ext in ['gb', 'gbk']:
            # GenBank file: extract 3'UTR
            mRNA = get_3utr_record_from_file(mrna_filepath)
            output += f"mRNA 3'UTR from GenBank file: {mrna_filepath}\n"
        else:
            # FASTA file: use sequence as-is
            seq_str, info = read_sequence_from_file(mrna_filepath)
            mRNA = SeqRecord(Seq(seq_str.replace('T','U')), id=info.get('id','mrna'), description=info.get('description',''))
            output += f"mRNA from FASTA file: {mrna_filepath}\n"
    elif mrna_source == "sequence":
        mRNA = SeqRecord(Seq(mrna_seq), name="mRNA_inline", description="user inline mRNA")
    else:
        raise ValueError(f"Unknown mRNA source: {mrna_source}")

    # Find binding sites
    list_mrna_binding_site = find_mrna_binding_sites(mi_RNA, mRNA, rng[0], rng[1])

    # Generate output
    if not list_mrna_binding_site:
        # No binding sites found - provide sequence information
        info_output = "No binding sites found with these parameters\n\n"
        info_output += "=" * 50 + "\n"
        info_output += "Sequence Information:\n"
        info_output += "=" * 50 + "\n\n"
        
        info_output += "microRNA:\n"
        info_output += f"  ID: {mi_RNA.id}\n"
        info_output += f"  Length: {len(mi_RNA.seq)} nucleotides\n"
        info_output += f"  Description: {mi_RNA.description}\n"
        if hasattr(mi_RNA, 'name') and mi_RNA.name:
            info_output += f"  Name: {mi_RNA.name}\n"
        info_output += "\n"
        
        info_output += "mRNA:\n"
        info_output += f"  ID: {mRNA.id}\n"
        info_output += f"  Length: {len(mRNA.seq)} nucleotides\n"
        info_output += f"  Description: {mRNA.description}\n"
        if hasattr(mRNA, 'name') and mRNA.name:
            info_output += f"  Name: {mRNA.name}\n"
        info_output += "\n"
        
        info_output += f"Seed region searched: positions {rng[0]}-{rng[1]}\n"
        info_output += "=" * 50 + "\n"
        
        return output + info_output

    # Binding sites found - generate alignments
    output += f"\n{'='*50}\n"
    output += f"Number of binding sites found: {len(list_mrna_binding_site)}\n"
    output += f"{'='*50}\n\n"

    for binding_pos in list_mrna_binding_site:
        output += plot_alignment(mi_RNA, mRNA, rng[0], rng[1], binding_pos, window=25)

    return output


# ================================================================================
# DATABASE SCANNING HELPER FUNCTIONS
# ================================================================================

def get_complement(base):
    """
    Return RNA complement for a single nucleotide (Watson-Crick only).
    
    Args:
        base (str): Single nucleotide character
    
    Returns:
        str: Complementary nucleotide (A→U, U→A, G→C, C→G) or 'N' for unknown
    """
    comp = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G'}
    return comp.get(base.upper(), 'N')


def is_watson_crick(mirna_nt, mrna_nt):
    """
    Check for canonical Watson-Crick base pair (A-U or C-G).
    
    Essential for strong thermodynamic stability in RNA duplexes.
    
    Args:
        mirna_nt (str): microRNA nucleotide
        mrna_nt (str): mRNA nucleotide
    
    Returns:
        bool: True if forms Watson-Crick pair
    """
    mirna_nt, mrna_nt = mirna_nt.upper(), mrna_nt.upper()
    return get_complement(mirna_nt) == mrna_nt


def is_wobble(mirna_nt, mrna_nt):
    """
    Check for G-U wobble base pair.
    
    Wobble pairs have thermodynamic stability comparable to Watson-Crick
    but with distinct structural geometry.
    
    Args:
        mirna_nt (str): microRNA nucleotide
        mrna_nt (str): mRNA nucleotide
    
    Returns:
        bool: True if forms wobble pair
    """
    mirna_nt, mrna_nt = mirna_nt.upper(), mrna_nt.upper()
    return (mirna_nt == 'G' and mrna_nt == 'U') or (mirna_nt == 'U' and mrna_nt == 'G')


def compress_positions_to_ranges(positions):
    """
    Convert list of integer positions to compact range string representation.
    
    Example: [1, 2, 3, 5, 6, 9] → "1-3, 5-6, 9"
    
    Args:
        positions (list): List of 1-based position integers
    
    Returns:
        str: Comma-separated range representation
    """
    if not positions:
        return ""
    
    # Remove duplicates and sort
    positions = sorted(list(set(positions)))
    ranges = []
    start = positions[0]
    end = positions[0]
    
    for pos in positions[1:]:
        if pos == end + 1:
            end = pos
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = pos
            end = pos
    
    # Add final range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")
        
    return ", ".join(ranges)


# ================================================================================
# DYNAMITE MODE: High-Throughput Database Scanning
# ================================================================================

def match_dyn_miRNA_on_mRNA(mrna_seq, seed_range_indices=(2, 7), 
                            path_mirna_db="data/miRNA.dat", progress_callback=None):
    """
    Scan entire microRNA database against target mRNA sequence.
    
    Implements seed-and-extend algorithm:
    1. For each microRNA in database
    2. Extract seed region and find reverse complement matches in mRNA
    3. For each match, calculate full alignment score
    4. Rank results by score
    
    Args:
        mrna_seq (str or SeqRecord): Target mRNA sequence
        seed_range_indices (tuple): Seed region (start, end) as 1-based positions
        path_mirna_db (str): Path to miRNA database file
        progress_callback (callable): Function to report progress (current, total)
    
    Returns:
        list: List of result dictionaries, sorted by binding strength.
              Each dict contains: accession_id, mir_seq, len_mir, seed_range_str,
                                 mrna_match_pos, score_outside_seed, bound_total,
                                 bind_percent, others_matches
    """
    
    # Get correct path for PyInstaller bundles and source execution
    path_mirna_db = get_resource_path(path_mirna_db)
    
    # Normalize input sequence
    if isinstance(mrna_seq, SeqRecord):
        mrna_seq = str(mrna_seq.seq).upper().replace("T", "U")
    else:
        mrna_seq = str(mrna_seq).upper().replace("T", "U")
    
    seed_start, seed_end = seed_range_indices
    seed_length = seed_end - seed_start + 1

    miRNAs = []
    
    # Load microRNAs from database
    try:
        for record in SeqIO.parse(path_mirna_db, "embl"):
            seq = str(record.seq).replace("T", "U")
            for feature in record.features:
                if feature.type == "miRNA":
                    start = int(feature.location.start)
                    end = int(feature.location.end)
                    mature_seq = seq[start:end]
                    accession_id = feature.qualifiers.get("accession", ["NA"])[0]
                    miRNAs.append((accession_id, mature_seq))
                    
    except FileNotFoundError:
        return []
    except Exception:
        return []

    total_miRNAs = len(miRNAs)
    results = []

    # Test each microRNA against target mRNA
    for idx, (accession_id, mir_seq) in enumerate(miRNAs, start=1):
        if progress_callback:
            try:
                progress_callback(idx, total_miRNAs)
            except Exception:
                pass

        mir_seq = mir_seq.upper()
        mirna_len = len(mir_seq)
        
        # Extract seed region
        seed_seq = mir_seq[seed_start-1 : seed_end]
        if len(seed_seq) != seed_length:
            continue

        # Generate reverse complement of seed
        seed_rc = "".join(get_complement(b) for b in seed_seq)[::-1]
        
        # Find all matches of seed reverse complement in mRNA
        start_pos = -1 
        while True:
            start_pos = mrna_seq.find(seed_rc, start_pos + 1)
            if start_pos == -1:
                break
            
            # Calculate alignment coordinates
            mrna_align_for_mirna_0 = start_pos + seed_length - 1 + (seed_start - 1)
            
            wc_positions_outside_seed = []
            wobble_positions_outside_seed = []
            current_score = 0.0
            
            # Score full alignment (positions outside seed region)
            for mir_idx in range(mirna_len):
                mir_pos_biological = mir_idx + 1 
                
                if seed_start <= mir_pos_biological <= seed_end:
                    continue
                
                mrna_idx = mrna_align_for_mirna_0 - mir_idx
                
                if mrna_idx < 0 or mrna_idx >= len(mrna_seq):
                    continue
                
                mirna_nt = mir_seq[mir_idx]
                mrna_nt = mrna_seq[mrna_idx]
                
                is_wc = is_watson_crick(mirna_nt, mrna_nt)
                is_wob = is_wobble(mirna_nt, mrna_nt)

                if is_wc:
                    current_score += 1.0
                    wc_positions_outside_seed.append(mir_pos_biological)
                elif is_wob:
                    current_score += 0.5
                    wobble_positions_outside_seed.append(mir_pos_biological)
            
            # Aggregate results
            total_bound_nucleotides = seed_length + len(wc_positions_outside_seed) + len(wobble_positions_outside_seed)
            bind_percent = round(100 * total_bound_nucleotides / mirna_len, 1)

            all_outside_positions = wc_positions_outside_seed + wobble_positions_outside_seed
            others_string = compress_positions_to_ranges(all_outside_positions)

            results.append({
                "accession_id": accession_id,
                "mir_seq": mir_seq,
                "len_mir": mirna_len,
                "seed_range_str": f"{seed_start}-{seed_end}",
                "mrna_match_pos": start_pos + 1, 
                "score_outside_seed": current_score, 
                "bound_total": total_bound_nucleotides,
                "bind_percent": bind_percent,
                "others_matches": others_string,
            })

    # Sort results: by score (descending), then by binding % (descending)
    if results:
        results.sort(key=lambda x: (x["score_outside_seed"], x["bind_percent"]), reverse=True)

    return results


def format_results_table(results_list, seed_range):
    """
    Format database scanning results as a human-readable table.
    
    Args:
        results_list (list): List of result dictionaries from match_dyn_miRNA_on_mRNA
        seed_range (tuple): Seed region (start, end)
    
    Returns:
        str: Formatted table with columns for all result metrics
    """
    
    if isinstance(results_list, dict) and "error" in results_list:
        return f"ERROR: {results_list['error']}"

    if not results_list:
        return "No binding sites found matching the seed criteria."

    output = []
    output.append(f"Number of microRNAs found: {len(results_list)}")
    output.append(f"Seed region: {seed_range[0]}-{seed_range[1]}")
    output.append("")
    
    # Table header
    header = f"{'Accession':<12} {'Score':<6} {'Seed':<8} {'Bound':<7} {'Bind%':<7} {'Pos':<5} {'Len':<4} {'microRNA Seq':<22} {'Other Pairs'}"
    output.append(header)
    output.append("=" * 140)

    # Table rows
    for r in results_list:
        line = (
            f"{r['accession_id']:<12} {r['score_outside_seed']:<6.1f} " 
            f"{r['seed_range_str']:<8} "
            f"{r['bound_total']:<7} {str(r['bind_percent'])+'%':<7} "
            f"{r['mrna_match_pos']:<5} {r['len_mir']:<4} "
            f"{r['mir_seq'][:22]:<22} {r['others_matches']}"
        )
        output.append(line)
        
    return "\n".join(output)


# ================================================================================
# BACKEND ENTRY POINT FOR DYNAMITE MODE
# ================================================================================

def backend_dynamite_on_mrna(mrna_seq, rng, meta, progress_callback=None):
    """
    Execute high-throughput microRNA database scan against target mRNA.
    
    This is the "Dynamite" analysis mode where we scan the entire microRNA
    database to find all potential binding microRNAs.
    
    Args:
        mrna_seq (str): Target mRNA sequence
        rng (tuple): Seed region (start, end) as 1-based positions
        meta (dict): Metadata with mRNA source information
                    Structure: {
                        "mrna": {"source": "dbid|file|sequence", "data": {...}},
                        "range": rng
                    }
        progress_callback (callable): Function to report progress (current, total)
    
    Returns:
        str: Formatted results table of matching microRNAs
    """

    # Extract mRNA source information
    if "mrna" in meta:
        mrna_source = meta["mrna"]["source"]
        mrna_meta = meta["mrna"].get("data", {})
    else:
        mrna_source = meta.get("mrna_source")
        mrna_meta = meta.get("mrna_meta", {})

    # Retrieve mRNA sequence
    if mrna_source == "dbid":
        dbid = mrna_meta.get("dbid")
        if not dbid:
            raise ValueError("No GenBank ID provided")
        mRNA_seq = str(get_3utr_from_id(dbid).seq)

    elif mrna_source == "file":
        filepath = mrna_meta.get("file") or mrna_meta.get("filepath")
        if filepath:
            # Check if file is GenBank format (.gb, .gbk extension)
            file_ext = filepath.lower().split('.')[-1]
            if file_ext in ['gb', 'gbk']:
                # GenBank file: extract 3'UTR
                mRNA_seq = str(get_3utr_record_from_file(filepath).seq)
            else:
                # FASTA file: use sequence as-is
                seq_str, _info = read_sequence_from_file(filepath)
                mRNA_seq = seq_str
        else:
            if not mrna_seq:
                raise ValueError("No mRNA sequence available")
            mRNA_seq = str(mrna_seq)

    elif mrna_source == "sequence":
        mRNA_seq = str(mrna_seq)
    else:
        raise ValueError(f"Unknown mRNA source: {mrna_source}")

    # Scan database
    raw_results = match_dyn_miRNA_on_mRNA(mRNA_seq, rng, progress_callback=progress_callback)

    # Format results
    if not raw_results:
        return "No microRNA binding sites found with the specified seed region"

    return format_results_table(raw_results, rng)
