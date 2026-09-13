from fastapi import APIRouter

router = APIRouter(
    prefix="/{{ROUTE}}",
    tags=["{{CLASS_NAME}}"],
)