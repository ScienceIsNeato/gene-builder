# lrfn1

**Why this gene**: Simple case with 2 transcripts. One appears redundant (lrfn1-201 seems to be a subset of lrfn1-202).

**Files**:
- `lrfn1_lrfn1-202_reference.gbk`: The canonical transcript which we likely want to keep.

**Notes**:
- We need to determine if 201 should be filtered automatically or if there's a biological reason to keep it.
- Current tool behavior with `--canonical-only` correctly keeps only 202.
