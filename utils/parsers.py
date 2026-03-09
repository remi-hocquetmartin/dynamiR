"""
================================================================================
INPUT PARSING UTILITIES - SEED REGION SPECIFICATION
================================================================================

PURPOSE:
    Parses and validates user input for seed region definitions.
    Seed region specifies which nucleotide positions to prioritize in binding
    analysis (typically positions 2-7 or 2-8 of the microRNA 5' end).

FORMAT SUPPORTED:
    "2-7": Start position to end position (1-indexed, inclusive range)
================================================================================
"""


def parse_range_text(txt):
    """
    Parse a seed region range text specification.
    
    Converts string like "2-7" into tuple of start and end positions.
    Validates that start < end to ensure meaningful range.
    
    Args:
        txt (str): Range specification in format "start-end" (1-indexed)
                   Example: "2-7" specifies positions 2 through 7 inclusive
    
    Returns:
        tuple: (start, end) as integers, both inclusive
               Example: "2-7" → (2, 7)
    
    Raises:
        ValueError: If input is empty, format invalid, or start >= end
    
    Notes:
        - Positions are 1-indexed (matching biological convention)
        - Range is inclusive on both ends
        - Used internally as 0-indexed in sequence operations (converted at call site)
    """
    # Reject empty input
    if not txt:
        raise ValueError("Empty seed")
    
    try:
        a_str, b_str = txt.split("-")
        a, b = int(a_str), int(b_str)
    except Exception:
        raise ValueError("Invalid seed format - use 'start-end' (e.g., 2-7)")

    # Validate logical range (start < end)
    if a >= b:
        raise ValueError("Seed start must be smaller than seed end")

    return (a, b)
