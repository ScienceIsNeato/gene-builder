# Gene Builder

Extracts zebrafish gene sequences from Ensembl and generates GenBank files for APE.

## Features

- Exon numbering stays consistent across splice variants
- Separates 5' UTR, coding exons, and 3' UTR
- Creates audit reports with Ensembl links for verification
- All settings in one file (`config.py`)

## Setup

```bash
./setup.sh
```

## Usage

```bash
./extract_gene.sh GENE_SYMBOL
```

Files go to `output/`. Each gene gets a `.gbk` file and `_audit.txt` report.

## Customizing

Edit `config.py`:
- Exon colors
- Default species
- Filtering behavior

For help modifying: Copy `config.py` to ChatGPT/Claude, ask for changes.

## Output

**GenBank files**: Color-coded exons, labeled UTRs, APE-compatible

**Audit reports**: Lists all decisions with Ensembl verification links

## When Things Go Wrong

See `TROUBLESHOOTING.md`. The short version: Document the issue, share with an LLM along with `DOCS/AGENTS.md` and `config.py`, apply the fix. Takes about 5 minutes.

## Documentation

- `START_HERE.md` - Quick overview
- `TROUBLESHOOTING.md` - Fixing issues
- `DOCS/USER_GUIDE.md` - Detailed usage
- `DOCS/AGENTS.md` - For LLM help

## Requirements

- Mac (Intel or Apple Silicon)
- Python 3.8+
- Internet connection

## Status

Works well for simple genes. For complex cases, check the audit report and validate.

---

Questions? See `DOCS/` or open an issue.
