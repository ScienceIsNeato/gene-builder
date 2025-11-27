# Instructions for AI Agents

**For LLMs helping users modify this codebase**

Share this file with ChatGPT/Claude along with `config.py` when requesting changes.

## Project Context

### What This Tool Does
Extracts gene sequences from Ensembl and generates GenBank files. Keeps exon numbering consistent across splice variants.

### Who Uses It
- Neuroscience researchers (zebrafish)
- Technical but not developers (use tools like Fiji, APE)
- Can edit config files, less comfortable with CLI
- Works with LLMs via web interfaces when customizing

### Design Philosophy
1. Single config file - all settings in `config.py`
2. Audit reports - document decisions with Ensembl links
3. Transparency over perfection
4. Iteration-friendly - fixes improve tool for everyone
5. For biologists, not developers

## 🏗️ Architecture Overview

### File Structure
```
config.py              ← ALL user-editable settings (edit this!)
gui.py                 ← Tkinter GUI (simple, self-contained)
scripts/
  └── gene_to_genbank.py  ← Core logic (complex, modify carefully)
training/              ← Test cases for validation
output/                ← Generated files
```

### Key Insight: Separation of Concerns
- **config.py**: Settings that users change frequently
- **gui.py**: Interface logic (rarely modified)
- **gene_to_genbank.py**: Algorithm (only change when improving accuracy)

### Data Flow
```
User → GUI → config.py settings → gene_to_genbank.py → Ensembl API → GenBank files
```

## 📋 When Users Ask For Changes

### Easy Changes (Modify config.py)
User requests like:
- "Change exon colors"
- "Use different species by default"
- "Change output directory"
- "Adjust filtering parameters"

**Your response**: Show exact changes to `config.py`

**Example**:
```python
# In config.py, change:
EXON_COLORS = [
    "cyan",      # Change this to user's preferred colors
    "#ff00dc",
    # ...
]
```

### Medium Changes (Modify filtering logic)
User requests like:
- "Filter out transcripts shorter than X"
- "Keep all transcripts over Y length"
- "Prioritize transcripts with more exons"

**Your response**: Modify filtering in `gene_to_genbank.py`, function: `filter_duplicate_transcripts()`

**Important**: Explain biological implications!

### Hard Changes (Core algorithm)
User requests like:
- "Fix UTR boundary detection"
- "Handle reverse strand genes differently"
- "Improve exon numbering"

**Your response**: 
1. Acknowledge complexity
2. Ask for specific test cases
3. Suggest creating training examples first
4. Reference `DOCS/VALIDATION.md`

## 🔬 Biological Context You Should Know

