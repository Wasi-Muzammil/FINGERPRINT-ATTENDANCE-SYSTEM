
"""
Database Manager for PostgreSQL
Uses SQLAlchemy ORM - Models aligned with FastAPI backend
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean,Numeric,Null
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from datetime import datetime
import pandas as pd
from typing import Optional, List

Base = declarative_base()

# ==================== MODELS (Aligned with Backend) ====================

class DeviceStatusDB(Base):
    """Device status model - matches backend exactly"""
    __tablename__ = "device_status"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UserInformationDB(Base):
    """User information model - matches backend exactly"""
    __tablename__ = "user_information"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    slot_id = Column(PG_ARRAY(Integer), nullable=False)  # Array of slot IDs
    date = Column(String, nullable=False)  # DD/MM format
    time = Column(String, nullable=False)  # HH:MM:SS format
    salary = Column(Numeric(precision=10, scale=2),nullable=True,default= Null)
    created_at = Column(DateTime, default=datetime.now)

class AttendanceRecordDB(Base):
    """Attendance record model - matches backend exactly"""
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    slot_id = Column(PG_ARRAY(Integer), nullable=False)  # Array of slot IDs
    date = Column(String, nullable=False, index=True)  # DD/MM format
    checked_in_time = Column(String, nullable=True)  # HH:MM format
    checked_out_time = Column(String, nullable=True)  # HH:MM format
    is_present = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AdminInformationDB(Base):
    """Admin information model - NEW"""
    __tablename__ = "admin_information"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # Hashed password
    role = Column(String, nullable=False, default="admin")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# ==================== DATABASE MANAGER ====================

class DatabaseManager:
    """Manages all database operations using SQLAlchemy ORM"""
    
    def __init__(self, database_url: str):
        """Initialize database connection"""
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # ==================== USER OPERATIONS ====================
    
    def get_all_users(self) -> Optional[pd.DataFrame]:
        """
        Fetch all users from UserInformationDB
        Returns: pandas DataFrame or None
        """
        try:
            session = self.get_session()
            
            users = session.query(UserInformationDB).order_by(
                UserInformationDB.created_at.desc()
            ).all()
            
            session.close()
            
            if not users:
                return pd.DataFrame()
            
            # Convert to DataFrame
            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'name': user.name,
                    'user_id': user.user_id,
                    'slot_id': user.slot_id or [],
                    'date': user.date,
                    'time': user.time,
                    'created_at': user.created_at
                })
            
            return pd.DataFrame(users_data)
            
        except Exception as e:
            print(f"Error fetching users: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by user_id"""
        try:
            session = self.get_session()
            
            user = session.query(UserInformationDB).filter(
                UserInformationDB.user_id == user_id
            ).first()
            
            session.close()
            
            if not user:
                return None
            
            return {
                'id': user.id,
                'name': user.name,
                'user_id': user.user_id,
                'slot_id': user.slot_id or [],
                'date': user.date,
                'time': user.time,
                'created_at': user.created_at
            }
            
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    def get_attendance_by_date(self, date_str: str) -> Optional[pd.DataFrame]:
        """
        Get all attendance records for a specific date (DD/MM format)
        """
        try:
            session = self.get_session()
            
            records = session.query(AttendanceRecordDB).filter(
                AttendanceRecordDB.date == date_str
            ).order_by(AttendanceRecordDB.checked_in_time).all()
            
            session.close()
            
            if not records:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'name': record.name,
                    'user_id': record.user_id,
                    'slot_id': record.slot_id or [],
                    'date': record.date,
                    'checked_in_time': record.checked_in_time,
                    'checked_out_time': record.checked_out_time,
                    'is_present': record.is_present,
                    'created_at': record.created_at
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Error fetching attendance by date: {e}")
            return None
    
    def get_attendance_range(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get attendance records for a date range
        Note: Dates in DB are strings (DD/MM format), so we fetch all and filter
        """
        try:
            session = self.get_session()
            
            # Get all records and filter in Python (since dates are strings)
            all_records = session.query(AttendanceRecordDB).order_by(
                AttendanceRecordDB.date, AttendanceRecordDB.checked_in_time
            ).all()
            
            session.close()
            
            if not all_records:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for record in all_records:
                data.append({
                    'id': record.id,
                    'name': record.name,
                    'user_id': record.user_id,
                    'slot_id': record.slot_id or [],
                    'date': record.date,
                    'checked_in_time': record.checked_in_time,
                    'checked_out_time': record.checked_out_time,
                    'is_present': record.is_present,
                    'created_at': record.created_at
                })
            
            df = pd.DataFrame(data)
            
            # Filter by date range (convert DD/MM to comparable format)
            if not df.empty:
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m')
                start_obj = pd.to_datetime(start_date, format='%d/%m')
                end_obj = pd.to_datetime(end_date, format='%d/%m')
                
                df = df[(df['date_obj'] >= start_obj) & (df['date_obj'] <= end_obj)]
                df = df.drop('date_obj', axis=1)
            
            return df
            
        except Exception as e:
            print(f"Error fetching attendance range: {e}")
            return None
    
    def get_user_attendance(self, user_id: int, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Get attendance records for a specific user"""
        try:
            session = self.get_session()
            
            query = session.query(AttendanceRecordDB).filter(
                AttendanceRecordDB.user_id == user_id
            ).order_by(AttendanceRecordDB.date, AttendanceRecordDB.checked_in_time)
            
            records = query.all()
            session.close()
            
            if not records:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'name': record.name,
                    'user_id': record.user_id,
                    'slot_id': record.slot_id or [],
                    'date': record.date,
                    'checked_in_time': record.checked_in_time,
                    'checked_out_time': record.checked_out_time,
                    'is_present': record.is_present
                })
            
            df = pd.DataFrame(data)
            
            # Filter by date range if provided
            if start_date and end_date and not df.empty:
                df['date_obj'] = pd.to_datetime(df['date'], format='%d/%m')
                start_obj = pd.to_datetime(start_date, format='%d/%m')
                end_obj = pd.to_datetime(end_date, format='%d/%m')
                
                df = df[(df['date_obj'] >= start_obj) & (df['date_obj'] <= end_obj)]
                df = df.drop('date_obj', axis=1)
            
            return df
            
        except Exception as e:
            print(f"Error fetching user attendance: {e}")
            return None