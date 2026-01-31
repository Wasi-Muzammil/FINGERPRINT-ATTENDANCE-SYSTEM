from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, timedelta
import uvicorn
import sqlite3
import bcrypt
import jwt
import os
import shutil
from pathlib import Path
import io

# Import database utilities
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from utils.database import Database
from utils.pdf_generator import PDFGenerator
from utils.esp32_api import ESP32API

# Set database path to project root
DB_PATH = parent_dir / 'attendance.db'

# FastAPI app initialization
app = FastAPI(
    title="Fingerprint Attendance API",
    description="REST API for Fingerprint Attendance System",
    version="1.0.0"
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Initialize services
db = Database(db_name=str(DB_PATH))
pdf_gen = PDFGenerator()
esp32_api = ESP32API()

# ==================== PYDANTIC MODELS ====================

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    fingerprint_id: Optional[int] = Field(None, ge=1, le=127)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    fingerprint_id: Optional[int] = Field(None, ge=1, le=127)

class UserResponse(BaseModel):
    id: int
    name: str
    department: str
    fingerprint_id: Optional[int]
    image_path: Optional[str]
    created_at: Optional[str]

class AttendanceCreate(BaseModel):
    user_id: int
    status: str = Field(..., pattern="^(IN|OUT)$")
    timestamp: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    timestamp: str
    status: str

class FingerprintEnroll(BaseModel):
    user_id: int
    fingerprint_id: int = Field(..., ge=1, le=127)

class DateRangeRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# ==================== AUTHENTICATION ====================

def create_access_token(username: str) -> str:
    """Create JWT access token"""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin login credentials"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    return False

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Admin login endpoint"""
    if verify_admin_credentials(request.username, request.password):
        token = create_access_token(request.username)
        return TokenResponse(access_token=token)
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/auth/verify")
async def verify_auth(username: str = Depends(verify_token)):
    """Verify token validity"""
    return {"username": username, "authenticated": True}

@app.post("/api/auth/logout")
async def logout(username: str = Depends(verify_token)):
    """Logout endpoint (client should delete token)"""
    return MessageResponse(message="Logged out successfully")

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    name: str = Form(...),
    department: str = Form(...),
    fingerprint_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    username: str = Depends(verify_token)
):
    """Create a new user"""
    # Handle image upload
    image_path = None
    if image:
        os.makedirs("assets/user_images", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
        image_path = f"assets/user_images/{filename}"
        
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    
    # Add user to database
    success, result = db.add_user(name, department, fingerprint_id, image_path)
    
    if not success:
        raise HTTPException(status_code=400, detail=str(result))
    
    user_id = result
    
    # Enroll fingerprint on ESP32 if ID provided
    if fingerprint_id:
        fp_success, fp_message = esp32_api.enroll_fingerprint(user_id, fingerprint_id)
        if not fp_success:
            # Log warning but don't fail the user creation
            print(f"Warning: Fingerprint enrollment failed - {fp_message}")
    
    # Get created user
    user = db.get_user_by_id(user_id)
    return UserResponse(
        id=user[0],
        name=user[1],
        department=user[2],
        fingerprint_id=user[3],
        image_path=user[4],
        created_at=user[5] if len(user) > 5 else None
    )

@app.get("/api/users", response_model=List[UserResponse])
async def get_all_users(username: str = Depends(verify_token)):
    """Get all users"""
    users = db.get_all_users()
    return [
        UserResponse(
            id=user[0],
            name=user[1],
            department=user[2],
            fingerprint_id=user[3],
            image_path=user[4],
            created_at=user[5] if len(user) > 5 else None
        )
        for user in users
    ]

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, username: str = Depends(verify_token)):
    """Get user by ID"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user[0],
        name=user[1],
        department=user[2],
        fingerprint_id=user[3],
        image_path=user[4],
        created_at=user[5] if len(user) > 5 else None
    )