### Critical Biological Facts
1. **Genes have transcripts** (splice variants)
2. **Transcripts have exons** (coding regions) separated by introns
3. **CDS = Coding Sequence** (from ATG start to stop codon)
4. **UTRs = Untranslated Regions** (5' before ATG, 3' after stop)
5. **Canonical transcript** = the "main" one (Ensembl's designation)

### Common Pitfalls for LLMs
❌ **Wrong**: "Exons are numbered sequentially in each transcript"
✅ **Right**: "Exons are numbered by genomic position across ALL transcripts of a gene"

❌ **Wrong**: "5' UTR is exon 1"
✅ **Right**: "5' UTR comes before the first coding exon"

❌ **Wrong**: "All ATG codons are start codons"
✅ **Right**: "The CDS defines THE start codon; earlier ATGs are in 5' UTR"

### Alternative Splicing (THE KEY FEATURE)
When a gene has multiple transcripts:
- Some exons appear in all transcripts (constitutive)
- Some appear only in some transcripts (alternative)
- **Our tool numbers exons consistently** so users can compare

Example:
- Transcript A: exon1, exon2, exon4
- Transcript B: exon1, exon3, exon4

User immediately sees: B has exon3 instead of exon2!

## 🎨 Working with Users

### Communication Style
- **Use biological terms correctly** (exon, UTR, CDS, transcript)
- **Explain WHY** not just WHAT (biological reasoning)
- **Give examples** with actual gene names
- **Test incrementally** (one change at a time)

### When User Says "It's Wrong"
1. **Ask for specifics**: "What gene? What's wrong about it?"
2. **Request evidence**: "Can you share the Ensembl screenshot?"
3. **Check understanding**: "Let me verify my understanding of what should happen..."
4. **Propose hypothesis**: "I think the issue might be X because Y"
5. **Suggest test**: "Can we try this change and see if it fixes it?"

### Typical User Workflow
1. User runs tool on a gene
2. Opens output in APE
3. Notices something wrong (e.g., exon boundary off by 10bp)
4. Asks LLM for help
5. **You need to help debug** without seeing the output!

**Your approach**:
- Ask them to describe what they see
- Ask for the log output from the GUI
- Request specific coordinates (positions)
- Compare to Ensembl browser

## 🚨 Common Issues & Solutions

### Issue: "UTR boundaries are wrong"

**Diagnosis questions**:
- Where does Ensembl say CDS starts/ends?
- Where does our file say exons start/end?
- Is there a mismatch?

**Common cause**: CDS detection using wrong ATG

**Solution area**: `find_cds_in_transcript()` function

### Issue: "Transcripts being filtered incorrectly"

**Diagnosis**:
- How many transcripts in Ensembl?
- How many did we generate?
- What does the filtering log say?

**Common cause**: Filtering logic too aggressive OR too conservative

**Solution area**: `filter_duplicate_transcripts()` function

### Issue: "Exon numbers don't make sense"

**Diagnosis**:
- Are numbers consistent across transcripts?
- Are they based on genomic position?

**Common cause**: Exon map building issue

**Solution area**: `build_gene_exon_map()` function

### Issue: "Colors aren't showing in APE"

**Usually not a code problem!**
- Check if APE is installed
- Verify file opens correctly
- Colors are in the file (check FEATURES section)

## 💡 Best Practices for AI Assistance

### DO:
✅ Read the full file before suggesting changes
✅ Show exact code with context (not just snippets)
✅ Explain biological reasoning
✅ Test changes incrementally
✅ Maintain code style consistency
✅ Update documentation when changing behavior
✅ Ask clarifying questions

### DON'T:
❌ Guess at biological facts (ask for verification!)
❌ Make breaking changes without explanation
❌ Modify multiple files when config.py would suffice
❌ Remove logging/comments
❌ Add complex dependencies
❌ Assume you understand the biology (verify!)

### When Unsure:
1. State your uncertainty
2. Ask questions
3. Suggest looking at Ensembl documentation
4. Propose creating a test case first

## 📚 Code Patterns to Follow

### Adding a New Configuration Option

```python
# 1. Add to config.py with clear comment
NEW_SETTING = "default_value"  # What this controls

# 2. Use in code
import config
if config.NEW_SETTING:
    # do something

# 3. Document in USER_GUIDE.md
```

### Adding Logging

```python
# Always explain decisions
print(f"  ✅ KEEPING: {transcript_name}")
print(f"     Reason: [why]")
print(f"     Details: [specifics]")

print(f"  🚫 FILTERED: {transcript_name}")
print(f"     Reason: [why]")
```

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    # Helpful message for user
    print(f"  Warning: Could not process X: {e}")
    # Continue if possible, or explain why stopping
```

## 🧪 Testing Strategy

### Current State
- **Manual testing only** (no automated tests yet)
- Training set approach planned (see `DOCS/VALIDATION.md`)
- User validation is primary quality check

### When Suggesting Changes

1. **Explain test approach**: "Here's how to verify this works..."
2. **Provide test case**: "Try with gene lrfn1 and check..."
3. **Describe expected output**: "You should see..."
4. **Suggest comparison**: "Compare to the version in `training/`..."

### Red Flags That Need Testing
- Changes to filtering logic
- Changes to coordinate calculations
- Changes to CDS detection
- Changes to exon numbering

## 🎓 Lessons Learned

### From Development History

1. **Don't bypass quality checks** - Always explain why filtering happens
2. **Fail fast, fix immediately** - Don't continue with bad data
3. **Biological expertise > programmatic guessing** - When uncertain, ask
4. **Make decisions transparent** - Log everything
5. **One change at a time** - Especially for non-developers
6. **Config over code** - If it's a setting, put it in config.py

### From User Feedback

1. **UTR detection is hard** - Multiple ATGs, stop codons tricky
2. **Filtering is subjective** - Biological judgment needed
3. **Visualization matters** - Colors help users understand
4. **Context is king** - Users need to know WHY something was filtered
5. **Defaults matter** - Canonical-only is safer for beginners

## 🔧 Troubleshooting LLM Iteration

### User Says: "Your change didn't work"

**Checklist**:
- [ ] Did they save the file?
- [ ] Did they restart the GUI?
- [ ] Did they check the right file?
- [ ] Was there a syntax error? (check indentation!)
- [ ] Did they test with the same gene?

### User Says: "I got an error"

**Response template**:
```
I see the error. This happened because [reason].

To fix it:
1. Open config.py
2. Find line X
3. Change [this] to [that]
4. Save and restart GUI

This error means [biological/technical explanation].
```

### User Says: "How do I...?"

**Before answering**:
- Is it in `USER_GUIDE.md`? → Point them there
- Is it a config change? → Show config.py modification
- Is it complex? → Break into steps
- Is it about biology? → Ask for clarification

## 🌟 Success Metrics

### A Good LLM Interaction Results In:
- ✅ User can make changes confidently
- ✅ Changes are in config.py (not scattered)
- ✅ Biological reasoning is clear
- ✅ Changes are tested incrementally
- ✅ Documentation is updated if needed
- ✅ User understands WHY not just HOW

### A Bad LLM Interaction Results In:
- ❌ User breaks the tool
- ❌ Changes require fixing other files
- ❌ Biological errors introduced
- ❌ User doesn't understand what changed
- ❌ No way to test the changes

## 📖 Required Reading for Complex Changes

Before modifying core algorithms, read:
1. `KNOWN_ISSUES.md` - Current limitations
2. `TRAINING_SET_PLAN.md` - Testing approach
3. `DEVELOPERS.md` - Technical architecture
4. `SESSION_SUMMARY.md` - Development history

## 🤝 Collaboration Model

### You (LLM) Should:
- Understand biological context
- Provide clear, tested code
- Explain reasoning
- Ask questions when uncertain
- Maintain code quality
- Document changes

### User Should:
- Provide biological validation
- Test changes
- Report results clearly
- Share error messages
- Describe expected vs actual behavior

### Together You Can:
- Improve accuracy incrementally
- Add features safely
- Fix bugs systematically
- Build understanding
- Create better documentation

## 🎯 Final Reminder

**This tool is for biologists, not developers.**

Every interaction should:
1. **Respect their expertise** (biology) while providing yours (code)
2. **Reduce complexity** (one file > many files)
3. **Build confidence** (explain, don't just do)
4. **Enable iteration** (small steps, clear results)
5. **Maintain quality** (working tool > broken tool)

**When in doubt**: Ask questions, suggest small changes, test incrementally.

---

**For users**: Share this file with your LLM along with the file you want to modify. It provides important context that will make the interaction more successful!

**For LLMs**: This document captures lessons learned from extensive development. Please respect these patterns and principles when helping users.
