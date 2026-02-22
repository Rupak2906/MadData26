
from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from io import BytesIO
from typing import Any
from PIL import Image, UnidentifiedImageError
from app.services.cv_service import CVService, ValidationError, RawMeasurements

router = APIRouter()

@router.post("/dev/test-cv", response_model=None)
async def test_cv(
    front_image: UploadFile,
    back_image: UploadFile,
    front_pose_type: str = Form(...),
    back_pose_type: str = Form(...)
) -> Any:
    """
    Development endpoint for testing CVService body measurement extraction with two images (front and back).
    Validates that both images are present, checks pose types, and ensures all required features are visible.
    If valid, extracts features and (optionally) sends to ML/AI for further processing.
    """
    try:
        # Helper to decode image
        async def decode_image(upload_file: UploadFile):
            file_bytes = await upload_file.read()
            if not file_bytes:
                return None
            np_arr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is not None:
                return img
            try:
                pil = Image.open(BytesIO(file_bytes)).convert("RGB")
                img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            except (UnidentifiedImageError, OSError):
                img = None
            return img

        # Decode both images
        img_front = await decode_image(front_image)
        img_back = await decode_image(back_image)
        if img_front is None or img_back is None:
            raise HTTPException(status_code=400, detail={"status": "rejected", "message": "Invalid image file(s)."})

        # Validate pose types
        valid_poses = {"front", "back"}
        if front_pose_type.lower() != "front" or back_pose_type.lower() != "back":
            return JSONResponse(
                status_code=400,
                content={
                    "status": "rejected",
                    "message": "Pose types must be 'front' and 'back' respectively."
                }
            )

        cv_service = CVService()

        # Validate features in both images (placeholder: implement actual feature checks in CVService)
        missing_features = []
        try:
            features_front = cv_service.validate_features(img_front, pose_type="front")
        except ValidationError as ve:
            missing_features.append(f"front: {ve.message}")
        try:
            features_back = cv_service.validate_features(img_back, pose_type="back")
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

        # Extract measurements from both images
        measurements_front: RawMeasurements = cv_service.process_image(img_front, "front")
        measurements_back: RawMeasurements = cv_service.process_image(img_back, "back")

        # Optionally: send features/measurements to ML/AI for prediction or data generation
        # result = your_ml_model.predict({...})

        return JSONResponse(content={
            "front_measurements": measurements_front.__dict__,
            "back_measurements": measurements_back.__dict__
            # , "ml_result": result
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
