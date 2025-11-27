# User Guide

## Usage

### 1. Start the Application
Double-click the `run_gui.command` file in the main folder.

### 2. Extract a Gene
1.  Enter the gene symbol (e.g., `lrfn1`).
2.  (Optional) Change the species if not using Zebrafish.
3.  Click **Extract Gene**.

### 3. View Results
The tool will generate files in the `output/` folder.
*   **`.gbk` file**: Open this in ApE or SnapGene.
*   **`_audit.txt`**: Read this to verify the data source and decisions.

## Customizing

All settings are in `config.py`. Open it in any text editor.

Common changes:
- `EXON_COLORS` - Change visualization colors
- `DEFAULT_SPECIES` - Use different organism
- `DEFAULT_CANONICAL_ONLY` - Get all transcripts or just canonical

## Troubleshooting

**Gene not found**: Verify it exists in Ensembl. Check spelling.

**Setup fails**: Make sure Python 3.8+ is installed.

**GUI won't start**: Ensure you ran `./setup.sh` once. If it still fails, try running `./extract_gene.sh lrfn1` from the terminal to see error messages.

## Understanding Output

### GenBank Files
Open in APE or SnapGene. Exons are color-coded. Numbers stay consistent across splice variants.

### Audit Reports
Read these to understand what the tool did. Click Ensembl links to verify.
