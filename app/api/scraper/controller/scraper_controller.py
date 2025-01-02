import logging
import asyncio
import os
import json
import subprocess

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.model.request.process_request import ProcessRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()
SERVICE_SCRIPT = "app.service.scraper_service"


def run_service(company_name: str, website: bool, sedar: bool) -> str:
    """
    Runs the scraper service as a subprocess, passing in the requested tasks (website, sedar).
    """
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
        # Potentially blocking call:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info("Service execution completed successfully.")
    except FileNotFoundError as e:
        logger.exception("Python or the service script was not found.")
        raise HTTPException(
            status_code=500,
            detail=f"Cannot find the script or Python interpreter: {e}"
        )
    except subprocess.CalledProcessError as e:
        logger.exception("Error running service.")
        raise HTTPException(
            status_code=500, detail=f"Service error: {e.stderr.strip()}"
        )
    except OSError as e:
        logger.exception("OS error while trying to run the service script.")
        raise HTTPException(status_code=500, detail=str(e))

    if not result.stdout:
        logger.error("Service returned no output.")
        raise HTTPException(status_code=500, detail="Service returned no output.")

    return result.stdout


@router.post("", summary="Process Company and return combined results")
async def process_company(request: Request, req_data: ProcessRequest):
    """
    Main entry point for processing a company's data via FastAPI route,
    with support for cancelling if the client disconnects.
    """
    logger.info("Starting process for company: %s", req_data.company_name)

    # Run the blocking function in a thread so we can do async cancellation checks
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(
        None,  # default executor
        run_service,
        req_data.company_name,
        req_data.website,
        req_data.sedar
    )

    try:
        # Periodically check if the client disconnected
        while not future.done():
            if await request.is_disconnected():
                logger.warning("Client disconnected. Attempting to stop processing.")
                future.cancel()  # Cancels the future
                raise HTTPException(
                    status_code=499,  # 499 is often used to indicate "Client Closed Request"
                    detail="Client disconnected before processing could finish."
                )
            await asyncio.sleep(1)  # Wait a bit before checking again

        # If we reach here, future is done; check for errors
        exception = future.exception()
        if exception:
            # If the blocking call raised an HTTPException, re-raise it
            if isinstance(exception, HTTPException):
                raise exception
            # Otherwise raise a generic internal server error
            logger.exception("Error in run_service.")
            raise HTTPException(status_code=500, detail=str(exception))

        # If no exception, proceed as before
        combined_file_path = "json_files/combined_results.json"
        if not os.path.exists(combined_file_path):
            logger.error("Combined results file not found after service execution.")
            raise HTTPException(
                status_code=500, detail="Combined results file not found."
            )

        try:
            with open(combined_file_path, "r", errors="ignore") as f:
                combined_data = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Error decoding combined results JSON.")
            raise HTTPException(status_code=500, detail="Error decoding combined results JSON.")

        logger.info(
            "Successfully returning combined results for company: %s",
            req_data.company_name
        )
        return JSONResponse(content=combined_data)

    except asyncio.CancelledError:
        # If our future or the route got cancelled, handle gracefully
        logger.warning("Processing was cancelled.")
        raise HTTPException(
            status_code=499,
            detail="Request cancelled during processing."
        )
    except HTTPException as e:
        logger.exception("HTTPException during company processing.")
        raise e
    except Exception as e:
        logger.exception("Unexpected error during company processing.")
        raise HTTPException(status_code=500, detail=str(e))
