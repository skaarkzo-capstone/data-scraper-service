import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.model.request.process_request import ProcessRequest
import subprocess
import os
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()
SERVICE_SCRIPT = "app.service.scraper_service"


def run_service(company_name: str, website: bool, sedar: bool) -> str:
    logger.info("Preparing to run service for company: %s", company_name)
    company_name = company_name.strip().lower()
    tasks = []
    if website:
        tasks.append("website")
    if sedar:
        tasks.append("sedar")

    command = ["python", "-m", SERVICE_SCRIPT, company_name]
    if tasks:
        command.extend(["--tasks", *tasks])

    logger.info("Executing command: %s", command)
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info("Service execution completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.exception("Error running service.")
        raise HTTPException(status_code=500, detail=f"Service error: {e.stderr.strip()}")

    if not result.stdout:
        logger.error("Service returned no output.")
        raise HTTPException(status_code=500, detail="Service returned no output.")

    return result.stdout


@router.post("", summary="Process Company and return combined results")
def process_company(request: ProcessRequest):
    logger.info("Starting process for company: %s", request.company_name)
    try:
        run_service(request.company_name, request.website, request.sedar)
        combined_file_path = "json_files/combined_results.json"

        if not os.path.exists(combined_file_path):
            logger.error("Combined results file not found after service execution.")
            raise HTTPException(
                status_code=500, detail="Combined results file not found."
            )

        with open(combined_file_path, "r", errors="ignore") as f:
            combined_data = json.load(f)

        logger.info("Successfully returning combined results for company: %s", request.company_name)
        return JSONResponse(content=combined_data)
    except HTTPException as e:
        logger.exception("HTTPException during company processing.")
        raise e
    except Exception as e:
        logger.exception("Unexpected error during company processing.")
        raise HTTPException(status_code=500, detail=str(e))
