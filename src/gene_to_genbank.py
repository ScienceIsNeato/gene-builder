#!/usr/bin/env python3
"""
Convert gene data from Ensembl to GenBank format with proper exon/UTR annotations.
Handles alternative splicing with consistent exon numbering across variants.
Generates APE-compatible files for each splice variant.
"""

import requests
import time
from datetime import datetime
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
import argparse
import sys
import os
import hashlib

# Ensembl REST API base URL
ENSEMBL_API = "https://rest.ensembl.org"

# Color palette for features
FEATURE_COLORS = {
    '5utr': '#ffcc99',      # Orange for 5' UTR
    'exon': [                # Cycle through these for exons
        'cyan',
        '#ff00dc', 
        '#ff9fdf',
        '#d0b2ff',
        '#84ff84',
        '#ffd700',
        '#ff6b6b',
        '#4ecdc4',
    ],
    '3utr': '#ffcc99',      # Orange for 3' UTR (same as 5')
    'cds': '#b4e7ce',       # Light green for CDS
}

def ensembl_request(endpoint, params=None, max_retries=3):
    """
    Make a request to Ensembl REST API with rate limiting and retry logic.
    
    Args:
        endpoint: API endpoint
        params: Optional query parameters
        max_retries: Maximum number of retry attempts
    
    Returns:
        JSON response data
    """
    url = f"{ENSEMBL_API}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            print(f"  Request failed (attempt {attempt + 1}/{max_retries}), retrying...")
            time.sleep(1)
    
    raise Exception(f"Failed to fetch data from {endpoint} after {max_retries} attempts")

def get_gene_data(gene_symbol, species="danio_rerio"):
    """
    Fetch gene data from Ensembl.
    
    Args:
        gene_symbol: Gene symbol (e.g., "lrfn1")
        species: Species name (default: "danio_rerio" for zebrafish)
    
    Returns:
        Dict containing gene information
    """
    print(f"\nFetching gene data for {gene_symbol}...")
    gene_data = ensembl_request(f"/lookup/symbol/{species}/{gene_symbol}", 
                               params={"expand": "1"})
    return gene_data

def get_transcript_details(transcript_id):
    """
    Fetch detailed transcript information including exons.
    
    Args:
        transcript_id: Ensembl transcript ID
    
    Returns:
        Dict containing transcript details
    """
    return ensembl_request(f"/lookup/id/{transcript_id}", params={"expand": "1"})

def get_sequence(feature_id, seq_type="cdna"):
    """
    Fetch sequence for a transcript or exon.
    
    Args:
        feature_id: Ensembl feature ID
        seq_type: Sequence type ("cdna", "cds", "genomic")
    
    Returns:
        Sequence string
    """
    seq_data = ensembl_request(f"/sequence/id/{feature_id}", params={"type": seq_type})
    return seq_data.get('seq', '')

def build_gene_exon_map(gene_data):
    """
    Build a map of all exons across all transcripts of a gene.
    Assigns consistent exon numbers based on genomic position.
    
    Args:
        gene_data: Gene data from Ensembl
    
    Returns:
        Dict mapping exon_id to exon_number
    """
    print("\nBuilding gene-wide exon map...")
    
    # Collect all unique exons across all transcripts
    all_exons = {}  # exon_id -> genomic position
    
    transcripts = gene_data.get('Transcript', [])
    for transcript in transcripts:
        transcript_id = transcript.get('id')
        try:
            transcript_detail = get_transcript_details(transcript_id)
            exons = transcript_detail.get('Exon', [])
            
            for exon in exons:
                exon_id = exon.get('id')
                if exon_id not in all_exons:
                    # Store genomic position for sorting
                    all_exons[exon_id] = {
                        'start': exon.get('start'),
                        'end': exon.get('end'),
                        'id': exon_id
                    }
            
            time.sleep(0.3)  # Be nice to API
            
        except Exception as e:
            print(f"  Warning: Could not process transcript {transcript_id}: {e}")
            continue
    
    # Sort exons by genomic position
    sorted_exons = sorted(all_exons.values(), key=lambda e: e['start'])
    
    # Assign numbers
    exon_number_map = {}
    for i, exon in enumerate(sorted_exons, 1):
        exon_number_map[exon['id']] = i
    
    print(f"  Found {len(exon_number_map)} unique exons across all transcripts")
    
    return exon_number_map

