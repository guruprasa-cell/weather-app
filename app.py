import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    if request.method == "POST":
        city = request.form.get("city")

        # 1. Geocoding API to get latitude & longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()

        if geo_res.get("results"):
            location = geo_res["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            city_name = (
                f"{location.get('name')}, {location.get('country', '')}"
            )

            # 2. Weather API call with current_weather=true & relative_humidity_2m
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m"
            res = requests.get(weather_url).json()

            current = res.get("current_weather", {})
            hourly = res.get("hourly", {})

            # Get latest humidity value from hourly data
            humidity_list = hourly.get("relative_humidity_2m", [])
            humidity = humidity_list[0] if humidity_list else "N/A"

            weather_data = {
                "city": city_name,
                "temperature": current.get("temperature", "N/A"),
                "humidity": humidity,
                "wind_speed": current.get("windspeed", "N/A"),
                "condition": "Clear",
            }

    return render_template("index.html", weather=weather_data)


if __name__ == "__main__":
    app.run(debug=True)