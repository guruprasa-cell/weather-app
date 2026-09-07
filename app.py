from flask import Flask, render_template, request
import requests

app = Flask(__name__)

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Slight rain showers",
    81: "Moderate rain showers", 82: "Violent rain showers", 95: "Thunderstorm"
}

def get_coordinates(city_name):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "format": "json"}
    
    try:
        res = requests.get(geo_url, params=params).json()
        if "results" in res and len(res["results"]) > 0:
            item = res["results"][0]
            return {
                "name": item.get("name"),
                "country": item.get("country", ""),
                "lat": item["latitude"],
                "lon": item["longitude"]
            }
    except Exception:
        pass
    return None

def get_full_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "forecast_days": 5,
        "timezone": "auto"
    }
    
    try:
        res = requests.get(url, params=params).json()
        current_data = res.get("current", {})
        daily_data = res.get("daily", {})
        
        current = {
            "temp": current_data.get("temperature_2m"),
            "humidity": current_data.get("relative_humidity_2m"),
            "wind": current_data.get("wind_speed_10m"),
            "condition": WEATHER_CODES.get(current_data.get("weather_code"), "Clear")
        }
        
        forecast = []
        times = daily_data.get("time", [])
        for i in range(len(times)):
            forecast.append({
                "date": times[i],
                "max": daily_data["temperature_2m_max"][i],
                "min": daily_data["temperature_2m_min"][i],
                "condition": WEATHER_CODES.get(daily_data["weather_code"][i], "Clear")
            })
            
        return current, forecast
    except Exception as e:
        print(f"Error: {e}")
        return None, None
    
    
    try:
        res = requests.get(url, params=params).json()
        current_data = res.get("current", {})
        daily_data = res.get("daily", {})
        
        current = {
            "temp": current_data.get("temperature_2m"),
            "humidity": current_data.get("relative_humidity_2m"),
            "wind": current_data.get("wind_speed_10m"),
            "condition": WEATHER_CODES.get(current_data.get("weather_code"), "Unknown")
        }
        
        forecast = []
        for i in range(len(daily_data.get("time", []))):
            forecast.append({
                "date": daily_data["time"][i],
                "max": daily_data["temperature_2m_max"][i],
                "min": daily_data["temperature_2m_min"][i],
                "condition": WEATHER_CODES.get(daily_data["weather_code"][i], "Unknown")
            })
            
        return current, forecast
    except Exception:
        return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    location_data = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            location_data = get_coordinates(city)
            if location_data:
                weather_data, forecast_data = get_full_weather(location_data["lat"], location_data["lon"])
            else:
                error = f"City '{city}' not found."
        else:
            error = "Please enter a valid city name."

    return render_template(
        "index.html", 
        location=location_data, 
        current=weather_data, 
        forecast=forecast_data, 
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)