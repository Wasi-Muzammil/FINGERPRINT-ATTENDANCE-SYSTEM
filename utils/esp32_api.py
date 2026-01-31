import requests
import json
from typing import Tuple, Optional

# ESP32-S3 Configuration
ESP32_BASE_URL = "http://YOUR_ESP32_IP:80"  # Update with your ESP32 IP address
TIMEOUT = 10  # seconds

class ESP32API:
    """
    API wrapper for communicating with ESP32-S3 fingerprint module
    
    Replace the placeholder implementations with actual HTTP requests
    or serial communication based on your ESP32 firmware implementation.
    """
    
    def __init__(self, base_url=ESP32_BASE_URL):
        self.base_url = base_url
        self.timeout = TIMEOUT
    
    def check_connection(self) -> Tuple[bool, str]:
        """
        Check if ESP32 device is reachable
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            response = requests.get(
                f"{self.base_url}/status",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return True, "ESP32 device connected"
            else:
                return False, f"Device returned status code: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {str(e)}"
    
    def enroll_fingerprint(self, user_id: int, fingerprint_id: int) -> Tuple[bool, str]:
        """
        Enroll a new fingerprint on the ESP32 device
        
        Args:
            user_id: Database user ID
            fingerprint_id: Fingerprint slot number (1-127 typically)
        
        Returns:
            Tuple[bool, str]: (success, message)
            
        Implementation example:
            POST /enroll
            Body: {"user_id": 123, "fingerprint_id": 1}
        """
        try:
            # PLACEHOLDER: Replace with actual API call
            payload = {
                "user_id": user_id,
                "fingerprint_id": fingerprint_id
            }
            
            response = requests.post(
                f"{self.base_url}/enroll",
                json=payload,
                timeout=30  # Longer timeout for enrollment
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get("message", "Fingerprint enrolled successfully")
            else:
                return False, f"Enrollment failed: {response.text}"
                
        except requests.exceptions.RequestException as e:
            # For development: Return success to test without hardware
            return True, f"[MOCK] Fingerprint enrolled for user {user_id} at slot {fingerprint_id}"
            # return False, f"API Error: {str(e)}"
    
    def delete_fingerprint(self, fingerprint_id: int) -> Tuple[bool, str]:
        """
        Delete a fingerprint from the ESP32 device
        
        Args:
            fingerprint_id: Fingerprint slot number to delete
        
        Returns:
            Tuple[bool, str]: (success, message)
            
        Implementation example:
            DELETE /fingerprint/{id}
        """
        try:
            # PLACEHOLDER: Replace with actual API call
            response = requests.delete(
                f"{self.base_url}/fingerprint/{fingerprint_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, "Fingerprint deleted successfully"
            else:
                return False, f"Deletion failed: {response.text}"
                
        except requests.exceptions.RequestException as e:
            # For development: Return success to test without hardware
            return True, f"[MOCK] Fingerprint {fingerprint_id} deleted"
            # return False, f"API Error: {str(e)}"
    
    def fetch_live_attendance(self) -> Tuple[bool, Optional[dict]]:
        """
        Fetch latest attendance records from ESP32 device
        
        Returns:
            Tuple[bool, Optional[dict]]: (success, attendance_data)
            
        Expected response format:
            {
                "user_id": 123,
                "fingerprint_id": 1,
                "timestamp": "2024-01-15 09:30:45",
                "status": "IN"
            }
            
        Implementation example:
            GET /attendance/latest
        """
        try:
            # PLACEHOLDER: Replace with actual API call
            response = requests.get(
                f"{self.base_url}/attendance/latest",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, None
                
        except requests.exceptions.RequestException as e:
            return False, None
    
    def get_device_info(self) -> Tuple[bool, Optional[dict]]:
        """
        Get ESP32 device information and status
        
        Returns:
            Tuple[bool, Optional[dict]]: (success, device_info)
            
        Expected response:
            {
                "device_name": "ESP32-S3 Fingerprint",
                "firmware_version": "1.0.0",
                "total_fingerprints": 127,
                "enrolled_count": 5,
                "last_sync": "2024-01-15 10:00:00"
            }
        """
        try:
            response = requests.get(
                f"{self.base_url}/device/info",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
                
        except requests.exceptions.RequestException as e:
            # Mock response for development
            mock_info = {
                "device_name": "ESP32-S3 Fingerprint [MOCK]",
                "firmware_version": "1.0.0-dev",
                "total_fingerprints": 127,
                "enrolled_count": 0,
                "status": "offline"
            }
            return True, mock_info
    
    def sync_attendance_bulk(self) -> Tuple[bool, list]:
        """
        Sync all pending attendance records from ESP32 (if stored locally)
        
        Returns:
            Tuple[bool, list]: (success, list_of_attendance_records)
        """
        try:
            response = requests.get(
                f"{self.base_url}/attendance/sync",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data.get("records", [])
            else:
                return False, []
                
        except requests.exceptions.RequestException as e:
            return False, []
    
    def clear_device_logs(self) -> Tuple[bool, str]:
        """
        Clear attendance logs stored on ESP32 device (after successful sync)
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            response = requests.post(
                f"{self.base_url}/logs/clear",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, "Device logs cleared"
            else:
                return False, "Failed to clear logs"
                
        except requests.exceptions.RequestException as e:
            return True, "[MOCK] Logs cleared"

# Create singleton instance
esp32_api = ESP32API()

# Convenience functions
def enroll_fingerprint(user_id: int, fingerprint_id: int) -> Tuple[bool, str]:
    """Enroll fingerprint wrapper"""
    return esp32_api.enroll_fingerprint(user_id, fingerprint_id)

def delete_fingerprint(fingerprint_id: int) -> Tuple[bool, str]:
    """Delete fingerprint wrapper"""
    return esp32_api.delete_fingerprint(fingerprint_id)

def fetch_live_attendance() -> Tuple[bool, Optional[dict]]:
    """Fetch live attendance wrapper"""
    return esp32_api.fetch_live_attendance()

def get_device_status() -> Tuple[bool, Optional[dict]]:
    """Get device status wrapper"""
    return esp32_api.get_device_info()