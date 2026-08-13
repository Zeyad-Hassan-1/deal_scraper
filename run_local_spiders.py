import sys
import subprocess
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Run Scrapy spiders locally")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max_price", required=True, help="Maximum price")
    parser.add_argument("--item_count", required=True, help="Items to scrape per spider")
    
    args = parser.parse_args()
    
    print(f"Starting LOCAL spiders for query: '{args.query}' (Max Price: {args.max_price}, Items: {args.item_count})")
    
    scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers")
    
    # Run TwoB Spider
    twob_cmd = [
        "scrapy", "crawl", "twoB_eg",
        "-a", f"query={args.query}",
        "-a", f"max_price={args.max_price}",
        "-s", f"CLOSESPIDER_ITEMCOUNT={args.item_count}",
        "-O", "../data/raw/2b_laptops.json"
    ]
    
    # Run Jumia Spider
    jumia_cmd = [
        "scrapy", "crawl", "jumia_eg",
        "-a", f"query={args.query}",
        "-a", f"max_price={args.max_price}",
        "-s", f"CLOSESPIDER_ITEMCOUNT={args.item_count}",
        "-O", "../data/raw/jumia_laptops.json"
    ]
    
    print("Running TwoB Spider...")
    twob_process = subprocess.Popen(twob_cmd, cwd=scrapers_dir)
    
    print("Running Jumia Spider...")
    jumia_process = subprocess.Popen(jumia_cmd, cwd=scrapers_dir)
    
    # Wait for both to finish
    twob_process.wait()
    jumia_process.wait()
    
    if twob_process.returncode != 0 or jumia_process.returncode != 0:
        print("One or more spiders failed to run correctly.")
        sys.exit(1)
        
    print("All LOCAL scraping completed successfully!")

if __name__ == "__main__":
    main()
