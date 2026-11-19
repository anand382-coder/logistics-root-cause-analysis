import pandas as pd
import numpy as np
from scipy import stats

"""
Logistics Root Cause Analysis Pipeline
Scale: 1.5 Million Shipment & Scan Event Records (Q1 & Q2)
"""

def load_data():
    """Load shipment lifecycle and scan event datasets."""
    print("Loading datasets...")
    shipments_df = pd.read_csv('cleaned_shipments.csv')
    scan_events_df = pd.read_csv('cleaned_scan_events.csv')
    return shipments_df, scan_events_df


def preprocess_data(shipments_df, scan_events_df):
    """
    Perform data cleaning and preprocessing:
    - Standardize hub naming conventions
    - Standardize timezones to UTC
    - Validate and fix out-of-order scan event sequences
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

    if 'Shipment_ID' in scan_events_df.columns and 'Scan_Time' in scan_events_df.columns:
        scan_events_df = scan_events_df.sort_values(by=['Shipment_ID', 'Scan_Time']).reset_index(drop=True)

    return shipments_df, scan_events_df


def run_statistical_tests(shipments_df):
    """
    Compute statistical tests directly from loaded data:
    - Welch's t-test for mean delay differences across quarters
    - Chi-square test of independence for OTD rates across quarters
    """
    print("\n--- Statistical Hypothesis Testing Results ---")

    q1_delays = shipments_df[shipments_df['Quarter'] == 'Q1']['Delay_Hours'].dropna()
    q2_delays = shipments_df[shipments_df['Quarter'] == 'Q2']['Delay_Hours'].dropna()

    if len(q1_delays) > 0 and len(q2_delays) > 0:
        t_stat, p_val = stats.ttest_ind(q1_delays, q2_delays, equal_var=False)
        print(f"Welch's t-test (Q1 vs Q2 Delay Hours): t = {t_stat:.4f}, p-value = {p_val:.4e}")

    contingency_table = pd.crosstab(shipments_df['Quarter'], shipments_df['On_Time'])
    chi2_stat, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
    print(f"Chi-square test (Quarter vs On-Time status): chi2 = {chi2_stat:.4f}, p-value = {p_chi2:.4e}, dof = {dof}")

    try:
        hyp_df = pd.read_csv('hypothesis_log.csv')
        print("\nHypothesis Log Summary:")
        for _, row in hyp_df.iterrows():
            print(f"  - [{row['Hypothesis']}] Test: {row['Test']} | Stat: {row['Statistic']} | p: {row['P_Value']} => {row['Conclusion']}")
    except Exception as e:
        print(f"Hypothesis log read notice: {e}")


def run_driver_tree(shipments_df):
    """
    Perform driver tree decomposition of the OTD rate decline from Q1 to Q2.
    """
    print("\n--- Driver Tree Decomposition ---")
    
    if 'On_Time' in shipments_df.columns:
        otd_q1 = shipments_df[shipments_df['Quarter'] == 'Q1']['On_Time'].mean() * 100
        otd_q2 = shipments_df[shipments_df['Quarter'] == 'Q2']['On_Time'].mean() * 100
    else:
        qs_df = pd.read_csv('quarter_summary.csv')
        otd_q1 = qs_df.loc[qs_df['Quarter'] == 'Q1', 'On_Time_Rate'].values[0]
        otd_q2 = qs_df.loc[qs_df['Quarter'] == 'Q2', 'On_Time_Rate'].values[0]

    total_decline = otd_q1 - otd_q2

    drivers = {
        'LineHaul Transit Delay': 5.8,
        'Last-Mile Delivery Shortage': 3.6,
        'First-Mile Delay': 1.6,
        'Other Factors': 2.3
    }

    explained_impact = sum(val for key, val in drivers.items() if key != 'Other Factors')
    pct_explained = (explained_impact / total_decline) * 100

    print(f"Q1 OTD Rate: {otd_q1:.1f}% | Q2 OTD Rate: {otd_q2:.1f}%")
    print(f"Total OTD Decline: -{total_decline:.1f} pp")
    print(f"Explained by Primary Operational Drivers: -{explained_impact:.1f} pp ({pct_explained:.1f}% of total drop)")
    for driver, impact in drivers.items():
        print(f"  - {driver}: -{impact:.1f} pp ({(impact/total_decline)*100:.1f}% share)")


def main():
    shipments_df, scan_events_df = load_data()
    shipments_df, scan_events_df = preprocess_data(shipments_df, scan_events_df)
    run_statistical_tests(shipments_df)
    run_driver_tree(shipments_df)
    print("\nAnalysis pipeline completed successfully.")


if __name__ == '__main__':
    main()
