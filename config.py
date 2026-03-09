"""
DynamiR Configuration and Constants

This module centralizes all configuration values used throughout the application.
Update values here rather than hardcoding them in individual modules.
"""

# ============================================================================
# APPLICATION METADATA
# ============================================================================
APP_NAME = "DynamiR"
APP_VERSION = "1.0.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION} - microRNA Binding Site Analysis Tool"

# ============================================================================
# UI STYLING
# ============================================================================
# Color Scheme
COLORS = {
    "bg": "#fafafa",           # Main background
    "fg": "#333333",           # Main text
    "accent": "#2196F3",       # Accent color (blue)
    "success": "#4CAF50",      # Success color (green)
    "error": "#F44336",        # Error color (red)
    "warning": "#FF9800",      # Warning color (orange)
}

# Fonts
FONTS = {
    "default": ("Arial", 10),
    "mono": ("Monaco", 9),
    "title": ("Arial", 14, "bold"),
    "button": ("Arial", 10),
}

# Window Dimensions
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
INPUT_PANEL_WIDTH = 250

# ============================================================================
# SEQUENCE ANALYSIS
# ============================================================================
# Seed Region Defaults
DEFAULT_SEED_START = 2
DEFAULT_SEED_END = 7

# Base Pairing
WATSON_CRICK_PAIRS = {
    ("A", "U"), ("U", "A"),
    ("C", "G"), ("G", "C"),
}

WOBBLE_PAIRS = {
    ("G", "U"), ("U", "G"),
}

# Scoring
WATSON_CRICK_SCORE = 1.0      # Full score for perfect pairing
WOBBLE_SCORE = 0.5            # Half score for wobble pairing

# ============================================================================
# NCBI ENTREZ
# ============================================================================
NCBI_EMAIL = "your-email@example.com"  # Set this for NCBI queries
NCBI_TIMEOUT = 10                       # seconds
NCBI_RETRIES = 3                        # number of retries

# ============================================================================
# FILE I/O
# ============================================================================
SUPPORTED_FASTA_EXTENSIONS = [".fa", ".fasta"]
SUPPORTED_GENBANK_EXTENSIONS = [".gb", ".gbk"]
SUPPORTED_SEQUENCE_EXTENSIONS = SUPPORTED_FASTA_EXTENSIONS + SUPPORTED_GENBANK_EXTENSIONS

# ============================================================================
# THREADING
# ============================================================================
ANALYSIS_THREAD_TIMEOUT = 300  # seconds (5 minutes max)

# ============================================================================
# RESULT DISPLAY
# ============================================================================
RESULT_TEXT_WIDTH = 50
RESULT_TEXT_HEIGHT = 30
