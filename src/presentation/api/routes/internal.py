from fastapi import APIRouter, HTTPException, status

from src.application.exceptions import AdNotFoundError
from src.presentation.api.dependencies import GetAdInternalDep
from src.presentation.api.schemas import AdResponse

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/ads/{ad_id}")
async def get_ad_internal(
    ad_id: int,
    usecase: GetAdInternalDep,
) -> AdResponse:
    try:
        ad = await usecase.execute(ad_id)
    except AdNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )
    return AdResponse.from_entity(ad)
