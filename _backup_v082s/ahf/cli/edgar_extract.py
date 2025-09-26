# -*- coding: utf-8 -*-
"""EDGAR統合CLI
Usage: python -m cli.edgar_extract <CIK>
"""
import sys
import json
from mvp4.edgar_integration import extract_from_edgar

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m cli.edgar_extract <CIK>")
        print("Example: python -m cli.edgar_extract 0001753539")
        sys.exit(1)
    
    cik = sys.argv[1]
    
    try:
        result = extract_from_edgar(cik)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
