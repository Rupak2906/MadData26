from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from typing import Any
from app.services.cv_service import CVService, ValidationError, RawMeasurements

router = APIRouter()

@router.post("/dev/test-cv", response_model=None)
async def test_cv(
    image: UploadFile,
    pose_type: str = Form(...)
) -> Any:
    """
    Temporary development endpoint for testing CVService body measurement extraction.
    Accepts an image and pose_type, runs the CV pipeline, and returns RawMeasurements as JSON.
    No ML, database, or authentication involved.
    """
    try:
        file_bytes = await image.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail={"status": "rejected", "message": "Invalid image file."})

        cv_service = CVService()
        measurements: RawMeasurements = cv_service.process_image(img, pose_type)

        return JSONResponse(content=measurements.__dict__)

    except ValidationError as ve:
        return JSONResponse(
            status_code=400,
            content={
                "status": ve.status,
                "reason": ve.reason,
                "message": ve.message
            }
        )
    except Exception as e:
        # For development: log and return the actual error message for easier debugging
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": "rejected",
                "message": f"{type(e).__name__}: {str(e)}"
            }
        )