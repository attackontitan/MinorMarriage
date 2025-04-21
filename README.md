# Adoption and Mortality Analysis in Historical Taiwan

This repository contains three core Python scripts used for analyzing adoption patterns, sibling structures, and mortality outcomes of girls during the Japanese colonial period in Taiwan. The study combines historical microdata and econometric modeling to examine the effects of adoption and marriage type on child mortality.

## Repository Structure

### 1. `combine.py`
This script builds a **panel dataset** by merging and transforming two original datasets:
- Girls and their **biological siblings**
- Girls and their **adoptive siblings**

Key processing steps:
- Cleans and standardizes date fields.
- Removes duplicate individuals.
- Constructs year-by-year records for each girl up to age 20.
- Generates key indicators:
  - Adoption status (`AD`, `ADIL`, `BD`)
  - Mortality (`Dead`)
  - Sibling composition (number of elder/younger siblings by sex)
  - Birth gap and log-transformed birth gap
  - Father's occupation
- Saves output to `panel_data_output.xlsx`, used in downstream analysis.

### 2. `datades.py`
This script provides **descriptive statistics** and **visualizations** based on the two raw datasets and the generated panel data.

Analyses include:
- Percentage and counts of adopted girls with valid/invalid location data.
- Geographic proximity of adoptive households.
- Proportion of minor marriages (MarType == 3).
- Father's occupation distribution among adoptees.
- Birth order and age-at-death distributions.
- Breakdown of mortality under age 20, by adoption and marriage status.
- Bar charts and histograms for visual insight into trends.

### 3. `model.py`
This script implements a **Difference-in-Differences (DID)** regression to estimate the impact of adoption or minor marriage on mortality risk.

Key features:
- Compares either:
  - Adopted Daughters (AD) vs. Biological Daughters
  - Adopted Daughters-in-Law (ADIL) vs. Biological Daughters
- Constructs treatment and post-treatment indicators using `AdoptYear`.
- Controls for:
  - Sibling composition
  - Age and birth order
  - Year fixed effects
- Outputs OLS regression results with robust standard errors.

## Dependencies

Make sure to install the following Python packages:

```bash
pip install pandas numpy matplotlib seaborn statsmodels openpyxl
