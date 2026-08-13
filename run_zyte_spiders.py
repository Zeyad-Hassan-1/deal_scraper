import sys
import json
import time
import requests
import os
import argparse

API_KEY = "aa95fec4d2144a40a1d8db18d406537d"
PROJECT_ID = "873698"

def run_spider(spider_name, query, max_price, item_count):
    url = "https://app.zyte.com/api/run.json"
    data = {
        "project": PROJECT_ID,
        "spider": spider_name,
        "query": query,
        "max_price": max_price,
        "CLOSESPIDER_ITEMCOUNT": str(item_count)
    }
    response = requests.post(url, auth=(API_KEY, ""), data=data)
    response.raise_for_status()
    result = response.json()
    if result.get("status") == "ok":
        return result["jobid"]
    else:
        raise Exception(f"Failed to start spider {spider_name}: {result}")

def check_job_status(job_id):
    url = f"https://app.zyte.com/api/jobs/list.json?project={PROJECT_ID}&job={job_id}"
    response = requests.get(url, auth=(API_KEY, ""))
    response.raise_for_status()
    jobs = response.json().get("jobs", [])
    if jobs:
        return jobs[0]["state"]
    return "unknown"

def download_items(job_id, output_path):
    url = f"https://storage.scrapinghub.com/items/{job_id}?format=json"
    response = requests.get(url, auth=(API_KEY, ""))
    response.raise_for_status()
    items = response.json()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(items)} items to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Run Scrapy Cloud spiders via Zyte API")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max_price", required=True, help="Maximum price")
    parser.add_argument("--item_count", required=True, help="Items to scrape per spider")
    
    args = parser.parse_args()
    
    print(f"Starting spiders on Zyte Cloud for query: '{args.query}' (Max Price: {args.max_price}, Items: {args.item_count})")
    
    try:
        twob_job = run_spider("twoB_eg", args.query, args.max_price, args.item_count)
        print(f"Started twoB_eg: {twob_job}")
        
        jumia_job = run_spider("jumia_eg", args.query, args.max_price, args.item_count)
        print(f"Started jumia_eg: {jumia_job}")
    except Exception as e:
        print(f"Error starting jobs: {e}")
        sys.exit(1)
        
    print("Waiting for spiders to finish...")
    
    finished_jobs = set()
    while len(finished_jobs) < 2:
        time.sleep(5)
        for job_id in [twob_job, jumia_job]:
            if job_id not in finished_jobs:
                status = check_job_status(job_id)
                if status == "finished":
                    print(f"Job {job_id} finished!")
                    finished_jobs.add(job_id)
                elif status in ["deleted", "canceled"]:
                    print(f"Job {job_id} failed or canceled.")
                    finished_jobs.add(job_id)
    
    print("Downloading results...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    twob_out = os.path.join(base_dir, "data", "raw", "2b_laptops.json")
    jumia_out = os.path.join(base_dir, "data", "raw", "jumia_laptops.json")
    
    download_items(twob_job, twob_out)
    download_items(jumia_job, jumia_out)
    
    print("All scraping completed successfully in the cloud!")

if __name__ == "__main__":
    main()
