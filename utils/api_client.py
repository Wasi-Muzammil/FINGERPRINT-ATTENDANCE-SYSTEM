
"""
API Client for FastAPI Backend
Aligned with actual backend endpoints from main.py
"""

import requests
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime

class APIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self, base_url: str):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the FastAPI backend (from secrets)
        """
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    # ==================== AUTHENTICATION ====================
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Login to backend - validates credentials against admin_information table
        
        Args:
            username: Admin username
            password: Admin password
        
        Returns:
            Tuple of (success, token or error_message)
        """
        try:
            response = requests.post(
                f"{self.base_url}/esp32/user/admin/login",
                json={"username": username, "password": password},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token', 'authenticated')
                    return True, self.token
                else:
                    return False, data.get('message', 'Invalid credentials')
            else:
                return False, "Invalid credentials"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def verify_token(self) -> bool:
        """Verify if session is valid"""
        # Since backend doesn't have JWT, we just check if we have a token
        return self.token is not None
    
    def logout(self) -> None:
        """Logout and clear token"""
        self.token = None
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> bool:
        """Check if backend is reachable"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    # ==================== USER MANAGEMENT ====================
    
    def get_all_users(self) -> Tuple[bool, Any]:
        """
        Get all users from backend
        Endpoint: GET /esp32/users
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/user/esp32/users",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Error: {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def get_user_by_id(self, user_id: int) -> Tuple[bool, Any]:
        """
        Get specific user by user_id
        Endpoint: GET /esp32/user/{user_id}
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/user/esp32/user/{user_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except Exception as e:
            return False, None
    
    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        slot_ids: Optional[List[int]] = None,
        date: Optional[str] = None,
        time: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update user via API
        Endpoint: PUT /admin/user/update
        
        Args:
            user_id: User ID
            name: Updated name
            slot_ids: Updated slot IDs list
            date: Updated enrollment date
            time: Updated enrollment time
        
        Returns:
            Tuple of (success, message)
        """
        try:
            data = {"user_id": user_id}
            
            if name:
                data['name'] = name
            if slot_ids is not None:
                data['slot_id'] = slot_ids
            if date:
                data['date'] = date
            if time:
                data['time'] = time
            
            response = requests.put(
                f"{self.base_url}/esp32/user/admin/user/update",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return True, result.get('message', 'User updated successfully')
                else:
                    return False, result.get('message', 'Update failed')
            else:
                error = response.json().get('detail', 'Update failed')
                return False, error
                
        except Exception as e:
            return False, str(e)
    
    def create_user(
        self,
        name: str,
        user_id: int,
        slot_ids: List[int],
        date: str,
        time: str
    ) -> Tuple[bool, str]:
        """
        Create new user
        Endpoint: POST /esp32/user
        """
        try:
            data = {
                "name": name,
                "id": user_id,
                "slot_id": slot_ids,
                "date": date,
                "time": time
            }
            
            response = requests.post(
                f"{self.base_url}/esp32/user/esp32/user",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return True, result.get('message', 'User created successfully')
                else:
                    return False, result.get('message', 'Creation failed')
            else:
                return False, "Creation failed"
                
        except Exception as e:
            return False, str(e)
    
    def delete_user(
        self,
        user_id: int,
        slot_ids: List[int]
    ) -> Tuple[bool, str]:
        """
        Delete user
        Endpoint: DELETE /esp32/user/delete
        """
        try:
            data = {
                "user_id": user_id,
                "slot_id": slot_ids
            }
            
            response = requests.delete(
                f"{self.base_url}/esp32/user/esp32/user/delete",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return True, result.get('message', 'User deleted successfully')
                else:
                    return False, result.get('message', 'Deletion failed')
            else:
                return False, "Deletion failed"
                
        except Exception as e:
            return False, str(e)
    
    # ==================== DEVICE STATUS ====================
    
    def get_device_status(self, device_id: str = "ESP32_MAIN") -> Optional[Dict]:
        """
        Get ESP32 device status from API
        Endpoint: GET /esp32/status/{device_id}
        
        Returns:
            Device status dictionary or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/esp32/status/{device_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'connected': data.get('is_online', False),
                    'status': data.get('status', 'Offline'),
                    'last_seen': data.get('last_seen', 'Unknown'),
                    'device_id': data.get('device_id', device_id)
                }
            else:
                return {
                    'connected': False,
                    'status': 'Offline',
                    'last_seen': 'Unknown',
                    'device_id': device_id
                }
                
        except Exception as e:
            return {
                'connected': False,
                'status': 'Offline',
                'last_seen': 'Unknown',
                'device_id': device_id,
                'error': str(e)
            }
    
    def get_all_devices_status(self) -> Optional[Dict]:
        """
        Get status of all devices
        Endpoint: GET /esp32/status
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/esp32/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None
    
    # ==================== ATTENDANCE ====================
    
    def get_attendance_by_date(self, date_str: str) -> Tuple[bool, Any]:
        """
        Get attendance for specific date (DD/MM format)
        Endpoint: GET /esp32/attendance/date/{date}
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/atendance/esp32/attendance/date/{date_str}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except Exception as e:
            return False, None
    
    def get_user_attendance(self, user_id: int, date: str) -> Tuple[bool, Any]:
        """
        Get attendance for specific user and date
        Endpoint: GET /esp32/attendance/{user_id}/{date}
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/attendance/esp32/attendance/{user_id}/{date}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except Exception as e:
            return False, None
    
    def log_attendance(
        self,
        name: str,
        user_id: int,
        slot_ids: List[int],
        date: str,
        time: str
    ) -> Tuple[bool, str]:
        """
        Log attendance record
        Endpoint: POST /esp32/attendance
        """
        try:
            data = {
                "name": name,
                "id": user_id,
                "slot_id": slot_ids,
                "date": date,
                "time": time
            }
            
            response = requests.post(
                f"{self.base_url}/esp32/attendance/esp32/attendance",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return True, result.get('message', 'Attendance logged')
                else:
                    return False, result.get('message', 'Logging failed')
            else:
                return False, "Logging failed"
                
        except Exception as e:
            return False, str(e)
    
    # ==================== STATISTICS ====================
    
    def get_dashboard_stats(self) -> Optional[Dict]:
        """
        Get dashboard statistics
        Endpoint: GET /admin/stats/dashboard
        """
        try:
            response = requests.get(
                f"{self.base_url}/esp32/user/admin/stats/dashboard",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Return default stats if endpoint doesn't exist yet
                return {
                    'total_users': 0,
                    'today_records': 0,
                    'checked_in': 0,
                    'checked_out': 0
                }
                
        except Exception as e:
            return {
                'total_users': 0,
                'today_records': 0,
                'checked_in': 0,
                'checked_out': 0
            }