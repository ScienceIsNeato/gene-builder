# Developer Documentation

Technical reference for the Gene Builder codebase.

## Architecture

```
GUI → config.py → gene_to_genbank.py → Ensembl API → GenBank files
```

### Key Components

*   **`src/gui.py`**: Tkinter interface. Handles user input and threading.
*   **`src/gene_to_genbank.py`**: Core logic.
    *   Fetches data from Ensembl REST API.
    *   Normalizes exon numbering across transcripts.
    *   Filters redundant transcripts.
    *   Generates `.gbk` output.
*   **`config.py`**: Single source of truth for user settings (colors, species, defaults).
*   **`src/audit_report.py`**: Generates the text report for validation.

## Development Setup

1.  **Clone & Setup**:
    ```bash
    git clone <repo_url>
    cd gene-builder
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run GUI**:
    ```bash
    python src/gui.py
    ```

3.  **Run CLI (for testing logic)**:
    ```bash
    python src/gene_to_genbank.py lrfn1 --canonical-only
    ```

## Core Logic Explained

### Exon Numbering (`build_gene_exon_map`)
*   **Problem**: Alternative splicing makes sequential numbering (1, 2, 3...) confusing when comparing transcripts.
*   **Solution**: We collect *all* unique exons for a gene, sort them genomically, and assign a master ID (1..N).
*   **Result**: If Transcript A skips an exon, it might have exons 1, 3, 4. This allows immediate visual comparison.

### Transcript Filtering (`filter_duplicate_transcripts`)
*   **Goal**: Reduce noise by hiding biologically redundant info.
*   **Rules**:
    1.  **Subset**: If Transcript A's exons are a perfect subset of Transcript B, filter A.
    2.  **Genomic Containment**: If A is physically inside B's start/end coordinates and has fewer exons, filter A.
*   **Canonical Override**: If the user selects `--canonical-only`, we strictly filter everything except the Ensembl-designated canonical transcript.

### UTR Detection
We use the CDS (Coding Sequence) start and end points provided by Ensembl to delineate:
*   **5' UTR**: Start of transcript → Start of CDS.
*   **Coding Exons**: Overlapping with CDS.
*   **3' UTR**: End of CDS → End of transcript.

## API Integration

*   **Source**: Ensembl REST API (rest.ensembl.org).
*   **Rate Limiting**: Built-in backoff logic handles HTTP 429 responses automatically.
*   **No Auth**: Public API, no keys required.

## Testing & Validation

See `DOCS/VALIDATION.md` for the strategy on using "Training Sets" (curated gene examples) to validate logic changes.

## Contributing

1.  Create a branch.
2.  Make changes (prefer editing `config.py` for settings).
3.  Test with a known gene (e.g., `lrfn1`).
4.  Verify the Audit Report (`output/*_audit.txt`) matches expectations.
