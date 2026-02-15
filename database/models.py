"""
Database models for Smart Office Monitoring System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    face_data_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with attendance
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    def to_dict(self):
        """Convert employee to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'face_data_path': self.face_data_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Attendance(db.Model):
    """Attendance model for tracking employee entry/exit and actions"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    action = db.Column(db.String(50), default='Unknown')  # sitting, standing, walking, idle
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), default='inside')  # inside or exited
    
    def __repr__(self):
        return f'<Attendance {self.employee_id} - {self.entry_time}>'
    
    def to_dict(self):
        """Convert attendance record to dictionary"""
        work_duration = None
        if self.exit_time:
            duration = self.exit_time - self.entry_time
            hours = duration.total_seconds() / 3600
            work_duration = f"{int(hours)}h {int((hours % 1) * 60)}m"
        
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else 'Unknown',
            'department': self.employee.department if self.employee else 'Unknown',
            'entry_time': self.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': self.exit_time.strftime('%Y-%m-%d %H:%M:%S') if self.exit_time else None,
            'action': self.action,
            'date': self.date.strftime('%Y-%m-%d'),
            'status': self.status,
            'work_duration': work_duration
        }
