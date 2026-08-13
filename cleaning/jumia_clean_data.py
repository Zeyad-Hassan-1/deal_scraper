import pandas as pd 
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ram', type=str, help='RAM amount (e.g. 8, 16)')
parser.add_argument('--hard_disk', type=str, help='Hard disk space (e.g. 512, 1)')
args = parser.parse_args()

df = pd.read_json('../data/raw/jumia_laptops.json')
pd.set_option('display.max_columns', None)
print(df.info())

if df.empty:
    df.to_json('../data/cleaned/jumia_laptops_clean.json', orient='records', indent=2, date_format='iso')
    df.to_csv('../data/cleaned/jumia_laptops_clean.csv', index=False)
    print("Saved 0 cleaned records")
    import sys
    sys.exit(0)

# clean price column
df.price = df.price.str.replace('EGP ', '')
df.price = df.price.str.replace(',', '')
df.price = df.price.str.split('-').str[0].str.strip()
df.price = df.price.astype(float)
print(df.info())


# clean rating column
df.rating = df.rating.str.replace(' out of 5', '')
df.rating = df.rating.astype(float)
df['rating'] = df['rating'].fillna(0)
print(df.info())

# clean delivery time column
current_year = datetime.now().year

between_dates = df.delivery_time.str.extract(r'between\s+(\d+\s+\w+)\s+and\s+(\d+\s+\w+)')
on_dates = df.delivery_time.str.extract(r'on\s+(\d+\s+\w+)\s+if')

# inject current year into each extracted date string
between_start = between_dates[0] + f" {current_year}"
between_end = between_dates[1] + f" {current_year}"
on_date = on_dates[0] + f" {current_year}"

# merge "between" and "on" cases, then parse as real dates
df['best_delivery_time'] = pd.to_datetime(
    between_start.combine_first(on_date), format='%d %B %Y'
)
df['latest_delivery_time'] = pd.to_datetime(between_end, format='%d %B %Y')
df['latest_delivery_time'] = df['latest_delivery_time'].fillna(df['best_delivery_time'])

# drop unnecessary columns
df = df.drop(columns=['delivery_time','image'])
print(df.info())

# remove all non-ASCII characters from all columns (including nested dicts/lists)
import re
def clean_non_ascii(obj):
    if isinstance(obj, str):
        return re.sub(r'[^\x00-\x7F]', '', obj).strip()
    elif isinstance(obj, dict):
        return {clean_non_ascii(k): clean_non_ascii(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_non_ascii(item) for item in obj]
    return obj

for col in df.columns:
    df[col] = df[col].apply(clean_non_ascii)

# save cleaned data
if args.ram:
    # Filter where specs dictionary contains RAM value matching the requested amount
    # Jumia specs usually have 'Memory' or 'RAM'
    df = df[df['specs'].astype(str).str.contains(rf'{args.ram}\s*(GB|gb|Gigabytes)', flags=re.IGNORECASE, na=False)]

if args.hard_disk:
    df = df[df['specs'].astype(str).str.contains(rf'{args.hard_disk}\s*(GB|gb|TB|tb)', flags=re.IGNORECASE, na=False)]

df.to_json('../data/cleaned/jumia_laptops_clean.json', orient='records', indent=2, date_format='iso')
df.to_csv('../data/cleaned/jumia_laptops_clean.csv', index=False)

print(f"Saved {len(df)} cleaned records")