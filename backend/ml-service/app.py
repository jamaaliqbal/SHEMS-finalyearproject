from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from django.conf import settings

import joblib

# Load the trained models at startup so they can be used for predictions
energy_model = tf.keras.models.load_model("lstm_energy_model.h5")
# solar_model = tf.keras.models.load_model("lstm_solar_model.h5")

app = Flask(__name__)
CORS(app)

# ---- SOLAR PREDICTION MODEL TRAINING --------------------------------- #
SOLAX_API_URL="https://www.eu.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do"
SOLAX_API_TOKEN=settings.SOLAX_API_TOKEN
SOLAX_WIFI_SNS="SV8RYX9GZU"


WEATHER_API_KEY=settings.WEATHER_API_KEY
WEATHER_API_URL="https://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_API_URL="https://api.openweathermap.org/data/2.5/forecast"
LATITUDE = "51.32021"
LONGITUDE = "-0.13261"

# API URLs for Django backend
SOLAR_DATA_API = "http://127.0.0.1:8000/api/solar-data/"
WEATHER_DATA_API = "http://127.0.0.1:8000/api/weather-data/"
SYNTHETIC_SOLAR_DATA_API="http://127.0.0.1:8000/api/synthetic-solar-data/"

# Fetch Solar data from SOLAX API
def fetch_solar_data():
    response = requests.get(SYNTHETIC_SOLAR_DATA_API)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()
    # try: 
    #     response = requests.get(SOLAX_API_URL, params= {"tokenId": SOLAX_API_TOKEN, "sn": SOLAX_WIFI_SNS})
    #     print(f"DEBUG: solar data response: {response}" )
    #     data = response.json()
    #     print(f"DEBUG: solar data : {data}" )
    #     if response.status_code == 200:
    #         # return {
    #         #     "solar_power": data["result"]["acpower"],  # Current solar power (kW)
    #         #     "battery_power": data["result"]["yieldtoday"],  # Daily yield (kWh)
    #         #     "battery_percentage": data["result"]["soc"],  # Battery state of charge (%)
    #         #     "total_yield": data["result"]["yieldtotal"]  # Total solar energy (kWh)
    #         # }
    #         return data
    #     else:
    #         print("Error fetching solar data:", response.status_code)
    #         return []
    # except Exception as e:
    #     print("Error fetching solar data:", str(e))
    #     return None


# Fetch weather data from OpenWeatherMap API
def fetch_weather_data():
    response = requests.get(WEATHER_DATA_API)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()
    # try:
    #     response = requests.get(WEATHER_API_URL, params={
    #         "appid": WEATHER_API_KEY,
    #         "lat": LATITUDE,
    #         "lon": LONGITUDE,
    #         "units": "metric",
    #         "exclude": "minutely,hourly,alerts"
    #     })
    #     if response.status_code == 200:
    #         data = response.json()
    #         print(f"DEBUG: Weather data: {data}")
    #         return data     
    #         # return {
    #         #     "temperature": data["current"]["temp"],  # Temperature in °C
    #         #     "cloud_cover": data["current"]["clouds"] / 100,  # Cloud coverage (normalized)
    #         #     "sunlight_hours": data["daily"][0]["uvi"],  # UV index (proxy for sunlight hours)
    #         #     "humidity": data["current"]["humidity"] / 100  # Humidity (normalized)
    #         # }
    # except Exception as e:
    #     print("Error fetching weather data:", str(e))
    #     return None

# def load_historical_data():
#     solar_data = fetch_solar_data()
#     weather_data = fetch_weather_data()
#     print(f"DEBUG: loaded solar data: {solar_data}")
#     print(f"DEBUG: loaded weather data: {weather_data}")

#     if not solar_data or not weather_data:
#         print("Error fetching data")  
#         return None
    
