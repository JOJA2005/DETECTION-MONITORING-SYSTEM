# Smart Office Monitoring System

A full-stack AI-powered office monitoring system using Flask, OpenCV, and computer vision for real-time employee face recognition, attendance tracking, and basic action detection.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **Face Detection & Recognition**: Real-time face detection using OpenCV Haar Cascades and LBPH face recognition
- **Automated Attendance**: Automatic entry/exit logging with intelligent cooldown to prevent duplicates
- **Action Detection**: Basic pose-based action recognition (sitting, standing, walking, idle) using MediaPipe
- **Live Monitoring**: Real-time camera feed with face annotations and detection overlays
- **Web Dashboard**: Professional dark-themed web interface for monitoring and management

### Admin Features
- Employee registration with automated face sample collection
- Face recognition model training
- Employee management (add/delete)
- Real-time attendance monitoring
- Comprehensive reports and analytics
- CSV export functionality

### Security
- Admin authentication system
- Session-based access control
- Protected routes

## 📁 Project Structure

```
DETECTION MONITORING SYSTEM/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── modules/
│   ├── __init__.py
│   ├── vision_module.py           # Face detection & recognition
│   ├── action_module.py           # Pose estimation & action detection
│   ├── database_module.py         # Database operations
│   └── training_module.py         # Face model training
├── database/
│   ├── __init__.py
│   ├── models.py                  # SQLAlchemy models
│   └── office_monitoring.db       # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css              # Professional dark theme
│   ├── js/
│   │   └── dashboard.js           # Frontend logic
│   └── uploads/
│       └── face_data/             # Employee face images (auto-generated)
├── templates/
│   ├── base.html                  # Base template
│   ├── login.html                 # Admin login
│   ├── dashboard.html             # Main monitoring dashboard
│   ├── employees.html             # Employee management
│   ├── reports.html               # Reports & analytics
│   └── register_employee.html     # Employee registration
└── trained_models/
    └── face_recognizer.yml        # Trained LBPH model (auto-generated)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam/camera access
- Windows/Linux/macOS

### Step 1: Clone or Download
Download the project to your local machine.

### Step 2: Create Virtual Environment
```bash
# Navigate to project directory
cd "DETECTION MONITORING SYSTEM"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📖 Usage Guide

### First Time Setup

1. **Login**
   - Navigate to `http://localhost:5000`
   - Default credentials:
     - Username: `admin`
     - Password: `admin123`

2. **Register Employees**
   - Go to "Employees" page
   - Click "Add Employee"
   - Enter employee name and department
   - Click "Register & Capture Face"
   - Position your face in front of the camera
   - The system will automatically capture 50 face samples
   - Press 'Q' to quit if needed

3. **Train the Model**
   - After registering employees, go to "Employees" page
   - Click "Train Model" button
   - Wait for training to complete
   - The model is now ready for recognition

4. **Start Monitoring**
   - Go to "Dashboard"
   - Click "Start Monitoring"
   - The live camera feed will appear
   - Recognized employees will be automatically logged

### Daily Operations

