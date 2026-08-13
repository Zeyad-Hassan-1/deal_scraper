import pandas as pd
import json

combined = pd.read_json('../data/cleaned/combined_laptops.json')

import os
import sys
csv_path = '../data/cleaned/filter_results.csv'

if combined.empty:
    if os.path.exists(csv_path):
        os.remove(csv_path)
    print("0 results found in combined data. File was not created.")
    sys.exit(0)
def specs_to_text(specs):
    """Flatten a specs dict (including nested features lists) into one searchable string."""
    if not specs:
        return ""
    parts = []
    for key, value in specs.items():
        if isinstance(value, list):
            parts.extend(str(v) for v in value)
        else:
            parts.append(str(value))
    return " ".join(parts).lower()

combined['search_text'] = (combined['title'] + " " + combined['specs'].apply(specs_to_text)).str.lower()

def filter_laptops(df, ram=None, hard_disk=None, gpu_keyword=None, cpu_keyword=None, max_price=None, min_price=None):
    result = df.copy()
    
    if ram:
        import re
        pattern = re.compile(rf"(?:ram|memory)[\s:-]*{ram}\s*gb|{ram}\s*gb[\s:-]*(?:ram|memory)", re.IGNORECASE)
        
        # Match if the pattern is in search_text OR if the exact ram amount is in the title
        title_match = result['title'].str.contains(f"\\b{ram}gb\\b", na=False, case=False) | result['title'].str.contains(f"\\b{ram} gb\\b", na=False, case=False)
        specs_match = result['search_text'].apply(lambda x: bool(pattern.search(x)))
        result = result[title_match | specs_match]
    if hard_disk:
        import re
        pattern = re.compile(rf"{hard_disk}\s*(?:gb|tb|g|t)", re.IGNORECASE)
        title_match = result['title'].str.contains(f"\\b{hard_disk}\\s*(gb|tb)\\b", na=False, case=False)
        specs_match = result['search_text'].apply(lambda x: bool(pattern.search(x)))
        result = result[title_match | specs_match]
    if gpu_keyword:
        result = result[result['search_text'].str.contains(gpu_keyword.lower(), na=False)]
    if cpu_keyword:
        result = result[result['search_text'].str.contains(cpu_keyword.lower(), na=False)]
    if max_price:
        result = result[result['price'] <= max_price]
    if min_price:
        result = result[result['price'] >= min_price]
    
    return result.sort_values('price')[['title', 'price', 'store', 'url']]

import argparse

def parse_float(val):
    if not val or val.lower() == "null" or str(val).strip() == "":
        return None
    return float(val)

def parse_int(val):
    if not val or val.lower() == "null" or str(val).strip() == "":
        return None
    return int(val)

def parse_str(val):
    if not val or val.lower() == "null" or str(val).strip() == "":
        return None
    return str(val)

def main():
    parser = argparse.ArgumentParser(description="Filter scraped laptops")
    parser.add_argument('--ram', type=parse_int, help='Minimum RAM in GB')
    parser.add_argument('--hard_disk', type=parse_str, help='Hard disk size (e.g. 512, 1TB)')
    parser.add_argument('--gpu', type=parse_str, help='GPU keyword (e.g. rtx 3050)')
    parser.add_argument('--cpu', type=parse_str, help='CPU keyword')
    parser.add_argument('--max-price', type=parse_float, help='Maximum price')
    parser.add_argument('--min-price', type=parse_float, help='Minimum price')
    args = parser.parse_args()

    results = filter_laptops(
        combined, 
        ram=args.ram, 
        hard_disk=args.hard_disk,
        gpu_keyword=args.gpu, 
        cpu_keyword=args.cpu, 
        max_price=args.max_price, 
        min_price=args.min_price
    )
    
    import os
    
    csv_path = '../data/cleaned/filter_results.csv'
    
    if len(results) == 0:
        if os.path.exists(csv_path):
            os.remove(csv_path)
        print("0 results found. File was not created.")
    else:
        results.to_csv(csv_path, index=False)
        print(f"Saved {len(results)} results to {csv_path}")

if __name__ == "__main__":
    main()