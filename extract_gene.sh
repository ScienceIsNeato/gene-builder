#!/bin/bash
# Simple wrapper for gene extraction
# Usage: ./extract_gene.sh GENE_SYMBOL

if [ -z "$1" ]; then
    echo "Usage: ./extract_gene.sh GENE_SYMBOL"
    echo "Example: ./extract_gene.sh lrfn1"
    exit 1
fi

cd "$(dirname "$0")"
source venv/bin/activate
python src/gene_to_genbank.py "$1" --canonical-only

