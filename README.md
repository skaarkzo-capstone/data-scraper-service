# Project Overview

This project automates the process of collecting sustainability-related data from company websites and SEDAR (via Selenium), then consolidates the results into a JSON file. It leverages FastAPI for the API layer, Selenium for SEDAR automation, various scrapers for PDF and website content, and a coordinated service to combine data.

## Key Features

- **Parallel Task Execution**: Website scraping and SEDAR automation can run concurrently.
- **Robust Error Handling & Logging**: Wrapped in `try/except` with logging for easier debugging.
- **Directory Management**: Clears or recreates PDF, JSON, and temp directories to keep the workspace clean.
- **Unified JSON Output**: Consolidates all results into a single combined file for final consumption.

## Getting Started

1. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt

2. **Run FastAPI**:
   ```bash
   uvicorn app.main:app --port=8000 --reload

3. **Invoke Endpoint**:
Send POST request to http://localhost:8000/ with JSON containing { "company_name": "...", "website": true, "sedar": true }.
