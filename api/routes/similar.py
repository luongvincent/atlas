from __future__ import annotations

from fastapi import APIRouter

from api.schemas import SimilarItemsResponse
from core.similar_items import get_similar_items

router = APIRouter()


@router.get("/similar/{ticker}", response_model=SimilarItemsResponse)
async def get_similar(ticker: str) -> SimilarItemsResponse:
    ticker = ticker.upper()
    return SimilarItemsResponse(ticker=ticker, items=get_similar_items(ticker))
