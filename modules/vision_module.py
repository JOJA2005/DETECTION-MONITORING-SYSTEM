"""
Vision module for face detection and recognition
"""
import cv2
import threading
import time
import numpy as np
import face_recognition
from datetime import datetime, timedelta
from config import Config
from modules.database_module import DatabaseManager

class VisionSystem:
    """Handles real-time face detection and recognition"""
    
    def __init__(self, recognizer=None):
        self.recognizer = recognizer
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
        
        # Track last seen times to implement entry/exit logic
        self.last_seen = {}  # {employee_id: datetime}
        self.current_status = {}  # {employee_id: 'inside' or 'exited'}
    
    def set_recognizer(self, recognizer):
        """Set the trained recognizer"""
        self.recognizer = recognizer
    
    def start_camera(self):
        """Initialize and start camera"""
        try:
            self.camera = cv2.VideoCapture(Config.CAMERA_INDEX)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
            
            if not self.camera.isOpened():
                return False
            
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera and cleanup"""
        self.is_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def detect_faces(self, frame):
        """
        Detect faces in frame
        Returns: (face_locations, rgb_frame)
        face_locations format: (top, right, bottom, left)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')
        return face_locations, rgb_frame
    
    def recognize_face(self, rgb_frame, face_location):
        """
        Recognize face using trained model
        Returns: (employee_id, confidence) or (None, None)
        """
        if self.recognizer is None:
            return None, None

        try:
            face_encs = face_recognition.face_encodings(rgb_frame, [face_location])
            if not face_encs:
                return None, None

            face_encoding = face_encs[0]
            known_encodings = self.recognizer.get('encodings') if isinstance(self.recognizer, dict) else None
            known_labels = self.recognizer.get('labels') if isinstance(self.recognizer, dict) else None

            if known_encodings is None or known_labels is None or len(known_encodings) == 0:
                return None, None

            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if distances.size == 0:
                return None, None

            best_idx = int(np.argmin(distances))
            best_distance = float(distances[best_idx])

            if best_distance <= getattr(Config, 'FACE_RECOGNITION_TOLERANCE', 0.6):
                return int(known_labels[best_idx]), best_distance

            return None, best_distance
        except Exception as e:
            print(f"Recognition error: {e}")
            return None, None
    
    def handle_detection(self, employee_id, employee_name):
        """
        Handle entry/exit logic when a face is detected
        """
        current_time = datetime.utcnow()
        
        # Check if this is a new detection or re-detection
        if employee_id in self.last_seen:
            time_diff = current_time - self.last_seen[employee_id]
            
            # If seen within cooldown period, just update last_seen
            if time_diff < timedelta(minutes=Config.ENTRY_EXIT_COOLDOWN_MINUTES):
                self.last_seen[employee_id] = current_time
                return None
            
            # If not seen for a while, this is a re-entry
            if employee_id in self.current_status and self.current_status[employee_id] == 'exited':
                # Log new entry
                result = DatabaseManager.log_entry(employee_id)
                if result['success']:
                    self.current_status[employee_id] = 'inside'
                    self.last_seen[employee_id] = current_time
                    return f"{employee_name} has entered the office"
        else:
            # First time seeing this employee today
            result = DatabaseManager.log_entry(employee_id)
            if result['success']:
                self.current_status[employee_id] = 'inside'
                self.last_seen[employee_id] = current_time
                return f"{employee_name} has entered the office"
        
        # Update last seen time
        self.last_seen[employee_id] = current_time
        return None
    
    def check_exits(self):
        """
        Check for employees who haven't been seen recently and mark as exited
        """
        current_time = datetime.utcnow()
        exit_threshold = timedelta(minutes=Config.ENTRY_EXIT_COOLDOWN_MINUTES)
        
        for employee_id, last_time in list(self.last_seen.items()):
            if employee_id in self.current_status and self.current_status[employee_id] == 'inside':
                time_diff = current_time - last_time
                
                # If not seen for threshold time, mark as exited
                if time_diff > exit_threshold:
                    result = DatabaseManager.log_exit(employee_id)
                    if result['success']:
                        self.current_status[employee_id] = 'exited'
                        employee = DatabaseManager.get_employee_by_id(employee_id)
                        if employee:
                            print(f"{employee.name} has exited the office")
    
    def process_frame(self):
        """
        Process a single frame: detect and recognize faces
        Returns: processed frame with annotations
        """
        if not self.camera or not self.is_running:
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            return None
        
        # Detect faces
        face_locations, rgb_frame = self.detect_faces(frame)
        
        messages = []
        
        for (top, right, bottom, left) in face_locations:
            # Recognize face
            employee_id, confidence = self.recognize_face(rgb_frame, (top, right, bottom, left))
            
            if employee_id is not None:
                # Get employee details
                employee = DatabaseManager.get_employee_by_id(employee_id)
                
                if employee:
                    # Handle entry/exit
                    message = self.handle_detection(employee_id, employee.name)
                    if message:
                        messages.append(message)
                    
                    # Draw green rectangle for recognized face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Display name and confidence
                    label = f"{employee.name} ({confidence:.2f})"
                    cv2.putText(frame, label, (left, top-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    # Unknown employee ID
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (left, top-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # Unrecognized face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Store current frame
        with self.lock:
            self.current_frame = frame.copy()
        
        # Print messages
        for msg in messages:
            print(msg)
        
        return frame
    
    def get_current_frame(self):
        """Get the current processed frame"""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def run_monitoring(self):
        """Run continuous monitoring in a loop"""
        while self.is_running:
            self.process_frame()
            self.check_exits()
            time.sleep(0.03)  # ~30 FPS
    
    def start_monitoring_thread(self):
        """Start monitoring in a background thread"""
        if not self.is_running:
            if self.start_camera():
                thread = threading.Thread(target=self.run_monitoring, daemon=True)
                thread.start()
                return True
        return False
