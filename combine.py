# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 18:34:41 2025

@author: user
"""

import pandas as pd
import numpy as np

# Load datasets
adopted_df = pd.read_excel('D:/User_Data/Downloads/女性及其養兄弟姐妹_cp.xlsx')
blood_df = pd.read_excel('D:/User_Data/Downloads/女性及其兄弟姐妹_cp.xlsx')

# Ensure birthdate columns are in datetime format
adopted_df['birthdate'] = pd.to_datetime(adopted_df['birthdate'], errors='coerce')
adopted_df['adopteddate'] = pd.to_datetime(adopted_df['adopteddate'], errors='coerce')
blood_df['birthdate'] = pd.to_datetime(blood_df['birthdate'], errors='coerce')

# Remove duplicated PIDs within each dataset
adopted_df = adopted_df.drop_duplicates(subset='PID', keep='first')
blood_df = blood_df.drop_duplicates(subset='PID', keep='first')

# Prepare panel data
panel_data = []

def count_siblings(df, pid, birthdate, sex, elder=True):
    siblings = df[df['PID'] == pid]
    if elder:
        siblings = siblings[(pd.to_datetime(siblings['BS_Bdate'], errors='coerce') < birthdate) & (siblings['BS_sex'] == sex)]
    else:
        siblings = siblings[(pd.to_datetime(siblings['BS_Bdate'], errors='coerce') > birthdate) & (siblings['BS_sex'] == sex)]
    return len(siblings)

# Merge and label origin
combined_df = pd.concat([
    adopted_df.assign(adopted_status=1),
    blood_df.assign(adopted_status=0)
])

for _, row in combined_df.iterrows():
    pid = row['PID']
    birthdate = pd.to_datetime(row['birthdate'], errors='coerce')
    adopted_status = row['adopted_status']
    adopted_date = pd.to_datetime(row.get('adopteddate', None), errors='coerce')
    mar_type = row.get('MarType', None)
    death_date = pd.to_datetime(row.get('DeathDate', None), errors='coerce') if adopted_status else pd.to_datetime(row.get('eodate', None), errors='coerce')
    death_code = row.get('eocode', None) if not adopted_status else 2

    original_occu = blood_df[blood_df['PID'] == pid]['Occu'].dropna().iloc[0] if pid in blood_df['PID'].values else None
    adopted_occu = adopted_df[adopted_df['PID'] == pid]['Occu'].dropna().iloc[0] if pid in adopted_df['PID'].values else None

    if pd.notnull(birthdate):
        for year in range(birthdate.year, birthdate.year + 21):
            age = year - birthdate.year
            if age > 20:
                break

            adopted = 1 if adopted_status and pd.notnull(adopted_date) and adopted_date.year <= year else 0

            if adopted == 0 or (adopted_date and year < adopted_date.year):
                sibling_source = blood_df
                occu = original_occu
            else:
                sibling_source = adopted_df
                occu = adopted_occu

            elder_brothers = count_siblings(sibling_source, pid, birthdate, 'M', elder=True)
            younger_brothers = count_siblings(sibling_source, pid, birthdate, 'M', elder=False)
            elder_sisters = count_siblings(sibling_source, pid, birthdate, 'F', elder=True)
            younger_sisters = count_siblings(sibling_source, pid, birthdate, 'F', elder=False)

            previous_sibling = blood_df[(blood_df['PID'] == pid) & (pd.to_datetime(blood_df['BS_Bdate']) < birthdate)].sort_values(by='birthdate').tail(1)
            if not previous_sibling.empty:
                gap = (birthdate - pd.to_datetime(previous_sibling.iloc[0]['BS_Bdate'])).days / 365.25
                log_gap = np.log1p(gap)
                firstborn = 0
            else:
                gap = np.nan
                log_gap = np.nan
                firstborn = 1

            dead = 1 if pd.notnull(death_date) and death_date.year < year and death_code == 2 else 0

            if adopted_status:
                if pd.notnull(adopted_date) and adopted_date.year < year:
                    adil = 1 if mar_type == 3 else 0
                    ad = 1 if mar_type != 3 else 0
                    bd = 0
                else:
                    adil = 0
                    ad = 0
                    bd = 1
            else:
                adil = 0
                ad = 0
                bd = 1

            panel_data.append({
                'PID': pid,
                'Year': year,
                'Age': age,
                'Adopted': adopted,
                'Elder_Brothers': elder_brothers,
                'Younger_Brothers': younger_brothers,
                'Elder_Sisters': elder_sisters,
                'Younger_Sisters': younger_sisters,
                'Birth_Gap': gap,
                'Log_Birth_Gap': log_gap,
                'Firstborn': firstborn,
                'MarType': mar_type,
                'Dead': dead,
                'ADIL': adil,
                'AD': ad,
                'BD': bd,
                'Occu': occu
            })

# Convert to DataFrame
panel_df = pd.DataFrame(panel_data)
panel_df.to_excel('panel_data_output.xlsx', index=False)
print("Panel data constructed.")