@app.put("/api/users/{user_id}", response_model=MessageResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    username: str = Depends(verify_token)
):
    """Update user information"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.update_user(
        user_id,
        user_update.name,
        user_update.department,
        user_update.fingerprint_id
    )
    
    return MessageResponse(message="User updated successfully")

@app.delete("/api/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int, username: str = Depends(verify_token)):
    """Delete user"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete fingerprint from ESP32 if exists
    if user[3]:  # fingerprint_id
        esp32_api.delete_fingerprint(user[3])
    
    db.delete_user(user_id)
    return MessageResponse(message="User deleted successfully")

@app.get("/api/users/{user_id}/image")
async def get_user_image(user_id: int, username: str = Depends(verify_token)):
    """Get user profile image"""
    user = db.get_user_by_id(user_id)
    if not user or not user[4]:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_path = user[4]
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(image_path)

# ==================== ATTENDANCE ENDPOINTS ====================

@app.post("/api/attendance", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance: AttendanceCreate,
    username: str = Depends(verify_token)
):
    """Create attendance record"""
    # Verify user exists
    user = db.get_user_by_id(attendance.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.add_attendance(
        attendance.user_id,
        attendance.status,
        attendance.timestamp
    )
    
    return MessageResponse(message="Attendance recorded successfully")

@app.get("/api/attendance/date/{date_str}")
async def get_attendance_by_date(date_str: str, username: str = Depends(verify_token)):
    """Get attendance records for a specific date (YYYY-MM-DD)"""
    try:
        # Validate date format
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    records = db.get_attendance_by_date(date_str)
    return {
        "date": date_str,
        "count": len(records),
        "records": [
            {
                "id": r[0],
                "name": r[1],
                "department": r[2],
                "timestamp": r[3],
                "status": r[4]
            }
            for r in records
        ]
    }

@app.post("/api/attendance/date-range")
async def get_attendance_by_range(
    date_range: DateRangeRequest,
    username: str = Depends(verify_token)
):
    """Get attendance records for a date range"""
    try:
        datetime.strptime(date_range.start_date, "%Y-%m-%d")
        datetime.strptime(date_range.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    records = db.get_attendance_by_date_range(date_range.start_date, date_range.end_date)
    return {
        "start_date": date_range.start_date,
        "end_date": date_range.end_date,
        "count": len(records),
        "records": [
            {
                "id": r[0],
                "name": r[1],
                "department": r[2],
                "timestamp": r[3],
                "status": r[4]
            }
            for r in records
        ]
    }

@app.get("/api/attendance/user/{user_id}")
async def get_user_attendance(user_id: int, username: str = Depends(verify_token)):
    """Get all attendance records for a specific user"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    records = db.get_user_attendance(user_id)
    return {
        "user_id": user_id,
        "user_name": user[1],
        "count": len(records),
        "records": [
            {
                "id": r[0],
                "timestamp": r[1],
                "status": r[2]
            }
            for r in records
        ]
    }

@app.get("/api/attendance/summary")
async def get_attendance_summary(
    start_date: str,
    end_date: str,
    username: str = Depends(verify_token)
):
    """Get attendance summary with working hours"""
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    records = db.get_attendance_summary(start_date, end_date)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "count": len(records),
        "summary": [
            {
                "user_id": r[0],
                "name": r[1],
                "department": r[2],
                "date": r[3],
                "check_in": r[4],
                "check_out": r[5]
            }
            for r in records
        ]
    }

# ==================== PDF REPORT ENDPOINTS ====================

@app.get("/api/reports/daily/{date_str}")
async def generate_daily_report(date_str: str, username: str = Depends(verify_token)):
    """Generate daily attendance PDF report"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    records = db.get_attendance_by_date(date_str)
    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found for this date")
    
    pdf_buffer = pdf_gen.generate_daily_report(records, date_str)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=attendance_{date_str}.pdf"}
    )

@app.post("/api/reports/range")
async def generate_range_report(
    date_range: DateRangeRequest,
    username: str = Depends(verify_token)
):
    """Generate date range attendance PDF report"""
    try:
        datetime.strptime(date_range.start_date, "%Y-%m-%d")
        datetime.strptime(date_range.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    records = db.get_attendance_summary(date_range.start_date, date_range.end_date)
    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found for this period")
    
    pdf_buffer = pdf_gen.generate_range_report(records, date_range.start_date, date_range.end_date)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{date_range.start_date}_to_{date_range.end_date}.pdf"
        }
    )

