"""
Database operations module for Smart Office Monitoring System
"""
from database.models import db, Employee, Attendance
from datetime import datetime, timedelta, date
from sqlalchemy import and_

class DatabaseManager:
    """Handles all database operations"""
    
    @staticmethod
    def init_db(app):
        """Initialize database with app context"""
        with app.app_context():
            db.create_all()
            print("Database initialized successfully!")
    
    # ==================== Employee Operations ====================
    
    @staticmethod
    def add_employee(name, department, face_data_path):
        """Add a new employee to the database"""
        try:
            employee = Employee(
                name=name,
                department=department,
                face_data_path=face_data_path
            )
            db.session.add(employee)
            db.session.commit()
            return {'success': True, 'employee': employee.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_all_employees():
        """Retrieve all employees"""
        try:
            employees = Employee.query.all()
            return [emp.to_dict() for emp in employees]
        except Exception as e:
            return []
    
    @staticmethod
    def get_employee_by_id(employee_id):
        """Get employee by ID"""
        return Employee.query.get(employee_id)
    
    @staticmethod
    def get_employee_by_name(name):
        """Get employee by name"""
        return Employee.query.filter_by(name=name).first()
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete an employee and all related attendance records"""
        try:
            employee = Employee.query.get(employee_id)
            if employee:
                db.session.delete(employee)
                db.session.commit()
                return {'success': True}
            return {'success': False, 'error': 'Employee not found'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== Attendance Operations ====================
    
    @staticmethod
    def log_entry(employee_id, action='Unknown'):
        """Log employee entry"""
        try:
            # Check if employee already has an active entry today
            today = date.today()
            existing = Attendance.query.filter(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == today,
                    Attendance.status == 'inside'
                )
            ).first()
            
            # Check cooldown period (prevent duplicate entries within X minutes)
            if existing:
                time_diff = datetime.utcnow() - existing.entry_time
                if time_diff < timedelta(minutes=5):  # 5-minute cooldown
                    return {'success': False, 'error': 'Entry already logged recently'}
            
            # If exists and past cooldown, mark as exit first
            if existing:
                existing.exit_time = datetime.utcnow()
                existing.status = 'exited'
            
            # Create new entry
            attendance = Attendance(
                employee_id=employee_id,
                entry_time=datetime.utcnow(),
                action=action,
                date=today,
                status='inside'
            )
            db.session.add(attendance)
            db.session.commit()
            return {'success': True, 'attendance': attendance.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def log_exit(employee_id):
        """Log employee exit"""
        try:
            today = date.today()
            attendance = Attendance.query.filter(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == today,
                    Attendance.status == 'inside'
                )
            ).first()
            
            if attendance:
                attendance.exit_time = datetime.utcnow()
                attendance.status = 'exited'
                db.session.commit()
                return {'success': True, 'attendance': attendance.to_dict()}
            return {'success': False, 'error': 'No active entry found'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_action(employee_id, action):
        """Update the current action for an employee"""
        try:
            today = date.today()
            attendance = Attendance.query.filter(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == today,
                    Attendance.status == 'inside'
                )
            ).first()
            
            if attendance:
                attendance.action = action
                db.session.commit()
                return {'success': True}
            return {'success': False, 'error': 'No active entry found'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_current_attendance():
        """Get all employees currently inside the office"""
        try:
            today = date.today()
            current = Attendance.query.filter(
                and_(
                    Attendance.date == today,
                    Attendance.status == 'inside'
                )
            ).all()
            return [att.to_dict() for att in current]
        except Exception as e:
            return []
    
    @staticmethod
    def get_daily_attendance(target_date=None):
        """Get attendance for a specific date"""
        try:
            if target_date is None:
                target_date = date.today()
            elif isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            attendance = Attendance.query.filter_by(date=target_date).all()
            return [att.to_dict() for att in attendance]
        except Exception as e:
            return []
    
    @staticmethod
    def get_employee_work_duration(employee_id, target_date=None):
        """Calculate total work duration for an employee on a specific date"""
        try:
            if target_date is None:
                target_date = date.today()
            elif isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            records = Attendance.query.filter(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == target_date
                )
            ).all()
            
            total_seconds = 0
            for record in records:
                if record.exit_time:
                    duration = record.exit_time - record.entry_time
                    total_seconds += duration.total_seconds()
            
            hours = total_seconds / 3600
            return f"{int(hours)}h {int((hours % 1) * 60)}m"
        except Exception as e:
            return "0h 0m"
    
    @staticmethod
    def get_recent_activity(limit=10):
        """Get recent attendance activity"""
        try:
            recent = Attendance.query.order_by(Attendance.entry_time.desc()).limit(limit).all()
            return [att.to_dict() for att in recent]
        except Exception as e:
            return []
