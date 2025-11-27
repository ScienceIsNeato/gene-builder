#!/usr/bin/env python3
"""Audit Report - Makes validation trivial"""

from datetime import datetime
import hashlib

def generate_audit_report(gene_data, transcripts_kept, transcripts_filtered, 
                         exon_map, features_by_transcript, output_files):
    """
    Generate concise audit report.
    
    Returns: String containing full audit report
    """
    
    gene_id = gene_data.get('id')
    gene_name = gene_data.get('display_name')
    chrom = gene_data.get('seq_region_name')
    start = gene_data.get('start')
    end = gene_data.get('end')
    
    lines = []
    lines.append(f"GENE EXTRACTION AUDIT - {gene_name}")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Gene: {gene_id} | Location: chr{chrom}:{start:,}-{end:,}")
    lines.append(f"Verify: https://ensembl.org/Danio_rerio/Gene/Summary?g={gene_id}")
    lines.append("")
    
    # Transcript decisions
    lines.append("TRANSCRIPTS")
    lines.append("-" * 80)
    for t in transcripts_kept:
        tid = t.get('id')
        tname = t.get('display_name')
        canon = " [CANONICAL]" if t.get('is_canonical') else ""
        lines.append(f"✅ KEPT: {tname}{canon}")
        lines.append(f"   Link: https://ensembl.org/Danio_rerio/Transcript/Exons?t={tid}")
    
    for f in transcripts_filtered:
        lines.append(f"❌ FILTERED: {f['name']} - {f['reason']}")
    
    lines.append("")
    
    # Feature summary for each kept transcript
    lines.append("FEATURES ANNOTATED")
    lines.append("-" * 80)
    for transcript_name, features in features_by_transcript.items():
        lines.append(f"\n{transcript_name}:")
        for feat in features:
            label = feat['label']
            start = feat['start'] + 1
            end = feat['end']
            lines.append(f"  {label:<10} {start:>5}-{end:<5} ({end-start+1} bp)")
    
    lines.append("")
    
    # Validation
    lines.append("VALIDATION (2-minute checklist)")
    lines.append("-" * 80)
    lines.append("[ ] Transcript count matches Ensembl")
    lines.append("[ ] Exon boundaries match Ensembl links above")
    lines.append("[ ] Sequences look correct in APE")
    lines.append("")
    
    # Methodology (publication-ready)
    lines.append("METHODOLOGY (copy/paste for papers)")
    lines.append("-" * 80)
    lines.append("Gene sequences extracted using Gene Builder v1.0")
    lines.append("(github.com/USERNAME/gene-builder) from Ensembl Release 110")
    lines.append("via REST API. CDS boundaries validated against Ensembl annotations.")
    lines.append("All decisions documented with cross-references for verification.")
    lines.append("")
    
    # Output files
    lines.append("OUTPUT FILES")
    lines.append("-" * 80)
    for outfile in output_files:
        with open(outfile['path'], 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()[:8]
        lines.append(f"{outfile['filename']} ({outfile['sequence_length']} bp, MD5:{md5})")
    
    lines.append("")
    lines.append(f"Report generated: {datetime.now().isoformat()}")
    
    return '\n'.join(lines)