def find_cds_in_transcript(transcript_detail, transcript_seq):
    """
    Find the CDS (coding sequence) boundaries within the transcript.
    CDS starts at ATG (start codon) and ends at stop codon.
    
    Args:
        transcript_detail: Transcript details from Ensembl
        transcript_seq: Full transcript sequence
    
    Returns:
        Dict with cds_start, cds_end positions in transcript (0-based)
    """
    transcript_seq_upper = transcript_seq.upper()
    
    # Get CDS sequence from Ensembl
    try:
        cds_seq = get_sequence(transcript_detail.get('id'), "cds")
        if not cds_seq:
            return None
        
        cds_seq_upper = cds_seq.upper()
        cds_length = len(cds_seq)
        
        # The CDS should start with ATG
        if not cds_seq_upper.startswith('ATG'):
            print(f"  Warning: CDS doesn't start with ATG: {cds_seq_upper[:10]}")
            return None
        
        # Find where this CDS appears in the transcript
        # Search for the CDS start (first ~50 bp) to locate it precisely
        search_length = min(50, cds_length)
        cds_start_pattern = cds_seq_upper[:search_length]
        
        cds_start = transcript_seq_upper.find(cds_start_pattern)
        if cds_start == -1:
            print(f"  Warning: Could not locate CDS in transcript")
            return None
        
        cds_end = cds_start + cds_length
        
        # Verify the match
        if transcript_seq_upper[cds_start:cds_end] == cds_seq_upper:
            return {
                'cds_start': cds_start,
                'cds_end': cds_end
            }
        else:
            print(f"  Warning: CDS sequence doesn't match transcript")
            return None
            
    except Exception as e:
        print(f"  Warning: Could not get CDS: {e}")
        return None

def annotate_transcript_features(transcript_detail, transcript_seq, exon_number_map):
    """
    Identify and annotate all features in a transcript:
    - 5' UTR
    - Exons (only coding exons, numbered consistently across gene variants)
    - 3' UTR
    
    Args:
        transcript_detail: Transcript details from Ensembl
        transcript_seq: Full transcript sequence
        exon_number_map: Dict mapping exon_id to consistent exon number
    
    Returns:
        List of feature dicts with type, start, end, label
    """
    features = []
    
    # Get CDS boundaries
    cds_info = find_cds_in_transcript(transcript_detail, transcript_seq)
    
    if not cds_info:
        # Non-coding transcript, just annotate as single feature
        features.append({
            'type': 'misc_feature',
            'label': 'transcript',
            'start': 0,
            'end': len(transcript_seq),
            'color': 'cyan'
        })
        return features
    
    cds_start = cds_info['cds_start']
    cds_end = cds_info['cds_end']
    
    # 5' UTR (if exists)
    if cds_start > 0:
        features.append({
            'type': 'misc_feature',
            'label': "5'UTR",
            'start': 0,
            'end': cds_start,
            'color': FEATURE_COLORS['5utr']
        })
    
    # Now get the exons and figure out which parts are coding
    exons = transcript_detail.get('Exon', [])
    sorted_exons = sorted(exons, key=lambda e: e.get('start'))
    
    # Calculate exon positions in transcript
    current_pos = 0
    coding_exons_found = []
    
    for exon in sorted_exons:
        exon_id = exon.get('id')
        try:
            exon_seq = get_sequence(exon_id, "genomic")
            exon_length = len(exon_seq)
            
            exon_start = current_pos
            exon_end = current_pos + exon_length
            
            # Check if this exon overlaps with CDS
            if exon_end > cds_start and exon_start < cds_end:
                # This exon contains coding sequence
                # Calculate the coding portion
                coding_start = max(exon_start, cds_start)
                coding_end = min(exon_end, cds_end)
                
                # Get the consistent exon number from the map
                exon_number = exon_number_map.get(exon_id, '?')
                
                # Choose color based on exon number (not sequential position)
                color_idx = (exon_number - 1) % len(FEATURE_COLORS['exon'])
                
                coding_exons_found.append({
                    'type': 'misc_feature',
                    'label': f'exon{exon_number}',
                    'start': coding_start,
                    'end': coding_end,
                    'color': FEATURE_COLORS['exon'][color_idx],
                    'exon_number': exon_number
                })
            
            current_pos = exon_end
            
        except Exception as e:
            print(f"  Warning: Could not process exon {exon_id}: {e}")
            continue
    
    # Add coding exons to features
    features.extend(coding_exons_found)
    
    # 3' UTR (if exists)
    if cds_end < len(transcript_seq):
        features.append({
            'type': 'misc_feature',
            'label': "3'UTR",
            'start': cds_end,
            'end': len(transcript_seq),
            'color': FEATURE_COLORS['3utr']
        })
    
    return features

