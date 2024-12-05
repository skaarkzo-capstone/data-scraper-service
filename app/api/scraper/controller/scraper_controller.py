from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.model.request.process_request import ProcessRequest
import subprocess
import os
import json

router = APIRouter()

SERVICE_SCRIPT = "app.service.scraper_service"

def run_service(company_name: str, website: bool, sedar: bool):
    # Prepare arguments for the service script based on flags

    company_name = company_name.strip().lower()

    args = [company_name]
    if website:
        args.append("--website")
    if sedar:
        args.append("--sedar")

    print(f"Running the scraper using args: {args}")

    command = ["python", "-m", SERVICE_SCRIPT, *args]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Service error: {result.stderr.strip()}")
    
    print("Completed")

    return result.stdout

@router.post("")
def process_company(request: ProcessRequest):
    try:
        # Call the service with the provided parameters
        run_service(request.company_name, request.website, request.sedar)

        combined_file_path = "json_files/combined_results.json"
        if not os.path.exists(combined_file_path):
            raise HTTPException(
                status_code=500,
                detail="Combined results file not found after running the service.",
            )

        with open(combined_file_path, "r", errors="ignore") as f:
            combined_data = json.load(f)

        return JSONResponse(content=combined_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))