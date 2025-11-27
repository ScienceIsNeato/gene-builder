# Gene Builder

Extracts zebrafish genes from Ensembl and creates APE files.

## Quick Start

### 1. Setup (First Time Only)
Open Terminal and run:
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Run
Double-click `extract_gene.command`

### 3. Extract
1. Enter gene symbol (e.g., "lrfn1")
2. Click **Extract Gene**
3. Open files from `output/` in APE

**Note**: If the GUI doesn't start, ensure you installed Python from python.org (not Homebrew). As a fallback, you can use the terminal: `./extract_gene.sh lrfn1`

## What You Get

Each run creates:
- `.gbk` file with color-coded exons
- `_audit.txt` with all decisions and Ensembl links

The audit file helps you verify things quickly.

## Customizing

Edit `config.py` to change colors, default species, etc.

Working with ChatGPT/Claude: Copy `config.py` to the chat, ask for changes, copy back.

## If Something's Wrong

Don't give up - you can fix it:

1. Note what's wrong (e.g., "exon 3 at wrong position")
2. Copy the audit report
3. Open ChatGPT/Claude
4. Share: `DOCS/AGENTS.md` + `config.py` + your issue
5. Apply the suggested fix

Takes about 5 minutes. Each fix makes the tool work better.

## Features

**Exon numbering**: Numbers stay consistent across splice variants, so you can compare them easily.

**Audit reports**: Documents every decision with Ensembl verification links.

## More Info

- `README.md` - Overview
- `TROUBLESHOOTING.md` - Common issues
- `DOCS/` - Detailed docs
- `training/` - How to validate

## Requirements

Mac with Python 3.8+. Internet connection to query Ensembl.

## Status

Works well for simple genes with canonical transcripts. For complex cases, check the audit report and validate against Ensembl.
