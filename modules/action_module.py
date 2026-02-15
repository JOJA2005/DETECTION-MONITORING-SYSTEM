"""
Action detection module using pose estimation
"""
import cv2
import mediapipe as mp
import numpy as np

class ActionDetector:
    """Detects basic actions using MediaPipe Pose"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.previous_positions = {}
        self.movement_threshold = 0.05
    
    def calculate_angle(self, point1, point2, point3):
        """
        Calculate angle between three points
        Used for determining sitting/standing posture
        """
        a = np.array([point1.x, point1.y])
        b = np.array([point2.x, point2.y])
        c = np.array([point3.x, point3.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        
        return angle
    
    def detect_movement(self, landmarks, person_id):
        """
        Detect if person is moving (walking) or stationary
        """
        # Use hip position as reference point
        current_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        current_pos = (current_hip.x, current_hip.y)
        
        if person_id in self.previous_positions:
            prev_pos = self.previous_positions[person_id]
            distance = np.sqrt((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)
            
            self.previous_positions[person_id] = current_pos
            
            if distance > self.movement_threshold:
                return True  # Moving
            else:
                return False  # Stationary
        else:
            self.previous_positions[person_id] = current_pos
            return False
    
    def classify_action(self, landmarks, person_id=0):
        """
        Classify action based on pose landmarks
        Returns: 'sitting', 'standing', 'walking', or 'idle'
        """
        try:
            # Get key landmarks
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
            
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value]
            
            # Calculate angles
            left_hip_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            
            # Detect movement
            is_moving = self.detect_movement(landmarks, person_id)
            
            # Classify based on angles and movement
            if is_moving:
                return 'walking'
            elif left_hip_angle < 100 and left_knee_angle < 100:
                # Both hip and knee bent significantly
                return 'sitting'
            elif left_hip_angle > 160 and left_knee_angle > 160:
                # Both hip and knee relatively straight
                return 'standing'
            else:
                return 'idle'
                
        except Exception as e:
            print(f"Action classification error: {e}")
            return 'unknown'
    
    def process_frame(self, frame):
        """
        Process frame and detect pose/action
        Returns: (action, annotated_frame)
        """
        try:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            action = 'unknown'
            
            if results.pose_landmarks:
                # Draw pose landmarks on frame
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
                
                # Classify action
                action = self.classify_action(results.pose_landmarks.landmark)
                
                # Display action on frame
                cv2.putText(frame, f"Action: {action.upper()}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            return action, frame
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return 'unknown', frame
    
    def release(self):
        """Release resources"""
        self.pose.close()
