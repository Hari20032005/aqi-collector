import os
import requests
import pandas as pd
from datetime import datetime
import time
import logging
from pathlib import Path
import json

class GitHubAQICollector:
    def __init__(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # Get API key and Power BI Push URL from environment variables
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        self.push_url = os.environ.get('POWERBI_PUSH_URL')
        # Set up data directory and CSV path
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.csv_path = self.data_dir / 'aqi_data.csv'
        # Create CSV if it doesn’t exist
        if not self.csv_path.exists():
            self.setup_csv()

    def setup_csv(self):
        # Define CSV columns
        columns = ['city', 'timestamp', 'aqi', 'co', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'temperature', 'humidity', 'collection_status']
        pd.DataFrame(columns=columns).to_csv(self.csv_path, index=False)

    def collect_data(self, city):
        try:
            # Get city coordinates
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.api_key}"
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            if not geo_data:
                raise Exception(f"No coordinates found for {city}")
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

            # Fetch AQI data
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.api_key}"
            aqi_response = requests.get(aqi_url)
            aqi_data = aqi_response.json()

            # Fetch weather data
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            # Create data record
            record = {
                'city': city,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'aqi': aqi_data['list'][0]['main']['aqi'],
                'co': aqi_data['list'][0]['components']['co'],
                'no2': aqi_data['list'][0]['components']['no2'],
                'o3': aqi_data['list'][0]['components']['o3'],
                'so2': aqi_data['list'][0]['components']['so2'],
                'pm2_5': aqi_data['list'][0]['components']['pm2_5'],
                'pm10': aqi_data['list'][0]['components']['pm10'],
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'collection_status': 'success'
            }

            # Append to CSV
            df = pd.DataFrame([record])
            df.to_csv(self.csv_path, mode='a', header=False, index=False)

            # Push to Power BI
            self.push_to_powerbi(record)

            logging.info(f"Successfully collected data for {city}")
            return True

        except Exception as e:
            # Handle errors
            logging.error(f"Error collecting data for {city}: {str(e)}")
            error_record = {key: None for key in ['city', 'timestamp', 'aqi', 'co', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'temperature', 'humidity']}
            error_record['city'] = city
            error_record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_record['collection_status'] = f'error: {str(e)}'
            pd.DataFrame([error_record]).to_csv(self.csv_path, mode='a', header=False, index=False)
            return False

    def push_to_powerbi(self, record):
        # Method to push data to Power BI
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.push_url, headers=headers, data=json.dumps([record]))
            if response.status_code == 200:
                logging.info(f"Successfully pushed data to Power BI for {record['city']}")
            else:
                logging.error(f"Failed to push data to Power BI: {response.status_code}")
        except Exception as e:
            logging.error(f"Error pushing data to Power BI: {str(e)}")

    def collect_all_cities(self):
        # List of cities to collect data for
        cities = ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bengaluru', 'Ahmedabad', 'Lucknow', 'Hyderabad', 'Jaipur', 'Patna']
        for city in cities:
            self.collect_data(city)
            time.sleep(2)  # Avoid hitting API rate limits

if __name__ == "__main__":
    collector = GitHubAQICollector()
    collector.collect_all_cities()
