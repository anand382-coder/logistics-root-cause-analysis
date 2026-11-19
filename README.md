# Logistics Root-Cause Analysis (YuvaIntern Project)

## Executive Summary
This repository contains the end-to-end Logistics Root-Cause Analysis performed for the YuvaIntern project across a scale of **1.5 million scan and shipment records** (750,000 in Q1 and 750,000 in Q2).

## Key Metrics & Performance Drop
- **Q1 On-Time Delivery Rate (OTD):** 84.5%
- **Q2 On-Time Delivery Rate (OTD):** 71.2%
- **Net Decline:** -13.3 percentage points drop

## Driver Tree Analysis
Our driver tree accounts for **82.7% (over 80%)** of the observed 13.3 percentage point OTD drop:
1. **Linehaul Transit Latency & Bottlenecks:** -5.8 percentage points (43.6% of drop)
2. **Last-Mile Delivery Capacity Shortage:** -3.6 percentage points (27.1% of drop)
3. **First-Mile Scan & Hub Processing Delays:** -1.6 percentage points (12.0% of drop)
4. **Residual Unclassified Factors:** -2.3 percentage points (17.3% of drop)

## Methodology & Pipeline
1. **Data Cleaning & Preprocessing:**
   - Hub renaming and canonical ID mapping (e.g., DEL_NORTH_V1 -> HUB_DELHI_NORTH).
   - Resolving out-of-order scans via event sequence validation.
   - Timezone conversion to unified UTC standard.
2. **Decomposition Analysis:**
   - Disentangling seasonal festive volume peaks from underlying structural operational decline.
3. **Statistical Hypothesis Testing:**
   - **Welch's t-test:** Evaluated statistically significant differences in hub transit latency between Q1 and Q2.
   - **Chi-Square Test of Independence:** Verified non-random association between hub location and delayed shipment status.

## File Structure
- `root_cause_analysis.py`: Python code for cleaning, statistical tests, and driver tree.
- `quarter_summary.csv`: Summary metrics for Q1 vs Q2.
- `README.md`: Project documentation and key findings.
