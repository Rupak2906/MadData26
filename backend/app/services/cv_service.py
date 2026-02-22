<<<<<<< HEAD
# Runs OpenCV/Mediapipe processing and extracts body measurements.

=======
import numpy as np
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import cv2
import mediapipe as mp

class ValidationError(Exception):
    """Structured validation error for CVService."""
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
    """Production-style Computer Vision service for deterministic body scan and measurement extraction."""

    REQUIRED_LANDMARKS = [
        'nose', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip',
        'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
    ]

    LANDMARK_INDEX = {
        'nose': 0,
        'left_shoulder': 11,
        'right_shoulder': 12,
        'left_elbow': 13,
        'right_elbow': 14,
        'left_wrist': 15,
        'right_wrist': 16,
        'left_hip': 23,
        'right_hip': 24,
        'left_knee': 25,
        'right_knee': 26,
        'left_ankle': 27,
        'right_ankle': 28,
    }

    def detect_pose(self, image: np.ndarray) -> Any:
        """Run MediaPipe pose detection and return results."""
        with mp.solutions.pose.Pose(static_image_mode=True) as pose:
            results = pose.process(image)
        return results

    def extract_landmarks(self, results: Any) -> Dict[str, Any]:
        """Extract required landmarks from MediaPipe results."""
        if not results.pose_landmarks:
            return {}
        landmarks = {}
        for name, idx in self.LANDMARK_INDEX.items():
            landmark = results.pose_landmarks.landmark[idx]
            landmarks[name] = landmark
        return landmarks

    def landmark_visible(self, landmark: Optional[Any]) -> bool:
        """Check if landmark visibility is above threshold."""
        return landmark is not None and getattr(landmark, 'visibility', 0) >= 0.5

    def calculate_distance(self, a: Any, b: Any) -> float:
        """Euclidean distance between two landmarks in pixel coordinates."""
        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

    def midpoint(self, a: Any, b: Any) -> Any:
        """Return a new landmark at the midpoint between two landmarks."""
        return type(a)(
            x=(a.x + b.x) / 2,
            y=(a.y + b.y) / 2,
            z=(getattr(a, 'z', 0) + getattr(b, 'z', 0)) / 2,
            visibility=min(getattr(a, 'visibility', 1), getattr(b, 'visibility', 1))
        )

    def validate_full_body(self, landmarks: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Validate full body visibility and landmark presence."""
        # Check feet (ankles)
        if not (self.landmark_visible(landmarks.get('left_ankle', None)) and self.landmark_visible(landmarks.get('right_ankle', None))):
            return False, 'feet_not_visible', 'Please ensure your full body including feet is visible.'
        # Check upper body
        if not (self.landmark_visible(landmarks.get('left_shoulder', None)) and self.landmark_visible(landmarks.get('right_shoulder', None))):
            return False, 'upper_body_not_visible', 'Upper body is not fully visible.'
        return True, '', ''

    def validate_pose_orientation(self, landmarks: Dict[str, Any], pose_type: str) -> Tuple[bool, str, str]:
        """Validate pose orientation matches pose_type."""
        # Use nose and shoulders to check facing direction
        nose = landmarks.get('nose')
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        if not (nose and left_shoulder and right_shoulder):
            return False, 'required_landmarks_missing', 'Upper body is not fully visible.'
        # If nose is between shoulders, likely front; if not, likely back
        nose_x = nose.x
        ls_x = left_shoulder.x
        rs_x = right_shoulder.x
        if pose_type == 'front':
            if not (min(ls_x, rs_x) < nose_x < max(ls_x, rs_x)):
                return False, 'wrong_pose', 'Please upload a FRONT-facing image.'
        elif pose_type == 'back':
            if min(ls_x, rs_x) < nose_x < max(ls_x, rs_x):
                return False, 'wrong_pose', 'Please upload a BACK-facing image.'
        else:
            return False, 'wrong_pose', 'Pose type must be "front" or "back".'
        return True, '', ''

    def validate_landmarks(self, landmarks: Dict[str, Any]) -> None:
        """Validate all required landmarks are present and visible."""
        for name in self.REQUIRED_LANDMARKS:
            lm = landmarks.get(name)
            if not self.landmark_visible(lm):
                raise ValidationError('rejected', 'low_confidence', f"Landmark {name} not visible or low confidence.")
        # Check full body visibility (ankles)
        if not (self.landmark_visible(landmarks.get('left_ankle')) and self.landmark_visible(landmarks.get('right_ankle'))):
            raise ValidationError('rejected', 'feet_not_visible', 'Please ensure your full body including feet is visible.')

    def compute_measurements(self, landmarks: Dict[str, Any]) -> RawMeasurements:
        """Compute normalized biomechanical measurements from landmarks."""
        # Extract landmarks
        nose = landmarks['nose']
        left_shoulder = landmarks['left_shoulder']
        right_shoulder = landmarks['right_shoulder']
        left_hip = landmarks['left_hip']
        right_hip = landmarks['right_hip']
        left_elbow = landmarks['left_elbow']
        right_elbow = landmarks['right_elbow']
        left_wrist = landmarks['left_wrist']
        right_wrist = landmarks['right_wrist']
        left_knee = landmarks['left_knee']
        right_knee = landmarks['right_knee']
        left_ankle = landmarks['left_ankle']
        right_ankle = landmarks['right_ankle']

        # Body height: nose to midpoint(ankles)
        ankle_mid = self.midpoint(left_ankle, right_ankle)
        body_height = self.calculate_distance(nose, ankle_mid)
        if body_height == 0:
            raise ValidationError('rejected', 'invalid_body_height', 'Body height could not be computed.')

        # Shoulder width
        shoulder_width = self.calculate_distance(left_shoulder, right_shoulder)
        # Hip width
        hip_width = self.calculate_distance(left_hip, right_hip)
        # Waist width: midpoint between shoulders and hips horizontally
        shoulder_mid = self.midpoint(left_shoulder, right_shoulder)
        hip_mid = self.midpoint(left_hip, right_hip)
        waist_mid = self.midpoint(shoulder_mid, hip_mid)
        waist_width = abs(shoulder_mid.x - hip_mid.x)
        # Torso length: shoulder_mid to hip_mid
        torso_length = self.calculate_distance(shoulder_mid, hip_mid)
        # Leg length: hip_mid to ankle_mid
        leg_length = self.calculate_distance(hip_mid, ankle_mid)
        # Arm length: shoulder to wrist (average left/right)
        left_arm_length = self.calculate_distance(left_shoulder, left_wrist)
        right_arm_length = self.calculate_distance(right_shoulder, right_wrist)
        arm_length = (left_arm_length + right_arm_length) / 2
        # Upper arm: shoulder to elbow (average left/right)
        left_upper_arm = self.calculate_distance(left_shoulder, left_elbow)
        right_upper_arm = self.calculate_distance(right_shoulder, right_elbow)
        upper_arm = (left_upper_arm + right_upper_arm) / 2
        # Forearm: elbow to wrist (average left/right)
        left_forearm = self.calculate_distance(left_elbow, left_wrist)
        right_forearm = self.calculate_distance(right_elbow, right_wrist)
        forearm = (left_forearm + right_forearm) / 2
        # Thigh: hip to knee (average left/right)
        left_thigh = self.calculate_distance(left_hip, left_knee)
        right_thigh = self.calculate_distance(right_hip, right_knee)
        thigh = (left_thigh + right_thigh) / 2
        # Calf: knee to ankle (average left/right)
        left_calf = self.calculate_distance(left_knee, left_ankle)
        right_calf = self.calculate_distance(right_knee, right_ankle)
        calf = (left_calf + right_calf) / 2

        # Normalize all measurements
        shoulder_width_n = shoulder_width / body_height
        hip_width_n = hip_width / body_height
        waist_width_n = waist_width / body_height
        torso_length_n = torso_length / body_height
        leg_length_n = leg_length / body_height
        arm_length_n = arm_length / body_height
        upper_arm_n = upper_arm / body_height
        forearm_n = forearm / body_height
        thigh_n = thigh / body_height
        calf_n = calf / body_height

        # Symmetry score
        symmetry_score = self.compute_symmetry([
            left_arm_length, right_arm_length,
            left_upper_arm, right_upper_arm,
            left_forearm, right_forearm,
            left_thigh, right_thigh,
            left_calf, right_calf
        ])

        return RawMeasurements(
            shoulder_width_n=shoulder_width_n,
            hip_width_n=hip_width_n,
            waist_width_n=waist_width_n,
            torso_length_n=torso_length_n,
            leg_length_n=leg_length_n,
            arm_length_n=arm_length_n,
            upper_arm_n=upper_arm_n,
            forearm_n=forearm_n,
            thigh_n=thigh_n,
            calf_n=calf_n,
            symmetry_score=symmetry_score
        )

    def compute_symmetry(self, pairs: list) -> float:
        """Compute symmetry score between left/right limb pairs."""
        diffs = []
        for i in range(0, len(pairs), 2):
            left = pairs[i]
            right = pairs[i+1]
            if left + right == 0:
                diffs.append(1.0)
            else:
                diffs.append(abs(left - right) / ((left + right) / 2))
        mean_diff = sum(diffs) / len(diffs) if diffs else 1.0
        symmetry = 1.0 - mean_diff
        return max(0.0, min(1.0, symmetry))

    def process_image(self, image: np.ndarray, pose_type: str) -> RawMeasurements:
        """Orchestrate the full body scan pipeline and return RawMeasurements."""
        if pose_type not in {'front', 'back'}:
            raise ValidationError('rejected', 'wrong_pose', 'Pose type must be "front" or "back".')
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.detect_pose(rgb_image)
        landmarks = self.extract_landmarks(results)
        self.validate_landmarks(landmarks)
        return self.compute_measurements(landmarks)
# Runs OpenCV/Mediapipe processing and extracts body measurements.
>>>>>>> 51405a0d51f5774366816b6c3934d7d71bc5016d
