import pandas as pd
import numpy as np

# Load raw dataset
df = pd.read_csv("../data/raw/energy_weather_raw_data.csv")

# ---------------------------------------------------------
# Step 1: Convert String Date to Datetime
# ---------------------------------------------------------
df['timestamp'] = pd.to_datetime(df['date'])

# Set the datetime column as the index and sort chronologically
df = df.set_index('timestamp').sort_index()

# ---------------------------------------------------------
# Calculate Active Energy Consumption (kWh)
# ---------------------------------------------------------
# Assuming data is recorded at uniform intervals (e.g., every 15 minutes or every 1 hour)
# Calculate the time interval in hours automatically between consecutive timestamps
time_delta_hours = df.index.to_series().diff().dt.total_seconds() / 3600.0

# Fill the first NaN time delta with the median sampling interval
time_delta_hours.iloc[0] = time_delta_hours.median()

# Calculate Active Power in kWh:
df['active_energy_kwh'] = (df['active_power'] * time_delta_hours) / 1000.0

# ---------------------------------------------------------
# Validation Check (Power Factor)
# ---------------------------------------------------------
# Power Factor (PF) = Active Power / Apparent Power
# A valid Power Factor is always between 0.0 and 1.0
df['power_factor'] = df['active_power'] / df['apparent_power']


# ---------------------------------------------------------
# Aggergation to 1 Hour Windows and Hot-Encode Main Column to remove noise
# ---------------------------------------------------------

# 1. Define custom function to get the mode (most frequent value)
def get_mode(series):
    mode_values = series.mode()
    return mode_values.iloc[0] if not mode_values.empty else None

# 2. Resample raw data to hourly
agg_rules = {
    'active_energy_kwh': 'sum',
    'active_power': 'mean',
    'power_factor': 'mean',
    'temp': 'mean',
    'humidity': 'mean',
    'main': get_mode  
}

df_hourly = df.resample('1h').agg(agg_rules)

# 3. One-hot encode the dominant weather column on the hourly table
df_hourly = pd.get_dummies(df_hourly, columns=['main'], prefix='is', dtype=int)

# Drop remaining missing values (if any whole hours were missing)
df_hourly = df_hourly.dropna(subset=['active_energy_kwh'])

# ---------------------------------------------------------
# Extracting Features 
# ---------------------------------------------------------

# Temporal Featurs for model to learn the daily and weekly patterns


df_hourly['hour'] = df_hourly.index.hour
df_hourly['day_of_week'] = df_hourly.index.dayofweek
df_hourly['month'] = df_hourly.index.month
df_hourly['is_weekend'] = df_hourly['day_of_week'].isin([5, 6]).astype(int)


# Cooling Degree Days Feature to predicting when AC will be turned on

df_hourly['cdd'] = df_hourly['temp'].apply(lambda x: max(0, x - 24.0))

# Lag Features to compare with past data 

# Consumption 1 hour ago
df_hourly['kwh_lag_1h'] = df_hourly['active_energy_kwh'].shift(1)
# Consumption same hour yesterday (24 hours ago)
df_hourly['kwh_lag_24h'] = df_hourly['active_energy_kwh'].shift(24)

# Drop the initial missing rows created by shifting
df_hourly = df_hourly.dropna()

# Save your clean, hourly dataset with all engineered features in real physical units
df_hourly.to_csv('../data/processed/cleaned_hourly_energy_data.csv')

print("Preprocessing complete! Saved to 'cleaned_hourly_energy_data.csv'.")