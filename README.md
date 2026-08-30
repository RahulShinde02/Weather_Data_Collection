# 🌦️ Weather Data Collection

A lightweight weather ETL pipeline built for fun. It fetches daily weather forecasts for configured cities using the Open-Meteo API, transforms the data using **Polars**, and stores it in a local **Delta Lake** table.

---

## 🚀 What it does

1. **Extract**: Reads city coordinates from `city_json/city.json` and hits the free [Open-Meteo API](https://open-meteo.com/).
2. **Transform**: Flattens, unnests, and cleans the weather metrics with **Polars**.
3. **Load**: Appends structured records to a local **Delta table** (`weather_deltatable/`).

---

## 🛠️ Tech Stack

- **Python** (>= 3.14)
- **[Polars](https://pola.rs/)** – Blazing fast data processing
- **[Delta Lake](https://delta-io.github.io/delta-rs/) (`deltalake`)** – Reliable ACID table storage
- **[Requests](https://requests.readthedocs.io/)** – HTTP client for Open-Meteo API
- **[uv](https://github.com/astral-sh/uv)** – Fast Python package manager

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
# using uv
uv sync

# or using pip
pip install polars deltalake requests
```

### 2. Run the pipeline

```bash
python main.py
```

### 3. Useful options

```bash
# Fetch 7-day forecast (default is 1 day)
python main.py --forecast-days 7

# Reprocess existing JSON data without calling the API
python main.py --skip-request

# Download data only without writing to Delta table
python main.py --skip-process
```

---

## 📁 Project Layout

```text
├── city_json/          # City coordinate definitions
├── json_files/         # Raw JSON responses from API
├── weather_deltatable/ # Delta Lake storage directory
├── request_data.py     # Data extraction script
├── process_data.py     # Polars transformation & Delta writer
└── main.py             # Pipeline orchestrator & CLI
```

---
