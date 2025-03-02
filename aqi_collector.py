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
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # OpenWeatherMap API key from GitHub secrets
        self.api_key = os.environ.get('OPENWEATHER_API_KEY')
        
        # Setup data storage
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.csv_path = self.data_dir / 'aqi_data.csv'
        
        # Retrieve Power BI push URLs from environment variables
        self.push_urls = {
            'Delhi': os.environ.get('POWERBI_PUSH_URL_DELHI'),
            'Mumbai': os.environ.get('POWERBI_PUSH_URL_MUMBAI'),
            'Chennai': os.environ.get('POWERBI_PUSH_URL_CHENNAI'),
            'Kolkata': os.environ.get('POWERBI_PUSH_URL_KOLKATA'),
            'Bengaluru': os.environ.get('POWERBI_PUSH_URL_BENGALURU'),
            'Ahmedabad': os.environ.get('POWERBI_PUSH_URL_AHMEDABAD'),
            'Lucknow': os.environ.get('POWERBI_PUSH_URL_LUCKNOW'),
            'Hyderabad': os.environ.get('POWERBI_PUSH_URL_HYDERABAD'),
            'Jaipur': os.environ.get('POWERBI_PUSH_URL_JAIPUR'),
            'Patna': os.environ.get('POWERBI_PUSH_URL_PATNA')
        }
        self.main_push_url = os.environ.get('POWERBI_PUSH_URL_ALL')
        
        # Initialize CSV if it doesn’t exist
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

            # Push to Power BI
            self.push_to_powerbi(record)

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

    def push_to_powerbi(self, record):
        """Push data to Power BI for the specific city and the main dataset"""
        city = record['city']
        city_push_url = self.push_urls.get(city)
        if city_push_url:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(city_push_url, headers=headers, data=json.dumps([record]))
                if response.status_code == 200:
                    logging.info(f"Successfully pushed data to Power BI for {city}")
                else:
                    logging.error(f"Failed to push to city dataset for {city}: {response.status_code}")
            except Exception as e:
                logging.error(f"Error pushing to city dataset for {city}: {str(e)}")
        
        # Push to main dataset
        if self.main_push_url:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(self.main_push_url, headers=headers, data=json.dumps([record]))
                if response.status_code == 200:
                    logging.info(f"Successfully pushed data to Power BI main dataset for {city}")
                else:
                    logging.error(f"Failed to push to main dataset for {city}: {response.status_code}")
            except Exception as e:
                logging.error(f"Error pushing to main dataset for {city}: {str(e)}")

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
