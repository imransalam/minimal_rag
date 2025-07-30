import traceback
from fastapi import APIRouter, Depends, HTTPException
from custom_logger import logger
from api.model.input import Input
from api.model.output import Output
from api.services.query_service import QueryService
from api.auth import check_key
from typing import Annotated

router: APIRouter = APIRouter()

async def get_query_service() -> QueryService:
    return QueryService()

@router.post(
    "/query",
    response_model=Output,
    summary="Get a life advice based on the input query",
    responses={
        200: {"model": Output}, 
        500: {"description": "Internal Server Error"}, 
        422: {"description": "Validation Error"}
    }
)
async def query(query: Input,
                api_key: Annotated[str, Depends(check_key)], 
                query_service: QueryService = Depends(get_query_service)) -> Output:
    """
   Gets a life advice based on the input query

    Parameters
    ----------
    query : str
        This is the input query for which the life advice is to be generated.
    
    Returns
    -------
    JSONResponse
        JSON response containing the advice.
    """
    try:
        logger._log(f"POST /query", format="info")
        output_object: Output = query_service.get_life_advice(query.query)
        return output_object
    except Exception as e:
        logger._log(f"Internal Server Error: /query", format="error")
        logger._log(str(e), format="error")
        logger._log(traceback.format_exc(), format="error")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )