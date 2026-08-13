import pandas as pd
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ram', type=str, help='RAM amount (e.g. 8, 16)')
parser.add_argument('--hard_disk', type=str, help='Hard disk space (e.g. 512, 1)')
args = parser.parse_args()

df = pd.read_json('../data/raw/2b_laptops.json')
pd.set_option('display.max_columns', None)
print(df.info())

if df.empty:
    df.to_json('../data/cleaned/2b_laptops_clean.json', orient='records', indent=2, date_format='iso')
    df.to_csv('../data/cleaned/2b_laptops_clean.csv', index=False)
    print("Saved 0 cleaned records")
    import sys
    sys.exit(0)

# clean title column (strip leading/trailing whitespace and newlines)
df['title'] = df['title'].str.strip()

# clean price column (note: uses non-breaking space \xa0, not regular space)
df['price'] = df['price'].str.replace('EGP\xa0', '', regex=False)
df['price'] = df['price'].str.replace(',', '', regex=False)
df['price'] = df['price'].astype(str).str.split('-').str[0].str.strip()
df['price'] = df['price'].astype(float)

# clean old_price column (same treatment, may contain NaN for no-discount products)
df['old_price'] = df['old_price'].str.replace('EGP\xa0', '', regex=False)
df['old_price'] = df['old_price'].str.replace(',', '', regex=False)
df['old_price'] = df['old_price'].astype(float)
print(df.info())

# clean rating column
df['rating'] = df['rating'].astype(float)
df['rating'] = df['rating'].fillna(0)
print(df.info())

# delivery_cairo / delivery_outside are descriptive text, not dates - left as-is

# remove all non-ASCII characters from all columns (including nested dicts/lists)
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
    df = df[df['specs'].astype(str).str.contains(rf'{args.ram}\s*(GB|gb|Gigabytes|G)', flags=re.IGNORECASE, na=False)]

if args.hard_disk:
    df = df[df['specs'].astype(str).str.contains(rf'{args.hard_disk}\s*(GB|gb|TB|tb|T)', flags=re.IGNORECASE, na=False)]

df.to_json('../data/cleaned/2b_laptops_clean.json', orient='records', indent=2, date_format='iso')
df.to_csv('../data/cleaned/2b_laptops_clean.csv', index=False)

print(f"Saved {len(df)} cleaned records")