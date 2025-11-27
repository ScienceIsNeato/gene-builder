# Known Issues

## Current Limitations

### UTR/Exon Boundary Detection
Some edge cases in final exon boundaries. The CDS end position may not align perfectly with exon ends.

**Example**: Final coding exon may continue beyond stop codon.

**Workaround**: Check audit report, verify against Ensembl links.

### Transcript Filtering
May keep some redundant transcripts. Filtering is conservative to avoid losing data.

**Workaround**: Use `--canonical-only` flag.

### Not Fully Validated
Tested on simple genes. Complex cases need validation.

**Recommendation**: Review audit report for each gene. Report issues on GitHub.

## Reporting Issues

If you find incorrect output:

1. Note gene name and what's wrong
2. Save the audit report
3. Open GitHub issue with details
4. Or: Fix it yourself via LLM (see `TROUBLESHOOTING.md`)

## Development Status

See `DOCS/DEVELOPMENT.md` for detailed status and roadmap.

Core extraction works. Refinement ongoing through user validation.

