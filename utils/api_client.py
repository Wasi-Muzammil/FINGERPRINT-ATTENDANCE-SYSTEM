import requests
from typing import Optional, Dict, Any, List, Tuple
import streamlit as st

class APIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Tuple[bool, Any]:
        """Handle API response"""
        try:
            if response.status_code in [200, 201]:
                return True, response.json()
            elif response.status_code == 401:
                # Token expired or invalid
                self.token = None
                if 'authenticated' in st.session_state:
                    st.session_state.authenticated = False
                return False, "Authentication failed. Please login again."
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                return False, error_detail
        except Exception as e:
            return False, str(e)
    
    # ==================== AUTHENTICATION ====================
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Login to get access token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def verify_token(self) -> bool:
        """Verify if current token is valid"""
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/verify",
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def logout(self) -> Tuple[bool, str]:
        """Logout (clear token)"""
        try:
            requests.post(
                f"{self.base_url}/api/auth/logout",
                headers=self._get_headers(),
                timeout=5
            )
        except:
            pass
        
        self.token = None
        return True, "Logged out successfully"
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, name: str, department: str, 
                   fingerprint_id: Optional[int] = None,
                   image_file = None) -> Tuple[bool, Any]:
        """Create a new user"""
        try:
            files = {}
            data = {
                "name": name,
                "department": department
            }
            
            if fingerprint_id:
                data["fingerprint_id"] = fingerprint_id
            
            if image_file:
                files["image"] = image_file
            
            response = requests.post(
                f"{self.base_url}/api/users",
                data=data,
                files=files if files else None,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30
            )
            
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_all_users(self) -> Tuple[bool, List[Dict]]:
        """Get all users"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_user(self, user_id: int) -> Tuple[bool, Dict]:
        """Get user by ID"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/{user_id}",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def update_user(self, user_id: int, name: Optional[str] = None,
                   department: Optional[str] = None,
                   fingerprint_id: Optional[int] = None) -> Tuple[bool, str]:
        """Update user information"""
        try:
            data = {}
            if name:
                data["name"] = name
            if department:
                data["department"] = department
            if fingerprint_id is not None:
                data["fingerprint_id"] = fingerprint_id
            
            response = requests.put(
                f"{self.base_url}/api/users/{user_id}",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            
            success, result = self._handle_response(response)
            if success:
                return True, result.get('message', 'User updated')
            return False, result
        except Exception as e:
            return False, str(e)
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete user"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/users/{user_id}",
                headers=self._get_headers(),
                timeout=10
            )
            
            success, result = self._handle_response(response)
            if success:
                return True, result.get('message', 'User deleted')
            return False, result
        except Exception as e:
            return False, str(e)
    
    def get_user_image_url(self, user_id: int) -> str:
        """Get user image URL"""
        return f"{self.base_url}/api/users/{user_id}/image?token={self.token}"
    
    # ==================== ATTENDANCE ====================
    
    def create_attendance(self, user_id: int, status: str,
                         timestamp: Optional[str] = None) -> Tuple[bool, str]:
        """Create attendance record"""
        try:
            data = {
                "user_id": user_id,
                "status": status
            }
            if timestamp:
                data["timestamp"] = timestamp
            
            response = requests.post(
                f"{self.base_url}/api/attendance",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            
            success, result = self._handle_response(response)
            if success:
                return True, result.get('message', 'Attendance recorded')
            return False, result
        except Exception as e:
            return False, str(e)
    
    def get_attendance_by_date(self, date_str: str) -> Tuple[bool, Any]:
        """Get attendance for a specific date"""
        try:
            response = requests.get(
                f"{self.base_url}/api/attendance/date/{date_str}",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_attendance_by_range(self, start_date: str, end_date: str) -> Tuple[bool, Any]:
        """Get attendance for date range"""
        try:
            response = requests.post(
                f"{self.base_url}/api/attendance/date-range",
                json={"start_date": start_date, "end_date": end_date},
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_user_attendance(self, user_id: int) -> Tuple[bool, Any]:
        """Get all attendance for a user"""
        try:
            response = requests.get(
                f"{self.base_url}/api/attendance/user/{user_id}",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_attendance_summary(self, start_date: str, end_date: str) -> Tuple[bool, Any]:
        """Get attendance summary with working hours"""
        try:
            response = requests.get(
                f"{self.base_url}/api/attendance/summary",
                params={"start_date": start_date, "end_date": end_date},
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    # ==================== PDF REPORTS ====================
    
    def download_daily_report(self, date_str: str) -> Tuple[bool, Any]:
        """Download daily PDF report"""
        try:
            response = requests.get(
                f"{self.base_url}/api/reports/daily/{date_str}",
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.content
            else:
                return False, "Failed to generate report"
        except Exception as e:
            return False, str(e)
    
    def download_range_report(self, start_date: str, end_date: str) -> Tuple[bool, Any]:
        """Download date range PDF report"""
        try:
            response = requests.post(
                f"{self.base_url}/api/reports/range",
                json={"start_date": start_date, "end_date": end_date},
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.content
            else:
                return False, "Failed to generate report"
        except Exception as e:
            return False, str(e)
    
    def download_user_report(self, user_id: int) -> Tuple[bool, Any]:
        """Download user PDF report"""
        try:
            response = requests.get(
                f"{self.base_url}/api/reports/user/{user_id}",
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.content
            else:
                return False, "Failed to generate report"
        except Exception as e:
            return False, str(e)
    
    # ==================== ESP32 INTEGRATION ====================
    
    def enroll_fingerprint(self, user_id: int, fingerprint_id: int) -> Tuple[bool, str]:
        """Enroll fingerprint on ESP32"""
        try:
            response = requests.post(
                f"{self.base_url}/api/fingerprint/enroll",
                json={"user_id": user_id, "fingerprint_id": fingerprint_id},
                headers=self._get_headers(),
                timeout=30
            )
            
            success, result = self._handle_response(response)
            if success:
                return True, result.get('message', 'Fingerprint enrolled')
            return False, result
        except Exception as e:
            return False, str(e)
    
    def delete_fingerprint(self, fingerprint_id: int) -> Tuple[bool, str]:
        """Delete fingerprint from ESP32"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/fingerprint/{fingerprint_id}",
                headers=self._get_headers(),
                timeout=10
            )
            
            success, result = self._handle_response(response)
            if success:
                return True, result.get('message', 'Fingerprint deleted')
            return False, result
        except Exception as e:
            return False, str(e)
    
    def get_esp32_status(self) -> Tuple[bool, Dict]:
        """Get ESP32 device status"""
        try:
            response = requests.get(
                f"{self.base_url}/api/esp32/status",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, {"connected": False, "message": str(e)}
    
    def sync_esp32_attendance(self) -> Tuple[bool, Any]:
        """Sync attendance from ESP32"""
        try:
            response = requests.get(
                f"{self.base_url}/api/esp32/sync",
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    def get_live_attendance(self) -> Tuple[bool, Any]:
        """Get live attendance from ESP32"""
        try:
            response = requests.get(
                f"{self.base_url}/api/esp32/live",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    # ==================== STATISTICS ====================
    
    def get_dashboard_stats(self) -> Tuple[bool, Dict]:
        """Get dashboard statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/stats/dashboard",
                headers=self._get_headers(),
                timeout=10
            )
            return self._handle_response(response)
        except Exception as e:
            return False, str(e)
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> bool:
        """Check if API is reachable"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# Singleton instance
api_client = APIClient()