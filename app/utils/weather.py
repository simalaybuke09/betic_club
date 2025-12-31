"""Hava Durumu Yardımcı Modülü"""
import requests
import os
from flask import current_app


def get_weather_data(city="Trabzon"):
    """Hava durumu verilerini çeker"""
    api_key = os.environ.get('WEATHER_API_KEY') or current_app.config.get('WEATHER_API_KEY')
    
    
    if api_key:
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {'q': f"{city},TR", 'appid': api_key, 'units': 'metric', 'lang': 'tr'}
            response = requests.get(url, params=params, timeout=5)  #Hedef sunucuya bir HTTP GET isteği gönderir.
            response.raise_for_status() #anında bir HTTPError exception fırlatır ve programı güvenli bir şekilde except bloğuna yönlendirir.
            data = response.json() #ham metni (JSON formatı), Python'ın kolayca okuyabileceği bir Dictionary yapısına dönüştürür.
            return {
                'city': data.get('name', city),
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data.get('wind', {}).get('speed', 0) * 3.6),
                'error': None
            }
        except:
            pass
    