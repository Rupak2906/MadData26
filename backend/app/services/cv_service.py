"""
cv_service.py
-------------
Runs MediaPipe pose detection on body images and extracts normalized measurements.
Includes image validation, pose orientation checks, and measurement computation.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import cv2
import mediapipe as mp


class ValidationError(Exception):
    """Structured validation error raised by CVService."""
    def __init__(self, status: str, reason: str, message: str):
        self.status = status
        self.reason = reason
        self.message = message
        super().__init__(message)


@dataclass
class RawMeasurements:
    shoulder_width_n: float
    hip_width_n: float
    waist_width_n: float
    torso_length_n: float
    leg_length_n: float
    arm_length_n: float
    upper_arm_n: float
    forearm_n: float
    thigh_n: float
    calf_n: float
    symmetry_score: float


class CVService:
    """Computer Vision service for deterministic body scan and measurement extraction."""

    REQUIRED_LANDMARKS = [
        "nose", "left_shoulder", "right_shoulder", "left_hip", "right_hip",
        "left_elbow", "right_elbow", "left_wrist", "right_wrist",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
    ]

    LANDMARK_INDEX = {
        "nose": 0,
        "left_shoulder": 11,
        "right_shoulder": 12,
        "left_elbow": 13,
        "right_elbow": 14,
        "left_wrist": 15,
        "right_wrist": 16,
        "left_hip": 23,
        "right_hip": 24,
        "left_knee": 25,
        "right_knee": 26,
        "left_ankle": 27,
        "right_ankle": 28,
    }

    # ── Pose detection ─────────────────────────────────────────────────────────

    def detect_pose(self, image: np.ndarray) -> Any:
        """Run MediaPipe pose detection and return results."""
        with mp.solutions.pose.Pose(static_image_mode=True) as pose:
            results = pose.process(image)
        return results

    def extract_landmarks(self, results: Any) -> Dict[str, Any]:
        """Extract named landmarks from MediaPipe results."""
        if not results.pose_landmarks:
            return {}
        return {
            name: results.pose_landmarks.landmark[idx]
            for name, idx in self.LANDMARK_INDEX.items()
        }

    # ── Landmark helpers ────────────────────────────────────────────────────────

    def landmark_visible(self, landmark: Optional[Any]) -> bool:
        """Return True if landmark visibility exceeds threshold."""
        return landmark is not None and getattr(landmark, "visibility", 0) >= 0.5

    def calculate_distance(self, a: Any, b: Any) -> float:
        """Euclidean distance between two landmarks (normalised 0-1 coordinates)."""
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

    def midpoint(self, a: Any, b: Any) -> Any:
        """Return a simple object at the midpoint of two landmarks."""
        class _Point:
            pass
        p = _Point()
        p.x = (a.x + b.x) / 2
        p.y = (a.y + b.y) / 2
        p.z = (getattr(a, "z", 0) + getattr(b, "z", 0)) / 2
        p.visibility = min(getattr(a, "visibility", 1), getattr(b, "visibility", 1))
        return p

    # ── Validation ─────────────────────────────────────────────────────────────

    def validate_features(self, image: np.ndarray, pose_type: str) -> None:
        """
        Full validation pipeline for a single image.
        Raises ValidationError if any check fails.
        Called by both dev_routes and prediction_routes before extraction.
        """
        if pose_type not in {"front", "back"}:
            raise ValidationError("rejected", "wrong_pose", "Pose type must be 'front' or 'back'.")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detect_pose(rgb)
        landmarks = self.extract_landmarks(results)

        if not landmarks:
            raise ValidationError(
                "rejected", "no_pose_detected",
                "No person detected in the image. Ensure full-body visibility against a plain background."
            )

        # All required landmarks must be visible
        missing = [
            name for name in self.REQUIRED_LANDMARKS
            if not self.landmark_visible(landmarks.get(name))
        ]
        if missing:
            raise ValidationError(
                "rejected", "low_confidence",
                f"Could not detect: {', '.join(missing)}. Ensure good lighting and full-body photo."
            )

        # Full body — ankles must be visible
        if not (
            self.landmark_visible(landmarks.get("left_ankle"))
            and self.landmark_visible(landmarks.get("right_ankle"))
        ):
            raise ValidationError(
                "rejected", "feet_not_visible",
                "Please ensure your full body including feet is visible in the photo."
            )

        # Pose orientation check
        nose = landmarks.get("nose")
        ls = landmarks.get("left_shoulder")
        rs = landmarks.get("right_shoulder")
        if nose and ls and rs:
            nose_between = min(ls.x, rs.x) < nose.x < max(ls.x, rs.x)
            if pose_type == "front" and not nose_between:
                raise ValidationError("rejected", "wrong_pose", "Please upload a FRONT-facing image.")
            if pose_type == "back" and nose_between:
                raise ValidationError("rejected", "wrong_pose", "Please upload a BACK-facing image.")

    def validate_landmarks(self, landmarks: Dict[str, Any]) -> None:
        """Validate landmark dict directly (used inside process_image)."""
        for name in self.REQUIRED_LANDMARKS:
            if not self.landmark_visible(landmarks.get(name)):
                raise ValidationError(
                    "rejected", "low_confidence",
                    f"Landmark '{name}' not visible or low confidence."
                )

    # ── Measurement computation ────────────────────────────────────────────────

    def compute_measurements(self, landmarks: Dict[str, Any]) -> RawMeasurements:
        """Compute normalised biomechanical measurements from landmarks."""
        lm = landmarks  # shorthand

        nose = lm["nose"]
        ls, rs = lm["left_shoulder"], lm["right_shoulder"]
        lh, rh = lm["left_hip"], lm["right_hip"]
        le, re = lm["left_elbow"], lm["right_elbow"]
        lw, rw = lm["left_wrist"], lm["right_wrist"]
        lk, rk = lm["left_knee"], lm["right_knee"]
        la, ra = lm["left_ankle"], lm["right_ankle"]

        ankle_mid = self.midpoint(la, ra)
        body_height = self.calculate_distance(nose, ankle_mid)
        if body_height < 1e-6:
            raise ValidationError("rejected", "invalid_body_height", "Body height could not be computed.")

        shoulder_mid = self.midpoint(ls, rs)
        hip_mid = self.midpoint(lh, rh)

        shoulder_width = self.calculate_distance(ls, rs)
        hip_width = self.calculate_distance(lh, rh)
        waist_width = abs((shoulder_mid.x + hip_mid.x) / 2 - hip_mid.x) * 2  # estimated
        torso_length = self.calculate_distance(shoulder_mid, hip_mid)
        leg_length = self.calculate_distance(hip_mid, ankle_mid)

        l_arm = self.calculate_distance(ls, lw)
        r_arm = self.calculate_distance(rs, rw)
        arm_length = (l_arm + r_arm) / 2

        l_upper = self.calculate_distance(ls, le)
        r_upper = self.calculate_distance(rs, re)
        upper_arm = (l_upper + r_upper) / 2

        l_fore = self.calculate_distance(le, lw)
        r_fore = self.calculate_distance(re, rw)
        forearm = (l_fore + r_fore) / 2

        l_thigh = self.calculate_distance(lh, lk)
        r_thigh = self.calculate_distance(rh, rk)
        thigh = (l_thigh + r_thigh) / 2

        l_calf = self.calculate_distance(lk, la)
        r_calf = self.calculate_distance(rk, ra)
        calf = (l_calf + r_calf) / 2

        symmetry = self.compute_symmetry([
            l_arm, r_arm, l_upper, r_upper,
            l_fore, r_fore, l_thigh, r_thigh,
            l_calf, r_calf,
        ])

        h = body_height
        return RawMeasurements(
            shoulder_width_n=shoulder_width / h,
            hip_width_n=hip_width / h,
            waist_width_n=max(waist_width / h, 0.01),
            torso_length_n=torso_length / h,
            leg_length_n=leg_length / h,
            arm_length_n=arm_length / h,
            upper_arm_n=upper_arm / h,
            forearm_n=forearm / h,
            thigh_n=thigh / h,
            calf_n=calf / h,
            symmetry_score=symmetry,
        )

    def compute_symmetry(self, pairs: list) -> float:
        """Compute mean bilateral symmetry score (1.0 = perfect)."""
        diffs = []
        for i in range(0, len(pairs) - 1, 2):
            left, right = pairs[i], pairs[i + 1]
            avg = (left + right) / 2
            if avg > 0:
                diffs.append(abs(left - right) / avg)
        if not diffs:
            return 1.0
        return float(max(0.0, min(1.0, 1.0 - sum(diffs) / len(diffs))))

    # ── Public entry point ─────────────────────────────────────────────────────

    def process_image(self, image: np.ndarray, pose_type: str) -> RawMeasurements:
        """
        Full pipeline: validate → detect → extract → compute.
        Returns RawMeasurements ready for the ML feature builder.
        """
        if pose_type not in {"front", "back"}:
            raise ValidationError("rejected", "wrong_pose", "Pose type must be 'front' or 'back'.")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detect_pose(rgb)
        landmarks = self.extract_landmarks(results)

        if not landmarks:
            raise ValidationError(
                "rejected", "no_pose_detected",
                "No person detected. Ensure a clear, well-lit, full-body photo."
            )

        self.validate_landmarks(landmarks)
        return self.compute_measurements(landmarks)