def create_genbank_record(gene_symbol, transcript_name, transcript_seq, features):
    """
    Create a BioPython SeqRecord with proper feature annotations in GenBank format.
    
    Args:
        gene_symbol: Gene symbol
        transcript_name: Transcript name (e.g., "lrfn1-202")
        transcript_seq: Full transcript sequence
        features: List of feature dicts
    
    Returns:
        SeqRecord object
    """
    # Create sequence record
    seq = Seq(transcript_seq)
    record = SeqRecord(
        seq,
        id=transcript_name,
        name=gene_symbol,
        description="",
        annotations={
            "molecule_type": "DNA",
            "topology": "linear",
            "date": datetime.now().strftime("%d-%b-%Y").upper()
        }
    )
    
    # Add features
    for feat in features:
        # Use 1-based coordinates (GenBank standard) but FeatureLocation uses 0-based
        start = feat['start']
        end = feat['end']
        
        # Create feature
        feature = SeqFeature(
            FeatureLocation(start, end),
            type=feat['type'],
            qualifiers={
                "locus_tag": [feat['label']],
                "label": [feat['label']],
                "ApEinfo_label": [feat['label']],
                "ApEinfo_fwdcolor": [feat['color']],
                "ApEinfo_revcolor": ["green"],
                "ApEinfo_graphicformat": [
                    "arrow_data {{0 0.5 0 1 2 0 0 -1 0 -0.5} "
                    "{0 .5 .1 .5 .1 -.5 0 -.5} 0} width 5 offset 0"
                ]
            }
        )
        record.features.append(feature)
    
    return record

