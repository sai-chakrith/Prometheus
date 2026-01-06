import pandas as pd

# Load the dataset
df = pd.read_csv('cleaned_funding_synthetic_2010_2025.csv')

print("\n📊 DATASET VALIDATION SUMMARY")
print("=" * 70)
print(f"Total Records: {len(df):,}")
print(f"Date Range: {df['Year'].min()} - {df['Year'].max()}")
print(f"Unique Companies: {df['Startup Name'].nunique()}")
print(f"Unique Sectors: {df['Sector_Standardized'].nunique()}")
print(f"Unique Cities: {df['City'].nunique()}")
print(f"Unique States: {df['State_Standardized'].nunique()}")

print("\n📝 Sample Records:")
print(df.head(10).to_string())

print("\n🏭 Sector Distribution:")
print(df['Sector_Standardized'].value_counts().to_string())

print("\n🌆 Top 10 Cities:")
print(df['City'].value_counts().head(10).to_string())

print("\n📅 Year-wise Distribution:")
print(df['Year'].value_counts().sort_index().to_string())

print("\n💰 Top 10 Companies by Funding Count:")
print(df['Startup Name'].value_counts().head(10).to_string())

print("\n" + "=" * 70)
print("✅ Dataset validation complete!")
