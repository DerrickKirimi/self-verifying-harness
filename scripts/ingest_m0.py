"""Compatibility entry point for the budgeted sequential ingestion CLI."""
import argparse
from pathlib import Path
from svh.ingest import ingest_corpus

parser = argparse.ArgumentParser()
parser.add_argument('--only')
args = parser.parse_args()
ingest_corpus(Path(__file__).resolve().parents[1], Path('evals/frozen-m0.json'), args.only)
