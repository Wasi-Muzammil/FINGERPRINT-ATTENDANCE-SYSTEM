import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_name='attendance.db'):
        self.db_name = db_name
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    # ==================== USER OPERATIONS ====================
    
    def add_user(self, name, department, fingerprint_id=None, image_path=None):
        """Add a new user to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, department, fingerprint_id, image_path) VALUES (?, ?, ?, ?)",
                (name, department, fingerprint_id, image_path)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return True, user_id
        except sqlite3.IntegrityError as e:
            return False, str(e)
        finally:
            conn.close()
    
    def get_all_users(self):
        """Get all users from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY name")
        users = cursor.fetchall()
        conn.close()
        return users
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def update_user(self, user_id, name=None, department=None, fingerprint_id=None):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if department:
            updates.append("department = ?")
            params.append(department)
        if fingerprint_id is not None:
            updates.append("fingerprint_id = ?")
            params.append(fingerprint_id)
        
        if updates:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_user(self, user_id):
        """Delete user and their attendance records"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user image path to delete file
        cursor.execute("SELECT image_path FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            image_path = result[0]
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete user (CASCADE will handle attendance)
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    
    def delete_fingerprint(self, user_id):
        """Delete only fingerprint ID from user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET fingerprint_id = NULL WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    def add_attendance(self, user_id, status, timestamp=None):
        """Add attendance record"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (user_id, timestamp, status) VALUES (?, ?, ?)",
            (user_id, timestamp, status)
        )
        conn.commit()
        conn.close()
        return True
    
    def get_attendance_by_date(self, date):
        """Get all attendance records for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, u.name, u.department, a.timestamp, a.status
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.timestamp) = ?
            ORDER BY a.timestamp
        """, (date,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_attendance_by_date_range(self, start_date, end_date):
        """Get attendance records for a date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, u.name, u.department, a.timestamp, a.status
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE DATE(a.timestamp) BETWEEN ? AND ?
            ORDER BY a.timestamp
        """, (start_date, end_date))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_user_attendance(self, user_id):
        """Get all attendance records for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.timestamp, a.status
            FROM attendance a
            WHERE a.user_id = ?
            ORDER BY a.timestamp DESC
        """, (user_id,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_attendance_summary(self, start_date, end_date):
        """Get attendance summary with working hours calculation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                u.id,
                u.name,
                u.department,
                DATE(a.timestamp) as date,
                MIN(CASE WHEN a.status = 'IN' THEN a.timestamp END) as check_in,
                MAX(CASE WHEN a.status = 'OUT' THEN a.timestamp END) as check_out
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id
            WHERE DATE(a.timestamp) BETWEEN ? AND ?
            GROUP BY u.id, u.name, u.department, DATE(a.timestamp)
            ORDER BY date, u.name
        """, (start_date, end_date))
        records = cursor.fetchall()
        conn.close()
        return records