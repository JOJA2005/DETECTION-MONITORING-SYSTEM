"""
Training module for face recognition model
"""
import cv2
import os
import numpy as np
from config import Config

class FaceTrainer:
    """Handles training of face recognition model"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.model_path = os.path.join(Config.TRAINED_MODELS_FOLDER, 'face_recognizer.yml')
    
    def collect_face_samples(self, employee_id, employee_name, num_samples=50):
        """
        Collect face samples for training
        Returns: dict with success status and message
        """
        try:
            # Create directory for employee face data
            employee_folder = os.path.join(Config.UPLOAD_FOLDER, f"employee_{employee_id}")
            os.makedirs(employee_folder, exist_ok=True)
            
            # Initialize camera
            camera = cv2.VideoCapture(Config.CAMERA_INDEX)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
            
            if not camera.isOpened():
                return {'success': False, 'error': 'Cannot access camera'}
            
            count = 0
            print(f"Collecting {num_samples} face samples for {employee_name}...")
            print("Please look at the camera and move your head slightly...")
            
            while count < num_samples:
                ret, frame = camera.read()
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=Config.FACE_DETECTION_SCALE_FACTOR,
                    minNeighbors=Config.FACE_DETECTION_MIN_NEIGHBORS,
                    minSize=Config.FACE_DETECTION_MIN_SIZE
                )
                
                for (x, y, w, h) in faces:
                    count += 1
                    # Save face image
                    face_img = gray[y:y+h, x:x+w]
                    face_path = os.path.join(employee_folder, f"face_{count}.jpg")
                    cv2.imwrite(face_path, face_img)
                    
                    # Draw rectangle on frame for visual feedback
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Sample {count}/{num_samples}", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                cv2.imshow('Collecting Face Samples - Press Q to quit', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            camera.release()
            cv2.destroyAllWindows()
            
            if count >= num_samples:
                return {
                    'success': True,
                    'message': f'Successfully collected {count} samples',
                    'folder_path': employee_folder
                }
            else:
                return {
                    'success': False,
                    'error': f'Only collected {count} samples, need {num_samples}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def prepare_training_data(self):
        """
        Prepare training data from all employee face folders
        Returns: faces array, labels array, and label-to-name mapping
        """
        faces = []
        labels = []
        label_names = {}
        
        try:
            # Iterate through all employee folders
            for folder_name in os.listdir(Config.UPLOAD_FOLDER):
                folder_path = os.path.join(Config.UPLOAD_FOLDER, folder_name)
                
                if not os.path.isdir(folder_path):
                    continue
                
                # Extract employee ID from folder name (employee_X)
                try:
                    employee_id = int(folder_name.split('_')[1])
                except:
                    continue
                
                # Read all face images in the folder
                for image_name in os.listdir(folder_path):
                    if not image_name.endswith('.jpg'):
                        continue
                    
                    image_path = os.path.join(folder_path, image_name)
                    face_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    
                    if face_img is not None:
                        faces.append(face_img)
                        labels.append(employee_id)
                        label_names[employee_id] = folder_name
            
            return faces, labels, label_names
            
        except Exception as e:
            print(f"Error preparing training data: {e}")
            return [], [], {}
    
    def train_model(self):
        """
        Train the face recognition model
        Returns: dict with success status and message
        """
        try:
            faces, labels, label_names = self.prepare_training_data()
            
            if len(faces) == 0:
                return {'success': False, 'error': 'No training data found'}
            
            print(f"Training model with {len(faces)} face samples from {len(set(labels))} employees...")
            
            # Train the recognizer
            self.recognizer.train(faces, np.array(labels))
            
            # Save the model
            self.recognizer.save(self.model_path)
            
            return {
                'success': True,
                'message': f'Model trained successfully with {len(faces)} samples',
                'num_employees': len(set(labels)),
                'model_path': self.model_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_model(self):
        """
        Load existing trained model
        Returns: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.model_path):
                self.recognizer.read(self.model_path)
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_recognizer(self):
        """Get the trained recognizer"""
        return self.recognizer