#### Monitoring Dashboard
- View live camera feed with face detection
- See current employees inside the office
- Monitor recent activity in real-time
- View statistics (total employees, currently inside, today's entries)

#### Employee Management
- Add new employees
- Delete employees
- Retrain model after adding/removing employees

#### Reports & Analytics
- Select date to view attendance
- See entry/exit times
- View work duration
- Export data to CSV

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Camera settings
CAMERA_INDEX = 0  # Change if using external camera

# Detection settings
RECOGNITION_CONFIDENCE_THRESHOLD = 70  # Lower = stricter
ENTRY_EXIT_COOLDOWN_MINUTES = 5  # Duplicate prevention time
```

## 🎯 How It Works

### Face Recognition Pipeline
1. **Detection**: Haar Cascade detects faces in video frames
2. **Recognition**: LBPH algorithm identifies employees
3. **Logging**: Entry/exit events are logged to database
4. **Cooldown**: 5-minute cooldown prevents duplicate entries

### Action Detection
1. **Pose Estimation**: MediaPipe extracts body landmarks
2. **Angle Calculation**: Joint angles determine posture
3. **Classification**: Actions classified as sitting/standing/walking/idle
4. **Logging**: Actions stored with attendance records

### Entry/Exit Logic
- **Entry**: First detection of the day or after cooldown period
- **Exit**: No detection for cooldown period (5 minutes)
- **Duplicate Prevention**: Ignores detections within cooldown window

## 📊 Database Schema

### Employees Table
- `id`: Primary key
- `name`: Employee name (unique)
- `department`: Department name
- `face_data_path`: Path to face images
- `created_at`: Registration timestamp

### Attendance Table
- `id`: Primary key
- `employee_id`: Foreign key to Employee
- `entry_time`: Entry timestamp
- `exit_time`: Exit timestamp (nullable)
- `action`: Detected action
- `date`: Date of attendance
- `status`: 'inside' or 'exited'

## 🔍 Troubleshooting

### Camera Not Working
- Ensure no other application is using the camera
- Check camera permissions
- Try changing `CAMERA_INDEX` in config.py

### Face Not Recognized
- Ensure model is trained after adding employees
- Check lighting conditions
- Increase `RECOGNITION_CONFIDENCE_THRESHOLD` in config.py
- Recapture face samples with better lighting

### Performance Issues
- Reduce camera resolution in config.py
- Close other applications
- Ensure adequate CPU/RAM

## 🚀 Scalability Suggestions

### For Production Deployment

1. **Database**: Migrate to PostgreSQL or MySQL
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dbname'
   ```

2. **Face Recognition**: Upgrade to deep learning models
   - FaceNet
   - ArcFace
   - DeepFace

3. **Action Detection**: Advanced activity recognition
   - Temporal Segment Networks (TSN)
   - I3D (Inflated 3D ConvNet)

4. **Real-time Updates**: Implement WebSockets
   - Flask-SocketIO
   - Real-time push notifications

5. **Multi-Camera Support**: Extend to multiple feeds
   - Camera management system
   - Distributed processing

6. **Cloud Storage**: Store face data in cloud
   - AWS S3
   - Azure Blob Storage
   - Google Cloud Storage

7. **Containerization**: Docker deployment
   ```dockerfile
   FROM python:3.8
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["python", "app.py"]
   ```

8. **API Development**: RESTful API for mobile apps
   - Flask-RESTful
   - JWT authentication
   - API documentation with Swagger

9. **Analytics**: Advanced reporting
   - Data visualization (Chart.js, D3.js)
   - Predictive analytics
   - Attendance patterns

10. **Security Enhancements**
    - OAuth2 authentication
    - Role-based access control (RBAC)
    - Encrypted database
    - HTTPS/SSL

## 📝 API Endpoints

### Authentication
- `POST /login` - Admin login
- `GET /logout` - Logout

### Dashboard
- `GET /` - Main dashboard
- `GET /api/current_attendance` - Current attendance (JSON)
- `GET /api/recent_activity` - Recent activity (JSON)
- `GET /video_feed` - Video stream

### Camera Control
- `POST /api/start_monitoring` - Start camera
- `POST /api/stop_monitoring` - Stop camera

### Employee Management
- `GET /employees` - Employee list page
- `GET /register_employee` - Registration form
- `POST /api/add_employee` - Add employee
- `POST /api/delete_employee/<id>` - Delete employee
- `POST /api/train_model` - Train recognition model

### Reports
- `GET /reports` - Reports page
- `GET /api/daily_report?date=YYYY-MM-DD` - Daily report (JSON)
- `GET /api/export_csv?date=YYYY-MM-DD` - Export CSV

## 🛡️ Security Notes

- Change default admin credentials in production
- Use environment variables for sensitive data
- Implement HTTPS for production deployment
- Regular database backups
- Secure face data storage

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Development

### Adding New Features
1. Create new module in `modules/`
2. Add routes in `app.py`
3. Create templates in `templates/`
4. Update CSS/JS as needed

### Testing
- Test face recognition with different lighting
- Verify entry/exit logic
- Test with multiple employees
- Check performance under load

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for pose estimation
- Flask for web framework
- SQLAlchemy for database ORM

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review configuration settings
3. Ensure all dependencies are installed
4. Check camera permissions

---

**Built with ❤️ for smart office management**
