# %%
import datetime
import json
from pathlib import Path

import requests


def fetch_weather_data(
    city_file: Path | str = Path("./city_json/city.json"),
    output_dir: Path | str = Path("./json_files"),
    forecast_days: int = 1,
) -> Path:
    """Fetch daily weather forecasts from Open-Meteo API for configured cities.

    Args:
        city_file: Path to the city coordinates JSON file.
        output_dir: Directory where the fetched JSON data should be stored.
        forecast_days: Number of forecast days to request (default: 1).

    Returns:
        Path to the saved JSON file.
    """
    city_path = Path(city_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not city_path.exists():
        if Path("./city.json").exists():
            city_path = Path("./city.json")
        else:
            raise FileNotFoundError(f"City configuration file not found at: {city_path}")

    # 1. Load cities configuration
    with open(city_path, "r", encoding="utf-8") as file:
        cities: list[dict] = json.load(file)

    # 2. Extract coordinates
    latitudes = ",".join(str(c["lat"]) for c in cities)
    longitudes = ",".join(str(c["lng"]) for c in cities)

    # 3. Build Open-Meteo request URL
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitudes}"
        f"&longitude={longitudes}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
        f"&forecast_days={forecast_days}"
    )

    # 4. Fetch weather data safely
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 5. Save JSON using standard ISO date format (YYYY-MM-DD)
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        output_file = output_path / f"{date_str}_data.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(response.json(), file, indent=4)

        print(f"Successfully downloaded weather data to: {output_file}")
        return output_file

    except requests.RequestException as e:
        print(f"Error requesting weather data: {e}")
        raise


if __name__ == "__main__":
    fetch_weather_data()