#     # Convert to pandas DataFrame
#     df = pd.DataFrame([{
#         "solar_power": solar_data["result"]["acpower"],
#         "temperature": weather_data["main"]["temp"],
#         "cloud_cover": weather_data["current"]["cloud_cover"],
#         "sunlight_hours": weather_data["daily"][0]["uvi"]["sunlight_hours"],
#         "humidity": weather_data["current"]["humidity"]
#     }])

#     return df

# Load the data
solar_df = fetch_solar_data()
print(f"DEBUG: solar data: {solar_df}")
weather_df = fetch_weather_data()
print(f"DEBUG: weather data: {weather_df}")

# Merge solar and weather data on timestamp
solar_df['upload_time'] = pd.to_datetime(solar_df['upload_time'])
weather_df['date_time'] = pd.to_datetime(weather_df['date_time'])
df = pd.merge_asof(solar_df.sort_values('upload_time'), weather_df.sort_values('date_time'), left_on='upload_time', right_on='date_time')

# Select features & target variable
df = df[['ac_power',  'yield_today', 'clouds', 'temperature', 'humidity', 'wind_speed']]
df.dropna(inplace=True)
print(f"DEBUG: merged data frame: {df}")

# Normalize the data
solar_scaler = MinMaxScaler()
df_normalized = solar_scaler.fit_transform(df)

print(f"DEBUG: df_normalized shape: {df_normalized.shape}")
print(f"DEBUG: Total available samples: {len(df_normalized)}")

# Define sequence length for LSTM
seq_length = 48  # Use last 48 hours to predict next solar power
forecast_horizon = 24  # Predict next 24 hours of solar generation

# Create training data
def create_sequences(data, seq_length, forecast_horizon):
    sequences = []
    labels = []
    for i in range(len(data) - seq_length - forecast_horizon + 1):
        seq = data[i:i + seq_length]
        label = data[i + seq_length:i + seq_length + forecast_horizon, 0]
        sequences.append(seq)
        labels.append(label)
    return np.array(sequences), np.array(labels)

# Create sequences and reshape for LSTM input
X, y = create_sequences(df_normalized, seq_length, forecast_horizon)
print(f"DEBUG: X shape: {X.shape}")  # Expected (num_samples, seq_length, num_features)
print(f"DEBUG: y shape: {y.shape}")  # Expected (num_samples, forecast_horizon)

# Check if enough data is created
if X.shape[0] < 2:
    print("❌ ERROR: Not enough training samples. Increase dataset or lower seq_length/forecast_horizon!")
    exit()


#Save scaler for later use
# joblib.dump(solar_scaler, "solar_scaler.pk1")

# Define LSTM model
solar_model = Sequential([
    Input(shape=(seq_length, X.shape[2])),
    LSTM(64, return_sequences=True),
    LSTM(32, return_sequences=False),
    Dense(16, activation='relu'),
    Dense(forecast_horizon) # Predicting next 24 hours solar power
])

# Compile and train the model
print(f"DEBUG: Number of training samples: {X.shape[0]}")
solar_model.compile(loss='mean_squared_error', optimizer='adam')
solar_model.fit(X, y, epochs=100, batch_size=32, validation_split=0.2)

# Save the trained model
solar_model.save("lstm_synthetic_solar_model.h5")

print("Solar Model Training completed & Saved ")

