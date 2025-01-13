# aqi_collector.py
import os
import requests
import pandas as pd
from datetime import datetime
import time
import logging
from pathlib import Path

class GitHubAQICollector:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # OpenWeatherMap API key from GitHub secrets
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        
        # Setup data storage
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.csv_path = self.data_dir / 'aqi_data.csv'
        
        # Initialize CSV if it doesn't exist
        if not self.csv_path.exists():
            self.setup_csv()

    def setup_csv(self):
        """Initialize CSV file with headers"""
        columns = [
            'city', 'timestamp', 'aqi', 'co', 'no2', 'o3', 'so2',
            'pm2_5', 'pm10', 'temperature', 'humidity', 'collection_status'
        ]
        pd.DataFrame(columns=columns).to_csv(self.csv_path, index=False)

    def collect_data(self, city):
        """Collect AQI data for a city"""
        try:
            # Get coordinates
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={self.api_key}"
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()

            if not geo_data:
                raise Exception(f"No coordinates found for {city}")

            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

            # Get AQI and weather data
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.api_key}"
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"

            aqi_response = requests.get(aqi_url)
            weather_response = requests.get(weather_url)

            aqi_data = aqi_response.json()
            weather_data = weather_response.json()

            # Prepare data record
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

            logging.info(f"Successfully collected data for {city}")
            return True

        except Exception as e:
            logging.error(f"Error collecting data for {city}: {str(e)}")
            # Log error record to CSV
            error_record = {
                'city': city,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'aqi': None, 'co': None, 'no2': None, 'o3': None,
                'so2': None, 'pm2_5': None, 'pm10': None,
                'temperature': None, 'humidity': None,
                'collection_status': f'error: {str(e)}'
            }
            pd.DataFrame([error_record]).to_csv(
                self.csv_path, mode='a', header=False, index=False
            )
            return False

    def collect_all_cities(self):
        """Collect data for all cities"""
        cities = [
            'Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bengaluru',
            'Ahmedabad', 'Lucknow', 'Hyderabad', 'Jaipur', 'Patna'
        ]
        
        for city in cities:
            self.collect_data(city)
            time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    collector = GitHubAQICollector()
    collector.collect_all_cities()
