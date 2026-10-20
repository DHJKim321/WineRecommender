from fastapi import APIRouter, Request

from winerecommender.models.requests import ExtractRequest

router = APIRouter(prefix="/extractor", tags=["extractor"])

@router.post("/extract")
def extract(
    body: ExtractRequest,
    request: Request
):
    service = request.app.state.extractor
    params = service.extract(
        body.query
    )
    return {
        "params": params
    }