import pandas as pd
import numpy as np
from scipy import stats

"""
Logistics Root Cause Analysis Pipeline
Scale: Simulated Shipment & Scan Event Records (Q1 & Q2)
"""

def load_data():
    """Load shipment lifecycle and scan event datasets."""
    print("Loading datasets...")
    shipments_df = pd.read_csv('cleaned_shipments.csv')
    scan_events_df = pd.read_csv('cleaned_scan_events.csv')
    return shipments_df, scan_events_df


def preprocess_data(shipments_df, scan_events_df):
    """
    Standardize hub names, convert timestamps to UTC, and sort out-of-order scans.
    """
    print("Preprocessing shipments and scan events...")
    
    hub_rename_map = {
        'DEL_NORTH_V1': 'HUB_DELHI_NORTH',
        'BOM_WEST_V2': 'HUB_MUMBAI_WEST'
    }
    if 'Origin_Hub' in shipments_df.columns:
        shipments_df['Origin_Hub'] = shipments_df['Origin_Hub'].replace(hub_rename_map)
    if 'Scan_Hub' in scan_events_df.columns:
        scan_events_df['Scan_Hub'] = scan_events_df['Scan_Hub'].replace(hub_rename_map)

    for date_col in ['Shipment_Date', 'Expected_Delivery', 'Actual_Delivery']:
        if date_col in shipments_df.columns:
            shipments_df[date_col] = pd.to_datetime(shipments_df[date_col], utc=True)
            
    if 'Scan_Time' in scan_events_df.columns:
        scan_events_df['Scan_Time'] = pd.to_datetime(scan_events_df['Scan_Time'], utc=True)

    # Fix out-of-order scans
    if 'Shipment_ID' in scan_events_df.columns and 'Scan_Time' in scan_events_df.columns:
        scan_events_df = scan_events_df.sort_values(by=['Shipment_ID', 'Scan_Time']).reset_index(drop=True)

    # Ensure On_Time boolean column exists
    if 'On_Time' not in shipments_df.columns and {'Actual_Delivery', 'Expected_Delivery'}.issubset(shipments_df.columns):
        shipments_df['On_Time'] = shipments_df['Actual_Delivery'] <= shipments_df['Expected_Delivery']

    return shipments_df, scan_events_df


def run_statistical_tests(shipments_df):
    """
    Compute statistical tests directly from data with effect sizes (Cohen's d & Cramer's V)
    and save results to hypothesis_log.csv.
    """
    print("\n--- Statistical Hypothesis Testing Results ---")
    log_rows = []

    # 1. Welch's t-test + Cohen's d (Q1 vs Q2 Delay Hours)
    q1_delays = shipments_df[shipments_df['Quarter'] == 'Q1']['Delay_Hours'].dropna()
    q2_delays = shipments_df[shipments_df['Quarter'] == 'Q2']['Delay_Hours'].dropna()

    if len(q1_delays) > 0 and len(q2_delays) > 0:
        t_stat, p_val = stats.ttest_ind(q1_delays, q2_delays, equal_var=False)
        # Cohen's d calculation
        pooled_sd = np.sqrt((q1_delays.var(ddof=1) + q2_delays.var(ddof=1)) / 2)
        cohens_d = (q2_delays.mean() - q1_delays.mean()) / pooled_sd if pooled_sd > 0 else 0.0
        
        print(f"Welch's t-test (Q1 vs Q2 Delay): t = {t_stat:.4f}, p = {p_val:.4e}, Cohen's d = {cohens_d:.4f}")
        log_rows.append({
            'Hypothesis': 'Q1 vs Q2 Transit Delay Difference',
            'Test': "Welch's t-test",
            'Statistic': round(t_stat, 4),
            'P_Value': f"{p_val:.4e}",
            'Effect_Size': f"Cohen's d = {cohens_d:.4f}",
            'Conclusion': 'Significant increase in Q2 delay' if p_val < 0.05 else 'No significant difference'
        })

    # 2. Chi-square test + Cramer's V (Hub Location vs Delayed Status)
    if 'Origin_Hub' in shipments_df.columns and 'On_Time' in shipments_df.columns:
        contingency_table = pd.crosstab(shipments_df['Origin_Hub'], ~shipments_df['On_Time'])
        chi2_stat, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
        
        # Cramer's V calculation
        n_total = contingency_table.values.sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2_stat / (n_total * min_dim)) if (n_total * min_dim) > 0 else 0.0
        
        print(f"Chi-square (Hub vs Late Status): chi2 = {chi2_stat:.4f}, p = {p_chi2:.4e}, Cramer's V = {cramers_v:.4f}")
        log_rows.append({
            'Hypothesis': 'Origin Hub vs Late Delivery Status',
            'Test': 'Chi-Square Test',
            'Statistic': round(chi2_stat, 4),
            'P_Value': f"{p_chi2:.4e}",
            'Effect_Size': f"Cramer's V = {cramers_v:.4f}",
            'Conclusion': 'Late status depends on Hub' if p_chi2 < 0.05 else 'Independent'
        })

    # Save real computed results to CSV
    if log_rows:
        pd.DataFrame(log_rows).to_csv('hypothesis_log.csv', index=False)
        print("Saved updated statistical results to 'hypothesis_log.csv'.")


