#!/usr/bin/env python3
"""
Exploration script to query Ensembl REST API for LRFN1 and examine available data.
This helps us understand the data structure before building the full tool.
"""

import requests
import json
import time

# Ensembl REST API base URL
ENSEMBL_API = "https://rest.ensembl.org"

def ensembl_request(endpoint, params=None):
    """
    Make a request to Ensembl REST API with rate limiting.
    
    Args:
        endpoint: API endpoint (e.g., "/lookup/symbol/danio_rerio/lrfn1")
        params: Optional query parameters
    
    Returns:
        JSON response data
    """
    url = f"{ENSEMBL_API}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 429:  # Rate limited
        print("Rate limited, waiting...")
        time.sleep(1)
        return ensembl_request(endpoint, params)
    
    response.raise_for_status()
    return response.json()

def explore_gene(gene_symbol="lrfn1", species="danio_rerio"):
    """
    Explore a gene in the specified species using Ensembl REST API.
    
    Args:
        gene_symbol: Gene symbol to search for (e.g., "lrfn1")
        species: Species name (e.g., "danio_rerio" for zebrafish)
    """
    print(f"\n{'='*80}")
    print(f"Exploring gene: {gene_symbol} in {species}")
    print(f"{'='*80}\n")
    
    # Step 1: Look up the gene
    print("Step 1: Looking up gene...")
    gene_data = ensembl_request(f"/lookup/symbol/{species}/{gene_symbol}", 
                                params={"expand": "1"})
    
    print(f"\n{'-'*80}")
    print("Gene Information:")
    print(f"  Display Name: {gene_data.get('display_name')}")
    print(f"  Gene ID: {gene_data.get('id')}")
    print(f"  Description: {gene_data.get('description', 'N/A')}")
    print(f"  Location: {gene_data.get('seq_region_name')}:{gene_data.get('start')}-{gene_data.get('end')}")
    print(f"  Strand: {'+' if gene_data.get('strand') == 1 else '-'}")
    print(f"  Biotype: {gene_data.get('biotype')}")
    
    # Step 2: Get transcripts
    transcripts = gene_data.get('Transcript', [])
    print(f"\nNumber of transcripts (splice variants): {len(transcripts)}")
    
    for i, transcript in enumerate(transcripts, 1):
        print(f"\n{'-'*80}")
        print(f"Transcript {i}:")
        print(f"  ID: {transcript.get('id')}")
        print(f"  Display Name: {transcript.get('display_name')}")
        print(f"  Biotype: {transcript.get('biotype')}")
        print(f"  Location: {transcript.get('start')}-{transcript.get('end')}")
        print(f"  Is canonical: {transcript.get('is_canonical', False)}")
        
        # Get exons
        transcript_id = transcript.get('id')
        print(f"\n  Fetching detailed information for transcript {transcript_id}...")
        
        transcript_detail = ensembl_request(f"/lookup/id/{transcript_id}", 
                                           params={"expand": "1"})
        
        exons = transcript_detail.get('Exon', [])
        print(f"  Number of exons: {len(exons)}")
        
        for j, exon in enumerate(exons, 1):
            print(f"\n    Exon {j}:")
            print(f"      ID: {exon.get('id')}")
            print(f"      Location: {exon.get('start')}-{exon.get('end')}")
            length = exon.get('end') - exon.get('start') + 1
            print(f"      Length: {length} bp")
        
        # Get transcript sequence
        print(f"\n  Fetching sequence for transcript {transcript_id}...")
        seq_data = ensembl_request(f"/sequence/id/{transcript_id}", 
                                   params={"type": "cdna"})
        
        sequence = seq_data.get('seq', '')
        print(f"  Full transcript (cDNA) sequence length: {len(sequence)} bp")
        print(f"  First 100 bp: {sequence[:100]}...")
        
        # Get CDS sequence if it's protein coding
        if transcript.get('biotype') == 'protein_coding':
            cds_data = ensembl_request(f"/sequence/id/{transcript_id}", 
                                      params={"type": "cds"})
            cds_sequence = cds_data.get('seq', '')
            print(f"  Coding sequence (CDS) length: {len(cds_sequence)} bp")
            print(f"  CDS first 100 bp: {cds_sequence[:100]}...")
        
        # Get exon sequences
        print(f"\n  Fetching individual exon sequences...")
        for j, exon in enumerate(exons[:3], 1):  # Show first 3 exons as example
            exon_id = exon.get('id')
            exon_seq = ensembl_request(f"/sequence/id/{exon_id}")
            exon_sequence = exon_seq.get('seq', '')
            print(f"    Exon {j} sequence length: {len(exon_sequence)} bp")
            print(f"    Exon {j} first 50 bp: {exon_sequence[:50]}...")
        
        if len(exons) > 3:
            print(f"    ... and {len(exons) - 3} more exons")
        
        print(f"\n  {'='*80}")
        time.sleep(0.5)  # Be nice to the API

def main():
    print("\nGene Builder - Ensembl REST API Exploration Tool")
    print("=" * 80)
    
    try:
        explore_gene("lrfn1", "danio_rerio")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
