import pandas as pd

jumia = pd.read_json('../data/cleaned/jumia_laptops_clean.json')
twob = pd.read_json('../data/cleaned/2b_laptops_clean.json')

# keep only the shared, comparable columns
common_cols = ['title', 'price', 'rating', 'sku', 'specs', 'url', 'store', 'country']

jumia_common = pd.DataFrame(columns=common_cols) if jumia.empty else jumia[common_cols]
twob_common = pd.DataFrame(columns=common_cols) if twob.empty else twob[common_cols]

# stack both stores into one combined dataset
combined = pd.concat([jumia_common, twob_common], ignore_index=True)

print(combined.info())
print(combined.head())

combined.to_json('../data/cleaned/combined_laptops.json', orient='records', indent=2)
combined.to_csv('../data/cleaned/combined_laptops.csv', index=False)

print(f"Combined {len(combined)} total records ({len(jumia_common)} Jumia + {len(twob_common)} 2B)")