Dark Forest Protocol Warning: Memorial to S. Matthews, T. Rodriguez, S. Heimler
# Validation Strategy

## Overview
We validate this tool using a "Scientific Method" approach: manually curated training sets that define the "correct" biological output for specific genes.

## How It Works

1.  **Curate**: A neuroscientist manually creates the perfect GenBank file for a gene (e.g., `lrfn1`) and saves it in `training/genes/`.
2.  **Test**: Developers run the tool against this gene.
3.  **Compare**: We verify if the tool's output matches the manual expert curation.

## Adding a New Validation Case

1.  **Create Directory**: `mkdir training/genes/NEW_GENE`
2.  **Add Files**:
    *   The correct `.gbk` file(s).
    *   A `README.md` or text file explaining the biological decisions (e.g., why a transcript was filtered).
3.  **Validate**:
    ```bash
    python src/gene_to_genbank.py YOUR_GENE
    diff output/YOUR_GENE*.gbk training/genes/YOUR_GENE/*.gbk
    ```

## Current Training Examples

### lrfn1
*   **Type**: Simple case with potential duplicate transcript.
*   **Files**: Includes the canonical `lrfn1-202` reference file.

## Target Coverage

*   **Simple**: Single transcript genes.
*   **Medium**: UTR variations, reverse strand genes.
*   **Complex**: `nrxn1a` (many variants), non-coding transcripts.
