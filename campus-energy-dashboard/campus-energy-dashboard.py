# Name = Tushar saini
# Roll no. =2501730053

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def load_all_csv(data_dir="data"):
    print("\n=== SCANNING DATA DIRECTORY ===")

    files = list(Path(data_dir).glob("*.csv"))
    
    if len(files) == 0:
        print("\nERROR: No .csv files found in the 'data/' folder!")
        print("Please add files like building1.csv, building2.csv, etc.\n")
        return pd.DataFrame()  

    master_df = pd.DataFrame()

    for file in files:
        try:
            print(f"Loading: {file.name}")
            df = pd.read_csv(file, on_bad_lines='skip')

            if 'timestamp' not in df.columns or 'kwh' not in df.columns:
                print(f"WARNING: {file.name} skipped (missing timestamp or kwh column)")
                continue

            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])

            df['building'] = file.stem
            master_df = pd.concat([master_df, df], ignore_index=True)

        except Exception as e:
            print(f"ERROR reading {file}: {e}")

    print("\nMerged DataFrame Created Successfully!")
    print(master_df.head())
    return master_df



def calculate_daily_totals(df):
    return df.set_index('timestamp').resample('D')['kwh'].sum()

def calculate_weekly_totals(df):
    return df.set_index('timestamp').resample('W')['kwh'].sum()

def building_wise_summary(df):
    return df.groupby('building')['kwh'].agg(['mean', 'min', 'max', 'sum'])



class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        total = self.calculate_total_consumption()
        return f"{self.name}: {total:.2f} kWh"


class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def load_from_dataframe(self, df):
        for _, row in df.iterrows():
            building_name = row['building']

            if building_name not in self.buildings:
                self.buildings[building_name] = Building(building_name)

            reading = MeterReading(row['timestamp'], row['kwh'])
            self.buildings[building_name].add_reading(reading)

    def full_report(self):
        print("\n===== BUILDING ENERGY REPORT =====")
        for building in self.buildings.values():
            print(building.generate_report())


def generate_dashboard(df):
    print("\nGenerating dashboard...")

    plt.figure(figsize=(16, 8))

 
    plt.subplot(1, 3, 1)
    for b in df['building'].unique():
        daily = calculate_daily_totals(df[df['building'] == b])
        plt.plot(daily.index, daily.values, label=b)
    plt.title("Daily Energy Consumption")
    plt.xlabel("Date")
    plt.ylabel("kWh")
    plt.legend()

    plt.subplot(1, 3, 2)
    weekly = df.set_index('timestamp').groupby('building')['kwh'].resample('W').sum().unstack(0)
    weekly_mean = weekly.mean()
    plt.bar(weekly_mean.index, weekly_mean.values)
    plt.title("Weekly Average kWh by Building")
    plt.xlabel("Building")
    plt.ylabel("Average kWh")

    plt.subplot(1, 3, 3)
    plt.scatter(df['timestamp'], df['kwh'], s=10)
    plt.title("Peak Load Scatter Plot")
    plt.xlabel("Time")
    plt.ylabel("kWh")

    plt.tight_layout()
    Path("output").mkdir(exist_ok=True)
    plt.savefig("output/dashboard.png")
    plt.close()

    print("Dashboard saved as output/dashboard.png")



def export_outputs(df):
    Path("output").mkdir(exist_ok=True)

    df.to_csv("output/cleaned_energy_data.csv", index=False)
    summary = building_wise_summary(df)
    summary.to_csv("output/building_summary.csv")

    total_consumption = df['kwh'].sum()
    highest_building = summary['sum'].idxmax()
    peak_row = df.loc[df['kwh'].idxmax()]
    peak_time = peak_row['timestamp']

    report_text = f"""
CAMPUS ENERGY SUMMARY REPORT
----------------------------
Total Campus Consumption: {total_consumption:.2f} kWh
Highest Consuming Building: {highest_building}
Peak Load Time: {peak_time}
----------------------------
"""

    with open("output/summary.txt", "w") as f:
        f.write(report_text)

    print("Summary saved as output/summary.txt")



def main():
    df = load_all_csv("data")

    if df.empty:
        print("\nPROGRAM STOPPED: No valid data found.")
        return

    bm = BuildingManager()
    bm.load_from_dataframe(df)
    bm.full_report()

    generate_dashboard(df)
    export_outputs(df)

    print("\nAll tasks completed successfully!")


if __name__ == "__main__":
    main()
