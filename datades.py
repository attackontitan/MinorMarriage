# -*- coding: utf-8 -*-

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# File paths (update if necessary)
blood_siblings_file = "D:/User_Data/Downloads/女性及其兄弟姐妹_cp.xlsx"
adopted_siblings_file = "D:/User_Data/Downloads/女性及其養兄弟姐妹_cp.xlsx"

# %% Read Excel files
df_blood = pd.read_excel(blood_siblings_file)
df_adopted = pd.read_excel(adopted_siblings_file)

# %% Step 1: Count total unique females
total_females = df_blood['PID'].nunique()
adopted_females = df_adopted['PID'].nunique()
adopted_percentage = (adopted_females / total_females) * 100 if total_females > 0 else 0

# %% Step 2: Drop duplicates to get unique adopted females
df_adopted_unique = df_adopted.drop_duplicates(subset=['PID'])

# %% Step 3: Filter valid and invalid location data
nearby_cols = ['同街庄', '同郡堡', '同州廳']
invalid_values = [9999, 0]

invalid_adoptions = df_adopted_unique[df_adopted_unique[nearby_cols].isin(invalid_values).all(axis=1)]
invalid_count = invalid_adoptions['PID'].nunique()
invalid_percentage = (invalid_count / adopted_females) * 100 if adopted_females > 0 else 0

valid_adoptions = df_adopted_unique[~df_adopted_unique[nearby_cols].isin(invalid_values).all(axis=1)]
valid_count = valid_adoptions['PID'].nunique()
valid_percentage = (valid_count / adopted_females) * 100 if adopted_females > 0 else 0

# %% Step 4: Break Down Nearby Adoptions
nearby_street = valid_adoptions[valid_adoptions['同街庄'] == 1]['PID'].nunique()
nearby_county = valid_adoptions[valid_adoptions['同郡堡'] == 1]['PID'].nunique()
nearby_state = valid_adoptions[valid_adoptions['同州廳'] == 1]['PID'].nunique()

# %% Step 5: Count Minor Marriages
minor_marriages = df_adopted_unique[df_adopted_unique['MarType'] == 3]['PID'].nunique()
minor_marriage_percentage = (minor_marriages / adopted_females) * 100 if adopted_females > 0 else 0

# %% Step 6: Count Father's Occupation Distribution
occupation_counts = df_adopted_unique['Occu'].value_counts(normalize=True) * 100
occupation_distribution = occupation_counts.reset_index()
occupation_distribution.columns = ['Occupation', 'Percentage']
significant_occupations = occupation_distribution[occupation_distribution['Percentage'] >= 1]

# %% Step 7: Display Summary
summary_df = pd.DataFrame({
    'Category': [
        'Total Unique Females',
        'Adopted Females',
        'Adopted with Invalid Location Data',
        'Adopted with Valid Location Data',
        'Adopted to Nearby Street',
        'Adopted to Nearby County',
        'Adopted to Nearby State',
        'Entered Minor Marriage (MarType==3)'
    ],
    'Count': [
        total_females,
        adopted_females,
        invalid_count,
        valid_count,
        nearby_street,
        nearby_county,
        nearby_state,
        minor_marriages
    ],
    'Percentage': [
        '-',
        f"{adopted_percentage:.2f}%",
        f"{invalid_percentage:.2f}%",
        f"{valid_percentage:.2f}%",
        f"{(nearby_street / valid_count * 100) if valid_count > 0 else 0:.2f}%",
        f"{(nearby_county / valid_count * 100) if valid_count > 0 else 0:.2f}%",
        f"{(nearby_state / valid_count * 100) if valid_count > 0 else 0:.2f}%",
        f"{minor_marriage_percentage:.2f}%"
    ]
})

print(summary_df)
print("\nFather's Occupation Distribution (>=1%):")
print(significant_occupations.to_string(index=False))

# %% Step 8: Plot Birth Order Distribution
plt.figure(figsize=(10, 5))
sns.histplot(df_blood['SibOrder'], bins=20, kde=True)
plt.title("Birth Order Distribution in Original Family")
plt.xlabel("Birth Order")
plt.ylabel("Count")
plt.show()

plt.figure(figsize=(10, 5))
sns.histplot(df_adopted_unique['SibOrder'], bins=20, kde=True)
plt.title("Birth Order Distribution in Adopted Family")
plt.xlabel("Birth Order")
plt.ylabel("Count")
plt.show()