@app.route("/predict-solar", methods=["POST"])
def predict_solar():
    try:
        # Fetch request data
        request_data = request.get_json()

        # Check if fields are provided 
        if "solar_history" not in request_data or "weather_history" not in request_data:
            return jsonify({"error": "Missing solar_history or weather_history field"}), 400
        
        # Extract data 
        solar_history = request_data["solar_history"]
        weather_history = request_data["weather_history"]
        print(f"DEBUG: solar history length : {len(solar_history)}")
        print(f"DEBUG: weather history length : {len(weather_history)}")
        print(f"DEBUG: Type of solar_history[0]: {type(solar_history[0])}")
        print(f"DEBUG: Type of weather_history[0]: {type(weather_history[0])}")

        # Ensure data length matches sequence length
        if len(solar_history) != len(weather_history):
            return jsonify({"error": f"Solar and weather history data lengths do not match: solar={len(solar_history)}, weather={len(weather_history)}"}), 400

        # Extract solar features as lists of numerical values
        ac_power = [entry["ac_power"] for entry in request_data["solar_history"]]
        # battery_power = [entry["battery_power"] for entry in request_data["solar_history"]]
        # battery_soc = [entry["battery_soc"] for entry in request_data["solar_history"]]
        # pv1_power = [entry["pv1_power"] for entry in request_data["solar_history"]]
        # pv2_power = [entry["pv2_power"] for entry in request_data["solar_history"]]
        yield_today = [entry["yield_today"] for entry in request_data["solar_history"]]

        # Extract numerical values from weather_history
        temperature = [entry["temperature"] for entry in weather_history]
        humidity = [entry["humidity"] for entry in weather_history]
        wind_speed = [entry["wind_speed"] for entry in weather_history]
        clouds = [entry["clouds"] for entry in weather_history]

        # Ensure data length matches sequence length
        if len(solar_history) < seq_length:
            return jsonify({"error": f"Insufficient data. Expected at least {seq_length} values but got {len(solar_history)}"}), 400

        # Create the input array by combining all extracted values
        input_data = np.column_stack([
            ac_power[-seq_length:], 
            # battery_power[-seq_length:], battery_soc[-seq_length:],
            # pv1_power[-seq_length:], pv2_power[-seq_length:],
            yield_today[-seq_length:],
            temperature[-seq_length:], humidity[-seq_length:], wind_speed[-seq_length:], clouds[-seq_length:]
        ])
        print(f"DEBUG: Input data shape: {input_data.shape}")

        if not hasattr(solar_scaler, "scale_"): 
            print("Fitting scaler as it was not preloaded...")
            solar_scaler.fit(np.array(solar_history).reshape(-1, 1))

        # Convert to NumPy and normalize
        # input_data = np.column_stack([solar_history[-seq_length:], weather_history[-seq_length:]]) 
        normalized_input = solar_scaler.transform(input_data)
        input_sequence = normalized_input.reshape(1, seq_length, X.shape[2])

        solar_prediction = solar_model.predict(input_sequence)

        # Only inverse transform the predicted `ac_power` column
        # predicted_solar = solar_scaler.inverse_transform(
        #     np.concatenate([solar_prediction.reshape(-1,1), np.zeros((24, 9))], axis=1)
        # )[:, 0]  # Extract only first column (ac_power)
        if solar_prediction.shape[1] == 1:
            predicted_solar = solar_scaler.inverse_transform(solar_prediction)
        else:
            padded_prediction = np.concatenate([solar_prediction.reshape(24, 1), np.zeros((24,5))], axis=1)
            predicted_solar = solar_scaler.inverse_transform(padded_prediction)[:, 0]  # Extract only first column (ac_power)
        
        predicted_solar = predicted_solar.flatten().tolist()
        return jsonify({"solar_prediction": predicted_solar}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- ENERGY PREDICTION MODEL TRAINING -------------------------------- # 
# def fetch_energy_data():
#     API_URL = 'http://127.0.0.1:8000/api/hourly-data/'
#     try:
#         response = requests.get(API_URL)
#         print(f"DEBUG: response: {response}" )
#         if response.status_code == 200:
#             data = response.json()
#             print(f"DEBUG: data legnth: {len(data)}" )
#             return data
#         else:
#             print("Error fetching data:", response.status_code)
#             return []
#     except Exception as e:
#         print("Error:", str(e))
#         return []

# data = fetch_energy_data()

# if data:
#     df = pd.DataFrame(data)

#     # Convert timestamps to datetime format and sort by start time
#     df['interval_start'] = pd.to_datetime(df['interval_start'])
#     # df['interval_start'] = df['interval_start'].astype(int) / 10**9 
#     # df['interval_start'] = df['interval_start'] - df['interval_start'].min()

#     df['interval_end'] = pd.to_datetime(df['interval_end'])
#     # df['interval_end'] = df['interval_end'].astype(int) / 10**9 

#     # Adding time features to dataframe
#     df['hour'] = df['interval_start'].dt.hour / 23.0   # Normalize hour (0-23)
#     df['day'] = df['interval_start'].dt.weekday / 6.0  # Normalize weekday (0-6)
#     df['month'] = df['interval_start'].dt.month / 12.0  # Normalize month (1-12)

#     # Select relevant columns and sort by start time
#     df = df[['interval_start', 'consumption', 'hour', 'day', 'month']]
#     # df = df.sort_values(by="interval_start")

#     # df['timestamp'] = df['interval_start'].astype(int) / 10**9

#     # Normalize the data to values between 0 and 1
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     df['consumption'] = scaler.fit_transform(df[['consumption']])

#     # Drop original timestamp column
#     df.drop(columns=['interval_start'], inplace=True)

# # Function to create sequences for next 7 days
# def create_seqeunces(data, seq_length, forecast_horizon):
#     sequences = []
#     labels = []
#     for i in range(len(data) - seq_length - forecast_horizon + 1):
#         seq = data.iloc[i:i + seq_length].values
#         label = data.iloc[i + seq_length:i + seq_length + forecast_horizon]['consumption'].values 
#         sequences.append(seq)
#         labels.append(label)
#     return np.array(sequences), np.array(labels)

# # Sequence length to define window size of data to use for prediction. MODIFY THIS TO INCREASE DAYS
# seq_length = 168 # Use past 7 days (7*24)
# forecast_horizon = 168 # Predict next 7 days

# # Create sequences, where y is the actual consumption value for the next hour
# X, y = create_seqeunces(df, seq_length, forecast_horizon)

# # Reshape data for LSTM [samples, time steps, features]
# X = X.reshape(X.shape[0], X.shape[1], X.shape[2])

# # Print data shape
# print("Shape of X:", X.shape)
# print("Shape of y:", y.shape)

# # Define LSTM model
# model = Sequential([
#     LSTM(64, return_sequences=True, input_shape=(seq_length, X.shape[2])), # First layer with 64 neurons
#     LSTM(32, return_sequences=False), # Second layer with 64 neurons
#     Dense(16, activation='relu'), # Dense layer with 32 neurons
#     Dense(forecast_horizon) # Output layer predicting next 168 hours usage
# ])

# # Compile the model
# model.compile(loss='mean_squared_error', optimizer='adam')

# # Train the model
# model.fit(X, y,  epochs=50, batch_size=64, validation_split=0.2)

# # Save the model
# model.save('lstm_energy_model.h5')

# # Load the trained model
# model = tf.keras.models.load_model("lstm_energy_model.h5")

# # Predict energy consumption for the next time step
# predicted_consumption = model.predict(X[-1].reshape(1, seq_length, 1))

# # Inverse transform the value
# predicted_kWh = scaler.inverse_transform(predicted_consumption)

# print("Predicted Energy Consumption:", predicted_kWh[0][0], "kWh")

# ----------------------------------------------------------------
# Load trained energy model
energy_model = tf.keras.models.load_model("lstm_energy_model.h5")

# Define sequence length and feature count for energy model
seq_length_energy = 144 # temporarily set to 144 (6 days) for testing
feature_count_energy = 4 

# Load trained scaler (if saved during training)
try:
    scaler = joblib.load("scaler.pkl")  # Load pre-trained MinMaxScaler
except:
    scaler = MinMaxScaler(feature_range=(0,1))

# Load the scaler
# scaler = MinMaxScaler(feature_range=(0,1))

# Function to preprocess input data for energy model
@app.route('/predict-energy', methods=['POST'])
def predict_energy():
    try: 
        json_data = request.get_json()
        print(f"DEBUG: Recieved data : {json_data}")
        print("DEBUG payload keys:", list(json_data.keys()))
        print("DEBUG lengths:", {
            "consumption": len(json_data.get("consumption_history", [])),
            "hour": len(json_data.get("hour", [])),
            "day": len(json_data.get("day", [])),
            "month": len(json_data.get("month", [])),
        })
        # input_time = pd.to_datetime(json_data['interval_start'])

        # Check if `consumption_history` is provided in the request
        if "consumption_history" not in json_data:
            return jsonify({"error": "Missing 'consumption_history' field. Please provide the last 24 hours of consumption data."}), 400
        
        # Extract the last `seq_length` values from the request
        consumption_history = json_data["consumption_history"]
        hour_history = json_data["hour"]
        day_history = json_data["day"]
        month_history = json_data["month"]

        # Ensure the correct length
        if len(consumption_history) < seq_length_energy:
            return jsonify({"error": f"Insufficient data. Expected at least {seq_length_energy} values but got {len(consumption_history)}"}), 400

        # Fit the scaler if it wasn't loaded
        if not hasattr(scaler, "scale_"):
            print("Fitting scaler as it was not preloaded...")
            scaler.fit(np.array(consumption_history).reshape(-1, 1))
        
        # Convert to a NumPy array and reshape for LSTM model, and normalise data
        normalized_input = scaler.transform(np.array(consumption_history[-seq_length_energy:]).reshape(-1, 1))
        input_sequence = np.column_stack([normalized_input, hour_history[-seq_length_energy:], day_history[-seq_length_energy:], month_history[-seq_length_energy:]])

        # Reshape for LSTM model
        input_sequence = input_sequence.reshape(1, seq_length_energy, feature_count_energy)

        # input_time = pd.DataFrame({"interval_start": [int(input_time.timestamp())]}) 
        # print(f"DEBUG: converteed input time: {input_time}")

        prediction = energy_model.predict(input_sequence)

        # Inverse transform the prediction to get the actual kWh value
        # predicted_kWh = scaler.inverse_transform(prediction)
        # predicted_kWh_value = float(predicted_kWh[0][0])
        predicted_kWh_value = scaler.inverse_transform(prediction.reshape(-1, 1)).flatten().tolist()
        print(f"DEBUG: Predicted energy consumption: {predicted_kWh_value} kWh")

        return jsonify({'predicted_energy_usage': predicted_kWh_value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)



# # Plot training data
# plt.figure(figsize=(10, 6))
# sns.scatterplot(x=df['interval_start'], y=df['consumption'], color='blue', label='Actual Data')
# plt.xlabel("Time (Unix Timestamp)")
# plt.ylabel("Energy Consumption (kWh)")
# plt.title("Energy Consumption vs. Time")
# plt.legend()
# plt.show()

# # Make predictions on the training data
# df['predicted_consumption'] = model.predict(df[['interval_start']])

# # # Plot actual vs. predicted values
# # plt.figure(figsize=(10, 6))
# # sns.scatterplot(x=df['interval_start'], y=df['consumption'], color='blue', label='Actual Data')
# # sns.lineplot(x=df['interval_start'], y=df['predicted_consumption'], color='red', label='Predicted Values')
# # plt.xlabel("Time (Unix Timestamp)")
# # plt.ylabel("Energy Consumption (kWh)")
# # plt.title("Actual vs Predicted Energy Consumption")
# # plt.legend()
# # plt.show()

# df['datetime'] = pd.to_datetime(df['interval_start'], unit='s')

# plt.figure(figsize=(10, 6))
# sns.scatterplot(x=df['datetime'], y=df['consumption'], color='blue', label='Actual Data')
# sns.lineplot(x=df['datetime'], y=df['predicted_consumption'], color='red', label='Predicted Values')

# plt.xlabel("Time")
# plt.ylabel("Energy Consumption (kWh)")
# plt.title("Actual vs Predicted Energy Consumption")

# # Format x-axis as readable dates
# plt.xticks(rotation=45)
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
# plt.legend()
# plt.show()
