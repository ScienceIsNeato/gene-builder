# Troubleshooting

## When Output is Wrong

If you get incorrect results, you can fix it. Here's how:

### The Process (about 5 minutes)

1. **Document the issue**:
   - Gene name: `sox2`
   - Expected: Exon 3 at position 500-800
   - Got: Exon 3 at position 510-790

2. **Gather info**:
   - Copy audit report from `output/GENE_audit_report.txt`
   - Note the specific error

3. **Ask for help**:
   - Open ChatGPT or Claude
   - Share `DOCS/AGENTS.md` (gives context)
   - Share `config.py` (current settings)
   - Describe what's wrong

4. **Apply the fix**:
   - LLM suggests changes to `config.py` or notes a bug
   - Make the changes
   - Save and test again

5. **Verify**: Check audit report, confirm fix works

Each fix makes the tool work better for future genes.

## Common Issues

**Gene not found**: Check spelling. Verify it exists in Ensembl.

**No output generated**: Check the log. May have been filtered.

**Wrong exon boundaries**: Use the process above to fix.

**Setup fails**: Make sure Python 3.8+ is installed.

**GUI won't start**: Needs Python from python.org (not Homebrew). Or just use `./extract_gene.sh`.

## Getting Help

Open a GitHub issue with:
- Gene name
- What's wrong
- Audit report

Someone can help, or point you to a fix.

## Philosophy

Bad output isn't failure - it's a chance to improve the tool for everyone.

The time you spend fixing one gene makes future genes work better.
