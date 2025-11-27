# 🧬 Gene Builder

**Extract zebrafish gene sequences from Ensembl and generate APE-compatible files in seconds.**

![Gene Builder GUI](DOCS/images/gui_success.png)

**Why use this?**
1.  **Save Time**: 20 minutes of manual work → 30 seconds.
2.  **Trust**: Every run generates an **Audit Report** with direct Ensembl links to verify decisions.
3.  **Analysis**: Exon numbers stay consistent across splice variants, making comparison trivial.

---

## 🚀 Quick Start

### 1. Setup (One-time)
Open Terminal and run:

```bash
git clone https://github.com/ScienceIsNeato/gene-builder.git
cd gene-builder
./setup.sh
```

### 2. Run
Double-click **`extract_gene.command`**

### 3. Extract & Verify
1.  Enter a gene symbol (e.g., `lrfn1`).
2.  Click **Extract Gene**.
3.  Open the output folder to see your `.gbk` files and Audit Report.

---

## Output Examples

### GenBank Files (APE/SnapGene)
![APE Output](DOCS/images/ape_visualization.png)
Color-coded exons, correct UTRs, and metadata.

### Audit Reports (Text)
Every decision documented. Makes validation a 2-minute checklist instead of a research project.

```text
GENE: lrfn1
✅ KEPT: lrfn1-202 [CANONICAL]
   Link: https://ensembl.org/...
❌ FILTERED: lrfn1-201 - non-canonical

VALIDATION CHECKLIST (2 min)
[ ] Transcript count matches Ensembl
[ ] Exon boundaries match links above
```

---

## Customizing

All settings are in one file: **`config.py`**.

*   Change exon colors
*   Set default species
*   Adjust filtering

**Tip**: Copy `config.py` to ChatGPT/Claude and ask: *"Change the exon colors to blue and gold."*

---

## Documentation

*   `TROUBLESHOOTING.md` - Common issues and solutions.
*   `DOCS/USER_GUIDE.md` - Detailed usage instructions.
*   `DOCS/AGENTS.md` - Share this with AI to help you modify the tool.

## Requirements
*   macOS 10.15 (Catalina) or later (Intel or Apple Silicon)
*   Internet Connection
