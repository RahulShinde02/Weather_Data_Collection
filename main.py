"""Weather ETL Pipeline Orchestrator.

Orchestrates:
1. Data Extraction: Fetches weather forecasts using `request_data.py`.
2. Data Processing & Loading: Transforms and appends data to Delta Lake using `process_data.py`.
"""

import argparse
import sys
import time
from pathlib import Path

from process_data import process_weather_data
from request_data import fetch_weather_data


def run_pipeline(
    city_file: Path | str = Path("./city_json/city.json"),
    output_dir: Path | str = Path("./json_files"),
    delta_table_path: Path | str = Path("./weather_deltatable"),
    forecast_days: int = 1,
    skip_request: bool = False,
    skip_process: bool = False,
) -> bool:
    """Run the end-to-end weather data pipeline.

    Args:
        city_file: Path to JSON file containing city coordinate definitions.
        output_dir: Directory where raw JSON weather responses are stored.
        delta_table_path: Path to the destination Delta Lake table.
        forecast_days: Number of days of weather forecast to fetch.
        skip_request: If True, skips fetching new data from Open-Meteo API.
        skip_process: If True, skips transformation and Delta table write.

    Returns:
        bool: True if pipeline completed successfully, False otherwise.
    """
    start_time = time.time()
    print("=" * 60)
    print(" Weather ETL Pipeline Started")
    print("=" * 60)

    json_file_path: Path | None = None

    # Step 1: Request weather data
    if not skip_request:
        print("\n[Step 1/2] Requesting weather data from Open-Meteo API...")
        try:
            json_file_path = fetch_weather_data(
                city_file=city_file,
                output_dir=output_dir,
                forecast_days=forecast_days,
            )
            print(f"[Step 1/2] Data request complete. Saved to: {json_file_path}")
        except Exception as e:
            print(
                f"[Step 1/2] ERROR: Failed to request weather data: {e}",
                file=sys.stderr,
            )
            return False
    else:
        print("\n[Step 1/2] Skipping weather data request step (--skip-request).")

    # Step 2: Process data and load into Delta Lake
    if not skip_process:
        print("\n[Step 2/2] Processing weather data and writing to Delta table...")
        try:
            df = process_weather_data(
                json_file=json_file_path,
                city_file=city_file,
                output_delta_path=delta_table_path,
            )
            print(
                f"[Step 2/2] Processing complete. {len(df)} records written to {delta_table_path}"
            )
        except Exception as e:
            print(
                f"[Step 2/2] ERROR: Failed during data processing: {e}", file=sys.stderr
            )
            return False
    else:
        print("\n[Step 2/2] Skipping data processing step (--skip-process).")

    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f" Pipeline Execution Successful in {elapsed_time:.2f}s")
    print("=" * 60)
    return True


def main() -> None:
    """CLI entry point for pipeline orchestration."""
    parser = argparse.ArgumentParser(
        description="Orchestrate weather data extraction and Delta Lake processing."
    )
    parser.add_argument(
        "--city-file",
        type=Path,
        default=Path("./city_json/city.json"),
        help="Path to city coordinates JSON file (default: ./city_json/city.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./json_files"),
        help="Directory to store raw API JSON files (default: ./json_files)",
    )
    parser.add_argument(
        "--delta-table",
        type=Path,
        default=Path("./weather_deltatable"),
        help="Path to output Delta Lake directory (default: ./weather_deltatable)",
    )
    parser.add_argument(
        "--forecast-days",
        type=int,
        default=1,
        help="Number of forecast days to request (default: 1)",
    )
    parser.add_argument(
        "--skip-request",
        action="store_true",
        help="Skip requesting new data and use existing downloaded JSON file",
    )
    parser.add_argument(
        "--skip-process",
        action="store_true",
        help="Skip processing and saving to Delta table",
    )

    args = parser.parse_args()

    success = run_pipeline(
        city_file=args.city_file,
        output_dir=args.output_dir,
        delta_table_path=args.delta_table,
        forecast_days=args.forecast_days,
        skip_request=args.skip_request,
        skip_process=args.skip_process,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
