# Name =Tushar saini
#Roll no.=2501730053

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DATA_FILE = "weather.csv"   
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def make_sample_weather_csv(path=DATA_FILE):
    """Create a small sample weather.csv so the script can run immediately."""
    print(f"Creating sample dataset at '{path}' (because it was missing).")
    times = pd.date_range(start="2024-01-01", periods=24, freq="H")
    temp = 15 + 8 * np.sin(np.linspace(0, 2*np.pi, 24)) + np.random.normal(0, 0.5, 24)
    humidity = 60 + 20 * np.cos(np.linspace(0, 2*np.pi, 24)) + np.random.normal(0, 3, 24)
    rainfall = np.clip(np.random.choice([0,0,0,0.5,1,2,5], size=24, p=[0.6,0.15,0.1,0.05,0.04,0.03,0.03]), 0, None)

    df = pd.DataFrame({
        "date": times,
        "temperature": np.round(temp, 2),
        "humidity": np.round(humidity, 1),
        "rainfall": np.round(rainfall, 2)
    })
    df.to_csv(path, index=False)
    print("Sample CSV created.\n")

def load_dataset(filename=DATA_FILE):
    """Load CSV; if missing, create a sample then load."""
    if not Path(filename).exists():
        make_sample_weather_csv(filename)

    try:
        df = pd.read_csv(filename)
    except Exception as e:
        raise RuntimeError(f"Failed to read '{filename}': {e}")

    rename_map = {}
    cols = [c.lower() for c in df.columns]
    if "date" not in cols and "timestamp" in cols:
        rename_map[next(c for c in df.columns if c.lower()=="timestamp")] = "date"
    if "temperature" not in cols:
        for alt in ["temp","t"]:
            if alt in cols:
                rename_map[next(c for c in df.columns if c.lower()==alt)] = "temperature"
                break
    if "humidity" not in cols:
        for alt in ["hum"]:
            if alt in cols:
                rename_map[next(c for c in df.columns if c.lower()==alt)] = "humidity"
                break
    if "rainfall" not in cols:
        for alt in ["rain","precipitation","precip"]:
            if alt in cols:
                rename_map[next(c for c in df.columns if c.lower()==alt)] = "rainfall"
                break

    if rename_map:
        df = df.rename(columns=rename_map)

    required = {"date", "temperature", "humidity", "rainfall"}
    missing = required - set(c.lower() for c in df.columns)
    if missing:
        raise RuntimeError(f"Dataset missing required columns: {missing}")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).copy()

    for col in ['temperature', 'humidity', 'rainfall']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    num_cols = ['temperature', 'humidity', 'rainfall']
    for c in num_cols:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].mean())

    return df

def analyze_and_plot(df):
    print("\nData summary:")
    print(df[['temperature','humidity','rainfall']].describe())

    df['month'] = df['date'].dt.month

    monthly_mean_temp = df.groupby('month')['temperature'].mean()
    monthly_rainfall = df.groupby('month')['rainfall'].sum()

    print("\nMonthly mean temperature:\n", monthly_mean_temp)
    print("\nMonthly rainfall totals:\n", monthly_rainfall)

    plt.figure(figsize=(10,4))
    plt.plot(df['date'], df['temperature'], marker='o', linewidth=1)
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Daily Temperature Trend')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "daily_temperature.png")
    plt.close()

    plt.figure(figsize=(8,4))
    monthly_rainfall.plot(kind='bar')
    plt.xlabel('Month')
    plt.ylabel('Rainfall (units)')
    plt.title('Monthly Rainfall Total')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_rainfall.png")
    plt.close()

    plt.figure(figsize=(6,4))
    plt.scatter(df['temperature'], df['humidity'])
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Humidity (%)')
    plt.title('Humidity vs Temperature')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "humidity_vs_temperature.png")
    plt.close()

    fig, axes = plt.subplots(1,2,figsize=(12,4))
    axes[0].plot(df['date'], df['temperature'])
    axes[0].set_title('Daily Temperature')
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('°C')

    axes[1].scatter(df['temperature'], df['humidity'])
    axes[1].set_title('Humidity vs Temperature')
    axes[1].set_xlabel('Temperature (°C)')
    axes[1].set_ylabel('Humidity (%)')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "combined_plots.png")
    plt.close()

    df.to_csv(OUTPUT_DIR / "cleaned_weather.csv", index=False)
    print(f"\nSaved plots and cleaned CSV into '{OUTPUT_DIR.resolve()}'")

def main():
    print("Starting weather data visualizer...")
    try:
        df = load_dataset(DATA_FILE)
    except RuntimeError as e:
        print("ERROR loading dataset:", e)
        return

    analyze_and_plot(df)
    print("\nDone. Check the 'output' folder for results.")

if __name__ == "__main__":
    main()