@app.get("/api/reports/user/{user_id}")
async def generate_user_report(user_id: int, username: str = Depends(verify_token)):
    """Generate individual user attendance PDF report"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attendance = db.get_user_attendance(user_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="No attendance records found for this user")
    
    pdf_buffer = pdf_gen.generate_user_report(user[1], user[2], attendance)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{user[1].replace(' ', '_')}.pdf"
        }
    )

# ==================== ESP32 INTEGRATION ENDPOINTS ====================

@app.post("/api/fingerprint/enroll", response_model=MessageResponse)
async def enroll_fingerprint(
    enroll_data: FingerprintEnroll,
    username: str = Depends(verify_token)
):
    """Enroll fingerprint on ESP32 device"""
    user = db.get_user_by_id(enroll_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success, message = esp32_api.enroll_fingerprint(
        enroll_data.user_id,
        enroll_data.fingerprint_id
    )
    
    if success:
        # Update user's fingerprint_id
        db.update_user(enroll_data.user_id, fingerprint_id=enroll_data.fingerprint_id)
        return MessageResponse(message=message)
    else:
        raise HTTPException(status_code=500, detail=message)

@app.delete("/api/fingerprint/{fingerprint_id}", response_model=MessageResponse)
async def delete_fingerprint(fingerprint_id: int, username: str = Depends(verify_token)):
    """Delete fingerprint from ESP32 device"""
    success, message = esp32_api.delete_fingerprint(fingerprint_id)
    
    if success:
        # Clear fingerprint_id from database
        db.delete_fingerprint(fingerprint_id)
        return MessageResponse(message=message)
    else:
        raise HTTPException(status_code=500, detail=message)

@app.get("/api/esp32/status")
async def get_esp32_status(username: str = Depends(verify_token)):
    """Get ESP32 device status"""
    success, info = esp32_api.get_device_info()
    
    if success:
        return {
            "connected": True,
            "device_info": info
        }
    else:
        return {
            "connected": False,
            "message": "Cannot connect to ESP32 device"
        }

@app.get("/api/esp32/sync")
async def sync_attendance(username: str = Depends(verify_token)):
    """Sync attendance from ESP32 device"""
    success, records = esp32_api.sync_attendance_bulk()
    
    if success and records:
        # Save all records to database
        saved_count = 0
        for record in records:
            try:
                db.add_attendance(
                    record['user_id'],
                    record['status'],
                    record.get('timestamp')
                )
                saved_count += 1
            except Exception as e:
                print(f"Error saving record: {e}")
        
        return {
            "success": True,
            "fetched": len(records),
            "saved": saved_count,
            "message": f"Synced {saved_count} attendance records"
        }
    else:
        return {
            "success": False,
            "message": "No records to sync or connection failed"
        }

@app.get("/api/esp32/live")
async def get_live_attendance(username: str = Depends(verify_token)):
    """Fetch latest attendance from ESP32"""
    success, data = esp32_api.fetch_live_attendance()
    
    if success and data:
        # Optionally auto-save
        if 'user_id' in data and 'status' in data:
            db.add_attendance(
                data['user_id'],
                data['status'],
                data.get('timestamp')
            )
        return {
            "success": True,
            "data": data
        }
    else:
        return {
            "success": False,
            "message": "No new attendance data"
        }

# ==================== STATISTICS ENDPOINTS ====================

@app.get("/api/stats/dashboard")
async def get_dashboard_stats(username: str = Depends(verify_token)):
    """Get dashboard statistics"""
    users = db.get_all_users()
    today = date.today().strftime("%Y-%m-%d")
    today_attendance = db.get_attendance_by_date(today)
    
    checked_in = len([a for a in today_attendance if a[4] == 'IN'])
    checked_out = len([a for a in today_attendance if a[4] == 'OUT'])
    
    return {
        "total_users": len(users),
        "today_records": len(today_attendance),
        "checked_in": checked_in,
        "checked_out": checked_out,
        "date": today
    }

# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Fingerprint Attendance API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )