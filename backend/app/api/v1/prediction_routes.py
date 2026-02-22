from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from typing import Any
from app.services.cv_service import CVService, ValidationError, RawMeasurements

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("")
async def upload_images(
    front_image: UploadFile,
    back_image: UploadFile,
    front_pose_type: str = Form(...),
    back_pose_type: str = Form(...)
) -> Any:
    """
    Production endpoint for body analysis prediction.
    Accepts two images (front and back) and pose types from frontend.
    Validates images, pose types, and features, then extracts measurements and returns results.
    """
    try:
        # Helper to decode image
        async def decode_image(upload_file: UploadFile):
            file_bytes = await upload_file.read()
            np_arr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return img

        img_front = await decode_image(front_image)
        img_back = await decode_image(back_image)
        if img_front is None or img_back is None:
            raise HTTPException(status_code=400, detail={"status": "rejected", "message": "Invalid image file(s)."})

        # Validate pose types
        if front_pose_type.lower() != "front" or back_pose_type.lower() != "back":
            return JSONResponse(
                status_code=400,
                content={
                    "status": "rejected",
                    "message": "Pose types must be 'front' and 'back' respectively."
                }
            )

        cv_service = CVService()

        # Validate features in both images
        missing_features = []
        try:
            cv_service.validate_features(img_front, pose_type="front")
        except ValidationError as ve:
            missing_features.append(f"front: {ve.message}")
        try:
            cv_service.validate_features(img_back, pose_type="back")
        except ValidationError as ve:
            missing_features.append(f"back: {ve.message}")

        if missing_features:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "rejected",
                    "message": "Image validation failed.",
                    "details": missing_features
                }
            )

        # Extract measurements
        measurements_front: RawMeasurements = cv_service.process_image(img_front, "front")
        measurements_back: RawMeasurements = cv_service.process_image(img_back, "back")

        # TODO: Integrate ML/AI prediction logic here if needed

        return JSONResponse(content={
            "front_measurements": measurements_front.__dict__,
            "back_measurements": measurements_back.__dict__
        })

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
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": "rejected",
                "message": f"{type(e).__name__}: {str(e)}"
            }
        )

@router.get("/{scan_id}")
def get_prediction(scan_id: str):
    """Get processing result/status for a given scan."""
    # Implement retrieval logic as needed
    return JSONResponse(content={"scan_id": scan_id, "status": "not implemented"})