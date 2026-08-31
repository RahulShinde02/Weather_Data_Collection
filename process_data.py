# %%
import datetime
from pathlib import Path

import polars as pl


def process_weather_data(
    json_file: Path | str | None = None,
    city_file: Path | str = Path("./city_json/city.json"),
    output_delta_path: Path | str = Path("./weather_deltatable"),
) -> pl.DataFrame:
    """Read raw weather JSON, join with city metadata, transform and save to Delta Lake.

    Args:
        json_file: Optional path to the raw weather JSON. Defaults to today's data file.
        city_file: Path to the city coordinates JSON file.
        output_delta_path: Destination directory for Delta Lake table.

    Returns:
        Polars DataFrame containing processed weather observations.
    """
    city_path = Path(city_file)
    if not city_path.exists() and Path("./city.json").exists():
        city_path = Path("./city.json")

    if not city_path.exists():
        raise FileNotFoundError(f"City configuration file not found at: {city_path}")

    # 1. Setup JSON file path
    if json_file is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        target_json = Path(f"./json_files/{date_str}_data.json")

        # Fallback: check legacy date format if current ISO file doesn't exist
        if not target_json.exists():
            legacy_date = datetime.datetime.now().strftime("%d-%m-%Y")
            legacy_file = Path(f"./json_files/{legacy_date}_data.json")
            if legacy_file.exists():
                target_json = legacy_file

        if not target_json.exists():
            raise FileNotFoundError(f"No weather data file found for today ({date_str}) in ./json_files/")
    else:
        target_json = Path(json_file)
        if not target_json.exists():
            raise FileNotFoundError(f"Specified weather data file does not exist: {target_json}")

    # 2. Read city metadata with row index for 1-to-1 location joining
    cities_df = pl.read_json(city_path).with_row_index("location_id")

    # 3. Read Open-Meteo weather response
    weather_df = pl.read_json(target_json)
    timestamp = datetime.datetime.now()
    # 4. Join metadata and unnest/explode nested weather lists into clean tabular rows
    processed_df = (
        cities_df.join(weather_df, on="location_id")
        .unnest("daily")
        .explode(
            ["time", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            empty_as_null=True,
        )
        .with_columns(pl.col("time").str.to_date("%Y-%m-%d"))
        .select([
            pl.col("location_id"),
            pl.col("city"),
            pl.col("lat").alias("requested_lat"),
            pl.col("lng").alias("requested_lng"),
            pl.col("latitude").alias("api_lat"),
            pl.col("longitude").alias("api_lng"),
            pl.col("elevation"),
            pl.col("timezone"),
            pl.col("time").alias("forecast_date"),
            pl.col("temperature_2m_max"),
            pl.col("temperature_2m_min"),
            pl.col("precipitation_sum"),
            pl.lit(timestamp).alias("inserted_at"),
        ])
    )

    # 5. Append clean relational data to Delta Table
    delta_path_str = str(output_delta_path)
    processed_df.write_delta(
        delta_path_str,
        mode="append",
        delta_write_options={"schema_mode": "merge"},
    )


    print(f"Successfully processed {len(processed_df)} records and saved to Delta table at '{delta_path_str}'.")
    return processed_df


if __name__ == "__main__":
    process_weather_data()
