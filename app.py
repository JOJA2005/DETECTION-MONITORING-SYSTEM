"""
Main Flask application for Smart Office Monitoring System
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
from database.models import db
from modules.database_module import DatabaseManager
from modules.vision_module import VisionSystem
from modules.training_module import FaceTrainer
from modules.action_module import ActionDetector
from config import Config
import cv2
import os
from datetime import datetime
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
Config.init_app()

# Initialize database
db.init_app(app)

# Initialize modules
vision_system = VisionSystem()
face_trainer = FaceTrainer()
action_detector = ActionDetector()

# Load trained model if exists
if face_trainer.load_model():
    vision_system.set_recognizer(face_trainer.get_recognizer())
    print("Loaded existing face recognition model")

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created")

# ==================== Authentication Decorator ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Authentication Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect(url_for('login'))

# ==================== Dashboard Routes ====================

@app.route('/')
@login_required
def dashboard():
    """Main monitoring dashboard"""
    employees = DatabaseManager.get_all_employees()
    current_attendance = DatabaseManager.get_current_attendance()
    recent_activity = DatabaseManager.get_recent_activity(limit=10)
    
    stats = {
        'total_employees': len(employees),
        'currently_inside': len(current_attendance),
        'today_entries': len(DatabaseManager.get_daily_attendance())
    }
    
    return render_template('dashboard.html', 
                         stats=stats,
                         current_attendance=current_attendance,
                         recent_activity=recent_activity)

@app.route('/api/current_attendance')
@login_required
def get_current_attendance():
    """API endpoint for live attendance updates"""
    current = DatabaseManager.get_current_attendance()
    return jsonify({'success': True, 'data': current})

@app.route('/api/recent_activity')
@login_required
def get_recent_activity():
    """API endpoint for recent activity"""
    activity = DatabaseManager.get_recent_activity(limit=10)
    return jsonify({'success': True, 'data': activity})

# ==================== Video Streaming ====================

def generate_frames():
    """Generate frames for video streaming"""
    while vision_system.is_running:
        frame = vision_system.get_current_frame()
        
        if frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
@login_required
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# ==================== Camera Control ====================

@app.route('/api/start_monitoring', methods=['POST'])
@login_required
def start_monitoring():
    """Start camera monitoring"""
    if vision_system.start_monitoring_thread():
        return jsonify({'success': True, 'message': 'Monitoring started'})
    return jsonify({'success': False, 'error': 'Failed to start monitoring'})

@app.route('/api/stop_monitoring', methods=['POST'])
@login_required
def stop_monitoring():
    """Stop camera monitoring"""
    vision_system.stop_camera()
    return jsonify({'success': True, 'message': 'Monitoring stopped'})

# ==================== Employee Management Routes ====================

@app.route('/employees')
@login_required
def employees():
    """Employee management page"""
    all_employees = DatabaseManager.get_all_employees()
    return render_template('employees.html', employees=all_employees)

@app.route('/register_employee')
@login_required
def register_employee():
    """Employee registration page"""
    return render_template('register_employee.html')

@app.route('/api/add_employee', methods=['POST'])
@login_required
def add_employee():
    """Add new employee"""
    try:
        name = request.form.get('name')
        department = request.form.get('department')
        
        if not name or not department:
            return jsonify({'success': False, 'error': 'Name and department are required'})
        
        # Create temporary employee record to get ID
        temp_path = f"employee_temp_{datetime.now().timestamp()}"
        result = DatabaseManager.add_employee(name, department, temp_path)
        
        if not result['success']:
            return jsonify(result)
        
        employee_id = result['employee']['id']
        
        # Collect face samples
        sample_result = face_trainer.collect_face_samples(
            employee_id, 
            name, 
            num_samples=Config.FACE_SAMPLES_PER_EMPLOYEE
        )
        
        if sample_result['success']:
            # Update employee with correct face data path
            employee = DatabaseManager.get_employee_by_id(employee_id)
            employee.face_data_path = sample_result['folder_path']
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Employee {name} registered successfully',
                'employee_id': employee_id
            })
        else:
            # Delete employee if face collection failed
            DatabaseManager.delete_employee(employee_id)
            return jsonify({'success': False, 'error': sample_result.get('error', 'Face collection failed')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_employee/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    """Delete employee"""
    result = DatabaseManager.delete_employee(employee_id)
    return jsonify(result)

@app.route('/api/train_model', methods=['POST'])
@login_required
def train_model():
    """Train face recognition model"""
    result = face_trainer.train_model()
    
    if result['success']:
        # Reload model in vision system
        if face_trainer.load_model():
            vision_system.set_recognizer(face_trainer.get_recognizer())
    
    return jsonify(result)

# ==================== Reports Routes ====================

@app.route('/reports')
@login_required
def reports():
    """Reports and analytics page"""
    return render_template('reports.html')

@app.route('/api/daily_report')
@login_required
def daily_report():
    """Get daily attendance report"""
    date_str = request.args.get('date')
    
    if date_str:
        attendance = DatabaseManager.get_daily_attendance(date_str)
    else:
        attendance = DatabaseManager.get_daily_attendance()
    
    return jsonify({'success': True, 'data': attendance})

@app.route('/api/export_csv')
@login_required
def export_csv():
    """Export attendance data to CSV"""
    import csv
    from io import StringIO
    
    date_str = request.args.get('date')
    attendance = DatabaseManager.get_daily_attendance(date_str)
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Employee Name', 'Department', 'Entry Time', 'Exit Time', 'Work Duration', 'Action', 'Status'])
    
    # Write data
    for record in attendance:
        writer.writerow([
            record['employee_name'],
            record['department'],
            record['entry_time'],
            record['exit_time'] or 'N/A',
            record['work_duration'] or 'N/A',
            record['action'],
            record['status']
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_{date_str or "today"}.csv'}
    )

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('login.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('login.html', error='Internal server error'), 500

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