# %% Step 9: Plot Age at Death for Those Who Died (Unique Individuals Only)
df_blood['birthdate'] = pd.to_datetime(df_blood['birthdate'], errors='coerce')
df_blood['eodate'] = pd.to_datetime(df_blood['eodate'], errors='coerce')
df_blood['age_at_death'] = (df_blood['eodate'] - df_blood['birthdate']).dt.days / 365.25

# Only keep one death record per PID (e.g., first by eodate)
df_deceased = (
    df_blood[df_blood['eocode'] == 2]
    .sort_values('eodate')
    .drop_duplicates(subset='PID', keep='first')
    .copy()
)

df_deaths_under_20 = df_deceased[df_deceased['age_at_death'] < 20]

print("\nDeaths under age 20:")
print(df_deaths_under_20[['PID', 'birthdate', 'eodate', 'age_at_death']])

plt.figure(figsize=(10, 5))
sns.histplot(df_deceased['age_at_death'], bins=30, kde=False)
plt.title("Distribution of Age at Death (All Deceased, eocode == 2, Unique PIDs)")
plt.xlabel("Age at Death")
plt.ylabel("Count")
plt.grid(True)
plt.tight_layout()
plt.show()

# %% Step 10: Summary of Deaths Under 20 by Age Group
bins = [0, 1, 2, 3, 4, 5, 11, 16, 20]
labels = ['0', '1', '2', '3', '4', '5-10', '11-15', '16-19']
df_deaths_under_20['age_group'] = pd.cut(df_deaths_under_20['age_at_death'], bins=bins, labels=labels, right=False)
death_counts = df_deaths_under_20['age_group'].value_counts().sort_index()

print("\nNumber of girls who died before age 20:", len(df_deaths_under_20))
print("\nDeath Age Distribution (percentage among deaths under 20):")
print((death_counts / len(df_deaths_under_20) * 100).round(2).astype(str) + '%')

# %% Step 11: Summary of Deaths Under 20 by Age Group

# Classification: who died before adoption, after adoption but before marriage, and after adoption and marriage
panel_df = pd.read_excel('panel_data_output.xlsx')

# Identify first year where each individual died
first_death = panel_df[panel_df['Dead'] == 1].sort_values('Year').drop_duplicates('PID')

death_before_adoption = first_death[first_death['BD'] == 1]
death_after_adoption_before_marriage = first_death[(first_death['AD'] == 1) & (first_death['ADIL'] == 0)]
death_after_adoption_and_marriage = first_death[first_death['ADIL'] == 1]

# Print death share by category (percentage of all unique PIDs)
total_pids = panel_df['PID'].nunique()
print("Death Classification Percentages:")
print(f"Original daughters (before adoption): {(len(death_before_adoption)/total_pids*100):.2f}%")
print(f"Adopted daughters (after adoption, before marriage): {(len(death_after_adoption_before_marriage)/total_pids*100):.2f}%")
print(f"ADIL (after adoption and marriage): {(len(death_after_adoption_and_marriage)/total_pids*100):.2f}%")


# Also compute death category shares among deaths under 20
under20_pids = set(df_deaths_under_20['PID'])

under20_before_adoption = len(set(death_before_adoption['PID']) & under20_pids)
under20_after_adoption_before_marriage = len(set(death_after_adoption_before_marriage['PID']) & under20_pids)
under20_after_adoption_and_marriage = len(set(death_after_adoption_and_marriage['PID']) & under20_pids)

print("Death Classification Percentages (among deaths under 20):")
total_under20 = len(df_deaths_under_20)
print(f"Original daughters (before adoption): {(under20_before_adoption / total_under20 * 100):.2f}%")
print(f"Adopted daughters (after adoption, before marriage): {(under20_after_adoption_before_marriage / total_under20 * 100):.2f}%")
print(f"ADIL (after adoption and marriage): {(under20_after_adoption_and_marriage / total_under20 * 100):.2f}%")

# Continue with age group summary
bins = [0, 1, 2, 3, 4, 5, 11, 16, 20]
labels = ['0', '1', '2', '3', '4', '5-10', '11-15', '16-19']
df_deaths_under_20['age_group'] = pd.cut(df_deaths_under_20['age_at_death'], bins=bins, labels=labels, right=False)
death_counts = df_deaths_under_20['age_group'].value_counts().sort_index()

print("\nNumber of girls who died before age 20:", len(df_deaths_under_20))
print("\nDeath Age Distribution (percentage among deaths under 20):")
print((death_counts / len(df_deaths_under_20) * 100).round(2).astype(str) + '%')


