from fastapi import APIRouter, HTTPException, status

from ..schemas import ServiceOut
from ..services_catalog import SERVICES, get_service

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services() -> list[ServiceOut]:
    return SERVICES


@router.get("/{slug}", response_model=ServiceOut)
def read_service(slug: str) -> ServiceOut:
    service = get_service(slug)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return service
