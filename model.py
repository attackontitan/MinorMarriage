import pandas as pd
import statsmodels.formula.api as smf

# ===== User Parameter =====
# Choose 'AD' to compare Adopted Daughters (not ADIL) with Original Daughters
# Choose 'ADIL' to compare Adopted Daughters-in-Law with Original Daughters
compare_group = 'ADIL'  # <-- Change this to 'ADIL' if needed
print(compare_group)

# Load data
df = pd.read_excel('panel_data_output.xlsx')

# Remove Log_Birth_Gap for firstborns
df.loc[df['Firstborn'] == 1, 'Log_Birth_Gap'] = pd.NA

# Drop missing values in relevant variables
df = df.dropna(subset=[
    'Dead', 'Log_Birth_Gap', 'AD', 'ADIL', 'Age',
    'Elder_Brothers', 'Younger_Brothers', 'Elder_Sisters', 'Younger_Sisters',
    'Firstborn'
])

# ==== Filter and define Treatment based on compare_group ====
if compare_group == 'AD':
    df = df[((df['AD'] == 1) & (df['ADIL'] == 0)) | (df['AD'] == 0)].copy()
    df['Treatment'] = ((df['AD'] == 1) & (df['ADIL'] == 0)).astype(int)
elif compare_group == 'ADIL':
    df = df[(df['ADIL'] == 1) | (df['AD'] == 0)].copy()
    df['Treatment'] = (df['ADIL'] == 1).astype(int)
else:
    raise ValueError("compare_group must be either 'AD' or 'ADIL'")

# Convert Year to numeric
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

# Compute each individual's year of adoption (if treated)
df['AdoptYear'] = df.groupby('PID')['Year'].transform(
    lambda x: x[df.loc[x.index, 'Treatment'] == 1].min()
    if (df.loc[x.index, 'Treatment'] == 1).any() else pd.NA
)

# Safe function to compute Post variable
def compute_post(row):
    if pd.notna(row['AdoptYear']):
        return int(row['Year'] >= row['AdoptYear'])
    else:
        return 0

df['Post'] = df.apply(compute_post, axis=1)

# Create DID interaction
df['DID'] = df['Treatment'] * df['Post']

# Convert Year to category for fixed effects
df['Year'] = df['Year'].astype('category')

# Regression formula
formula = (
    'Dead ~ Treatment + Post + DID + '
    'Firstborn + Log_Birth_Gap + Age + '
    'Elder_Brothers + Younger_Brothers + Elder_Sisters + Younger_Sisters + '
    'C(Year)'
)

# Fit model
model = smf.ols(formula=formula, data=df)
result = model.fit(cov_type='HC1')

# Print results
print(result.summary())
