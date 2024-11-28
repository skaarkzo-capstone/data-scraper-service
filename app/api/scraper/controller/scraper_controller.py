from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def test_route():
    return "works!"

SERVICE_SCRIPT = "path_to_your_service_script.py"