def run_driver_tree(shipments_df):
    """
    Compute driver tree decomposition directly from shipment-level stage delays.
    """
    print("\n--- Driver Tree Decomposition ---")
    
    # Calculate Q1 & Q2 OTD directly from data
    otd_series = shipments_df.groupby('Quarter')['On_Time'].mean() * 100
    otd_q1 = otd_series.get('Q1', 0.0)
    otd_q2 = otd_series.get('Q2', 0.0)
    total_decline = otd_q1 - otd_q2

    # Save quarter_summary.csv from real data
    summary_df = shipments_df.groupby('Quarter').agg(
        Total_Shipments=('On_Time', 'count'),
        On_Time_Rate=('On_Time', lambda x: round(x.mean() * 100, 2)),
        Avg_Delay_Hours=('Delay_Hours', lambda x: round(x.mean(), 2))
    ).reset_index()
    summary_df.to_csv('quarter_summary.csv', index=False)

    print(f"Q1 OTD Rate: {otd_q1:.2f}% | Q2 OTD Rate: {otd_q2:.2f}%")
    print(f"Total OTD Decline: -{total_decline:.2f} pp")

    # Stage delay columns (Update these names if your CSV uses slightly different column names)
    stage_cols = ['First_Mile_Delay', 'Linehaul_Delay', 'Last_Mile_Delay']
    available_stages = [col for col in stage_cols if col in shipments_df.columns]

    if available_stages and total_decline > 0:
        late_df = shipments_df[~shipments_df['On_Time']].copy()
        # Attribute each late shipment to the stage with maximum delay (or 'Other Factors' if all <= 0)
        max_delay = late_df[available_stages].max(axis=1)
        late_df['Primary_Driver'] = np.where(
            max_delay > 0,
            late_df[available_stages].idxmax(axis=1),
            'Other_Factors'
        )

        total_per_q = shipments_df.groupby('Quarter').size()
        driver_counts = late_df.groupby(['Quarter', 'Primary_Driver']).size().unstack(fill_value=0)
        driver_share_pct = driver_counts.div(total_per_q, axis=0) * 100

        # Contribution in percentage points (Q2 late share - Q1 late share)
        contrib_pp = driver_share_pct.loc['Q2'] - driver_share_pct.loc['Q1']
        
        explained_pp = contrib_pp.drop('Other_Factors', errors='ignore').sum()
        pct_explained = (explained_pp / total_decline) * 100

        print(f"Explained by Primary Operational Drivers: -{explained_pp:.2f} pp ({pct_explained:.1f}% of total drop)")
        for driver, impact in contrib_pp.items():
            share_of_drop = (impact / total_decline) * 100
            print(f"  - {driver}: -{impact:.2f} pp ({share_of_drop:.1f}% share)")
    else:
        print("Notice: Stage delay columns not found in CSV. Check column names in cleaned_shipments.csv.")


def main():
    shipments_df, scan_events_df = load_data()
    shipments_df, scan_events_df = preprocess_data(shipments_df, scan_events_df)
    run_statistical_tests(shipments_df)
    run_driver_tree(shipments_df)
    print("\nAnalysis pipeline completed successfully.")


if __name__ == '__main__':
    main()