def write_genbank_file(record, output_path):
    """
    Write SeqRecord to GenBank file with ApEinfo formatting.
    
    Args:
        record: SeqRecord object
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        # Write manually to ensure ApEinfo comment is included
        f.write(f"LOCUS       {record.name:<20}{len(record.seq):>6} bp    DNA        linear       {record.annotations['date']}\n")
        f.write("DEFINITION  .\n")
        f.write("ACCESSION   \n")
        f.write("VERSION     \n")
        f.write("SOURCE      .\n")
        f.write("  ORGANISM  .\n")
        f.write("COMMENT     \n")
        f.write("COMMENT     ApEinfo:methylated:1\n")
        
        # Write features
        if record.features:
            f.write("FEATURES             Location/Qualifiers\n")
            for feature in record.features:
                # Write feature location (convert to 1-based)
                start = feature.location.start + 1
                end = feature.location.end
                f.write(f"     {feature.type:<16}{start}..{end}\n")
                
                # Write qualifiers
                for key, values in feature.qualifiers.items():
                    for value in values:
                        # Handle multi-line qualifiers
                        f.write(f"                     /{key}=\"{value}\"\n")
        
        # Write sequence
        f.write("ORIGIN\n")
        seq_str = str(record.seq).upper()
        for i in range(0, len(seq_str), 60):
            line = seq_str[i:i+60]
            # Format: 10 bp per group, 6 groups per line
            formatted = ' '.join([line[j:j+10] for j in range(0, len(line), 10)])
            f.write(f"{i+1:>9} {formatted}\n")
        
        f.write("//\n")

def generate_audit_report(gene_data, gene_symbol, species, transcripts_kept, 
                         transcripts_filtered, exon_map, features_by_transcript, output_files):
    """Generate concise audit report with verification links"""
    
    gene_id = gene_data.get('id')
    gene_name = gene_data.get('display_name')
    chrom = gene_data.get('seq_region_name')
    start = gene_data.get('start')
    end = gene_data.get('end')
    
    lines = []
    lines.append(f"GENE EXTRACTION AUDIT - {gene_symbol}")
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
        lines.append(f"   https://ensembl.org/Danio_rerio/Transcript/Exons?t={tid}")
    
    for f in transcripts_filtered:
        reason = f.get('reason', 'unknown')
        lines.append(f"❌ FILTERED: {f['name']} - {reason}")
    
    lines.append("")
    
    # Features for each transcript
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
    
    # Validation checklist
    lines.append("VALIDATION CHECKLIST")
    lines.append("-" * 80)
    lines.append("[ ] Transcript count matches Ensembl")
    lines.append("[ ] Exon boundaries match links above")
    lines.append("[ ] Output looks correct in APE")
    lines.append("")
    
    # Methodology
    lines.append("METHODOLOGY (for papers)")
    lines.append("-" * 80)
    lines.append(f"Gene sequences extracted using Gene Builder")
    lines.append(f"(github.com/USERNAME/gene-builder) from Ensembl Release 110.")
    lines.append(f"Species: {species}. CDS boundaries from Ensembl annotations.")
    lines.append(f"Exon numbering based on genomic position across variants.")
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

def filter_duplicate_transcripts(gene_data, canonical_only=False):
    """
    Filter out transcripts that are duplicates or subsets of other transcripts.
    Keeps the longest/most complete transcript when duplicates are found.
    
    Args:
        gene_data: Gene data from Ensembl
        canonical_only: If True, only keep canonical transcript(s)
    
    Returns:
        List of transcript dicts to keep, list of filtered transcript info
    """
    transcripts = gene_data.get('Transcript', [])
    
    if len(transcripts) <= 1:
        return transcripts, []
    
    print("\n" + "="*80)
    print("Filtering duplicate/subset transcripts...")
    print("="*80)
    
    # Get detailed info for all transcripts
    transcript_info = []
    for transcript in transcripts:
        transcript_id = transcript.get('id')
        try:
            detail = get_transcript_details(transcript_id)
            exons = detail.get('Exon', [])
            exon_ids = set(exon.get('id') for exon in exons)
            
            # Get genomic span
            start = transcript.get('start')
            end = transcript.get('end')
            span = end - start if start and end else 0
            
            transcript_info.append({
                'transcript': transcript,
                'detail': detail,
                'id': transcript_id,
                'name': transcript.get('display_name'),
                'exon_ids': exon_ids,
                'exon_count': len(exon_ids),
                'start': start,
                'end': end,
                'span': span,
                'is_canonical': transcript.get('is_canonical', False)
            })
            
            time.sleep(0.3)
        except Exception as e:
            print(f"  Warning: Could not analyze transcript {transcript_id}: {e}")
            continue
    
    # Filter duplicates/subsets
    to_keep = []
    filtered = []
    
    for i, info_i in enumerate(transcript_info):
        should_filter = False
        filter_reason = None
        filter_details = {}
        
        # Filter non-canonical if canonical_only mode
        if canonical_only and not info_i['is_canonical']:
            should_filter = True
            filter_reason = 'non_canonical'
            filter_details = {'note': 'Canonical-only mode enabled'}
        
        for j, info_j in enumerate(transcript_info):
            if i == j:
                continue
            
            # Check 1: Exon set subset (transcript i's exons are subset of j's)
            if info_i['exon_ids'].issubset(info_j['exon_ids']):
                # i is a subset of j
                # Keep j (the superset) unless i is canonical and j is not
                if not info_i['is_canonical'] or info_j['is_canonical']:
                    should_filter = True
                    filter_reason = 'exon_subset'
                    filter_details = {
                        'superset': info_j['name'],
                        'exons_this': info_i['exon_count'],
                        'exons_super': info_j['exon_count']
                    }
                    break
            
            # Check 2: Genomic containment (transcript i is fully contained in j's genomic span)
            # AND i has fewer exons (suggesting it's a partial transcript)
            if (info_i['start'] >= info_j['start'] and 
                info_i['end'] <= info_j['end'] and 
                info_i['exon_count'] < info_j['exon_count']):
                # i is genomically contained within j and has fewer exons
                # Keep j unless i is canonical and j is not
                if not info_i['is_canonical'] or info_j['is_canonical']:
                    should_filter = True
                    filter_reason = 'genomic_subset'
                    filter_details = {
                        'superset': info_j['name'],
                        'exons_this': info_i['exon_count'],
                        'exons_super': info_j['exon_count'],
                        'span_this': info_i['span'],
                        'span_super': info_j['span']
                    }
                    break
        
        if should_filter:
            filtered.append({
                'name': info_i['name'],
                'id': info_i['id'],
                'reason': filter_reason,
                'details': filter_details
            })
            
            print(f"\n  🚫 FILTERED: {info_i['name']}")
            if filter_reason == 'non_canonical':
                print(f"     Reason: Non-canonical transcript (canonical-only mode)")
                print(f"     Exons: {info_i['exon_count']}")
                print(f"     Genomic span: {info_i['start']}-{info_i['end']} ({info_i['span']:,} bp)")
            elif filter_reason == 'exon_subset':
                print(f"     Reason: Exon subset of {filter_details['superset']}")
                print(f"     This has {filter_details['exons_this']} exons, superset has {filter_details['exons_super']} exons")
            elif filter_reason == 'genomic_subset':
                print(f"     Reason: Genomically contained within {filter_details['superset']}")
                print(f"     This: {info_i['start']}-{info_i['end']} ({info_i['span']:,} bp, {filter_details['exons_this']} exons)")
                print(f"     Superset: {info_j['start']}-{info_j['end']} ({filter_details['span_super']:,} bp, {filter_details['exons_super']} exons)")
                print(f"     Likely a partial/truncated transcript")
        else:
            to_keep.append(info_i['transcript'])
            print(f"\n  ✓ KEEPING: {info_i['name']}")
            print(f"     Exons: {info_i['exon_count']}")
            print(f"     Genomic span: {info_i['start']}-{info_i['end']} ({info_i['span']:,} bp)")
            if info_i['is_canonical']:
                print(f"     Status: CANONICAL")
    
    print(f"\n  Summary: Keeping {len(to_keep)}/{len(transcripts)} transcripts")
    if filtered:
        print(f"  Filtered {len(filtered)} duplicate/subset transcript(s)")
    
    return to_keep, filtered

def process_gene(gene_symbol, species="danio_rerio", output_dir="output", canonical_only=False):
    """
    Process a gene and generate GenBank files for all splice variants.
    
    Args:
        gene_symbol: Gene symbol to process
        species: Species name
        output_dir: Output directory for GenBank files
        canonical_only: Only process canonical transcript(s)
    
    Returns:
        List of generated file paths
    """
    # Create output directory
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_dir_name = f"{gene_symbol}_{run_timestamp}"
    run_output_dir = os.path.join(output_dir, run_dir_name)
    os.makedirs(run_output_dir, exist_ok=True)
    
    print(f"Saving results to: {run_output_dir}")
    
    # Get gene data
    gene_data = get_gene_data(gene_symbol, species)
    gene_id = gene_data.get('id')
    gene_display_name = gene_data.get('display_name')
    
    print(f"Gene: {gene_display_name} ({gene_id})")
    print(f"Description: {gene_data.get('description', 'N/A')}")
    print(f"Location: {gene_data.get('seq_region_name')}:{gene_data.get('start')}-{gene_data.get('end')}")
    
    # Get transcripts
    all_transcripts = gene_data.get('Transcript', [])
    print(f"\nFound {len(all_transcripts)} transcript(s) in Ensembl")
    
    # Filter duplicates/subsets
    transcripts, filtered_info = filter_duplicate_transcripts(gene_data, canonical_only=canonical_only)
    
    # Build gene-wide exon numbering map (using filtered transcripts)
    gene_data['Transcript'] = transcripts  # Update gene data with filtered list
    exon_number_map = build_gene_exon_map(gene_data)
    
    generated_files = []
    features_by_transcript = {}  # For audit report
    
    for transcript in transcripts:
        transcript_id = transcript.get('id')
        transcript_name = transcript.get('display_name')
        is_canonical = transcript.get('is_canonical', False)
        
        print(f"\n{'='*80}")
        print(f"Processing: {transcript_name} ({transcript_id})")
        if is_canonical:
            print("  [CANONICAL TRANSCRIPT]")
        
        # Get detailed transcript info
        print("  Fetching transcript details...")
        transcript_detail = get_transcript_details(transcript_id)
        
        # Get transcript sequence
        print("  Fetching transcript sequence...")
        transcript_seq = get_sequence(transcript_id, "cdna")
        print(f"  Transcript length: {len(transcript_seq)} bp")
        
        # Annotate features (5'UTR, exons, 3'UTR)
        print("  Identifying features (5'UTR, exons, 3'UTR)...")
        features = annotate_transcript_features(transcript_detail, transcript_seq, exon_number_map)
        
        print(f"  Found {len(features)} features:")
        for feat in features:
            print(f"    {feat['label']}: {feat['start']}-{feat['end']} ({feat['end']-feat['start']} bp)")
        
        # Store for audit report
        features_by_transcript[transcript_name] = features
        
        # Create GenBank record
        print("  Creating GenBank record...")
        record = create_genbank_record(gene_symbol, transcript_name, transcript_seq, features)
        
        # Write to file
        output_filename = f"{gene_symbol}_{transcript_name}.gbk"
        output_path = os.path.join(run_output_dir, output_filename)
        print(f"  Writing to {output_path}...")
        write_genbank_file(record, output_path)
        
        generated_files.append({
            'path': output_path,
            'filename': output_filename,
            'transcript_name': transcript_name,
            'transcript_id': transcript_id,
            'sequence_length': len(transcript_seq),
            'feature_count': len(features)
        })
        print(f"  ✓ Complete!")
        
        # Be nice to the API
        time.sleep(0.5)
    
    # Generate audit report
    print(f"\n{'='*80}")
    print("Generating audit report...")
    audit_content = generate_audit_report(
        gene_data, gene_symbol, species, 
        transcripts, filtered_info, 
        exon_number_map, features_by_transcript, 
        generated_files
    )
    
    audit_filename = f"{gene_symbol}_audit_report.txt"
    audit_path = os.path.join(run_output_dir, audit_filename)
    with open(audit_path, 'w') as f:
        f.write(audit_content)
    print(f"Audit report saved: {audit_path}")
    
    return generated_files

def main():
    parser = argparse.ArgumentParser(
        description="Extract gene sequences from Ensembl and generate GenBank files with consistent exon numbering across splice variants"
    )
    parser.add_argument(
        "gene_symbol",
        help="Gene symbol to extract (e.g., 'lrfn1', 'nrxn1a')"
    )
    parser.add_argument(
        "--species",
        default="danio_rerio",
        help="Species name (default: danio_rerio for zebrafish)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for GenBank files (default: output)"
    )
    parser.add_argument(
        "--canonical-only",
        action="store_true",
        help="Only output the canonical transcript (filters all non-canonical variants)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("Gene Builder - Ensembl to GenBank Converter")
    print("Alternative Splicing-Aware Exon Numbering")
    print("="*80)
    
    try:
        generated_files = process_gene(
            args.gene_symbol,
            args.species,
            args.output_dir,
            args.canonical_only
        )
        
        print("\n" + "="*80)
        print("✓ SUCCESS!")
        print("="*80)
        print(f"\nGenerated {len(generated_files)} file(s):")
        for filepath in generated_files:
            print(f"  - {filepath}")
        print()
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
