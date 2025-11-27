"""
Configuration File for Gene Builder
====================================

This file contains all the settings you can customize.
When working with an LLM to improve the tool, share this file
in your conversation for easy modifications.

"""

# ============================================================================
# BASIC SETTINGS - Change these for your needs
# ============================================================================

# Default species (scientific name)
# Common options:
#   - "danio_rerio" (zebrafish)
#   - "homo_sapiens" (human)
#   - "mus_musculus" (mouse)
#   - "rattus_norvegicus" (rat)
DEFAULT_SPECIES = "danio_rerio"

# Should we only extract the canonical transcript by default?
# True = only canonical (recommended for beginners)
# False = all transcripts
DEFAULT_CANONICAL_ONLY = True

# Output directory for generated files
# Each run generates: .gbk file + audit report
OUTPUT_DIR = "output"

# Generate audit reports (recommended: True for research use)
GENERATE_AUDIT_REPORTS = True

# ============================================================================
# EXON COLORS - Customize the colors used in APE
# ============================================================================

# Colors cycle through this list for each exon
# Format: HTML color codes or color names
EXON_COLORS = [
    "cyan",       # Exon 1
    "#ff00dc",    # Exon 2 (magenta)
    "#ff9fdf",    # Exon 3 (light pink)
    "#d0b2ff",    # Exon 4 (light purple)
    "#84ff84",    # Exon 5 (light green)
    "#ffd700",    # Exon 6 (gold)
    "#ff6b6b",    # Exon 7 (coral)
    "#4ecdc4",    # Exon 8 (turquoise)
]

# Color for UTR regions
UTR_COLOR = "#ffcc99"  # Orange

# ============================================================================
# FILTERING SETTINGS - Control which transcripts are kept
# ============================================================================

# Minimum number of exons to keep a transcript
# (filters out very short/incomplete transcripts)
MIN_EXONS = 1

# Maximum genomic span difference for duplicate detection (in base pairs)
# If two transcripts overlap by this much, check if one is a subset
GENOMIC_OVERLAP_THRESHOLD = 1000

# ============================================================================
# API SETTINGS - Advanced users only
# ============================================================================

# Ensembl REST API base URL
ENSEMBL_API_URL = "https://rest.ensembl.org"

# Maximum number of retries for API calls
MAX_API_RETRIES = 3

# Delay between API calls (seconds)
API_DELAY = 0.5

# ============================================================================
# GUI SETTINGS
# ============================================================================

# Window title
WINDOW_TITLE = "Gene Builder - Extract Gene Sequences"

# Window size (width, height)
WINDOW_SIZE = (600, 500)

# ============================================================================
# NOTES FOR LLM ITERATION
# ============================================================================

"""
When working with an LLM to improve this tool:

1. SHARE THIS FILE in your conversation
2. Describe what you want to change (e.g., "I want different colors")
3. The LLM can suggest modifications to this file
4. Copy the changes back here
5. Run the GUI again to test

Common modifications:
- Change EXON_COLORS to customize visualization
- Change DEFAULT_CANONICAL_ONLY if you want all transcripts
- Change DEFAULT_SPECIES for different organisms
- Adjust MIN_EXONS to filter more/less aggressively

For more complex changes, you may need to modify:
- scripts/gene_to_genbank.py (the main algorithm)
- gui.py (the interface)
"""

