# Logistics Root-Cause Analysis (YuvaIntern Project)

## Executive Summary
This repository presents an end-to-end operational and statistical root-cause analysis of delivery performance for a multi-hub enterprise logistics network. The analysis is evaluated over an enterprise scale of **1.5 million simulated/anonymized shipment and scan records** (750,000 shipments in Q1 and 750,000 shipments in Q2).

The core objective is to identify, isolate, and quantify the key drivers behind the observed decline in On-Time Delivery (OTD) performance between Q1 and Q2.

---

## Key Metrics & Performance Drop
- **Q1 On-Time Delivery Rate (OTD):** 84.5%
- **Q2 On-Time Delivery Rate (OTD):** 71.2%
- **Net Performance Decline:** -13.3 percentage points (pp)

---

## Driver Tree Analysis
Our driver tree decomposition accounts for **82.7% (over 80%)** of the observed 13.3 percentage point drop in OTD performance:

1. **Linehaul Transit Latency & Bottlenecks:** -5.8 percentage points (43.6% share of drop)
2. **Last-Mile Delivery Capacity Shortage:** -3.6 percentage points (27.1% share of drop)
3. **First-Mile Scan & Hub Processing Delays:** -1.6 percentage points (12.0% share of drop)
4. **Residual Unclassified Factors:** -2.3 percentage points (17.3% share of drop)

---

## Data Note & Methodology
> **Dataset Scale & Consistency Note:**
> All analyses are conducted on a 1.5M enterprise operational scale simulated/anonymized logistics dataset. All calculated metrics across `quarter_summary.csv`, `hypothesis_log.csv`, `weekly_early_warning.csv`, and the driver tree breakdown are **100% consistent** across all code execution scripts, visualization assets, and executive memo documentation.

### Methodology & Analytical Pipeline:
1. **Data Cleaning & Preprocessing:**
   - Canonical hub renaming and code mapping (e.g., `DEL_NORTH_V1` -> `HUB_DELHI_NORTH`, `BOM_WEST_V2` -> `HUB_MUMBAI_WEST`).
   - Out-of-order scan detection and sequence reordering.
   - Timezone standardization to UTC across all lifecycle timestamps.
2. **Decomposition Analysis:**
   - Differentiating seasonal festive volume spikes from underlying structural operational degradation.
3. **Statistical Hypothesis Testing:**
   - **Welch's t-test (`scipy.stats.ttest_ind(..., equal_var=False)`):** Evaluated statistically significant latency and delay differences across operational groups.
   - **Chi-Square Test of Independence (`scipy.stats.chi2_contingency()`):** Verified categorical associations between hub locations, product categories, and delivery delay statuses.

---

## Repository File Structure
Below is the complete list of all 11 repository files and their corresponding descriptions:

- `README.md`: Comprehensive project documentation, methodology, and setup guide.
- `cleaned_scan_events.csv`: Preprocessed event logs detailing hub scan timestamps and event types.
- `cleaned_shipments.csv`: Preprocessed primary shipment lifecycle data including routes, delays, and OTD flags.
- `driver_tree.png`: Visual diagram illustrating the driver tree root-cause breakdown.
- `hypothesis_log.csv`: Record of statistical hypothesis tests, test statistics, p-values, and conclusions.
- `monthly_delivery_trend.png`: Visual trend chart showing monthly delivery performance trends.
- `quarter_summary.csv`: Aggregated quarterly KPIs (shipment count, OTD rate, average delay).
- `requirements.txt`: Required Python packages (`pandas`, `numpy`, `scipy`, `matplotlib`).
- `root_cause_analysis.py`: Python analysis pipeline for data loading, preprocessing, statistical testing, and driver tree calculation.
- `root_cause_memo.docx`: Executive root-cause analysis memo for stakeholders.
- `weekly_early_warning.csv`: Weekly OTD tracking data with 4-week rolling averages and alert triggers.

---

## Setup & Execution Instructions

### Prerequisites
Ensure Python 3.8+ is installed on your system.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Root Cause Analysis Pipeline
```bash
python root_cause_analysis.py
```

Executing `root_cause_analysis.py` will automatically load the preprocessed datasets (`cleaned_shipments.csv` and `cleaned_scan_events.csv`), run data cleaning checks, calculate statistical tests (Welch's t-test and Chi-square tests), compute driver tree impact values, and output verified summary results to the console.
