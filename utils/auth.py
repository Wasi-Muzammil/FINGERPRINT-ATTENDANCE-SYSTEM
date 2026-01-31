import sqlite3
import bcrypt
import streamlit as st

class Authentication:
    def __init__(self, db_name='attendance.db'):
        self.db_name = db_name
    
    def verify_login(self, username, password):
        """Verify admin login credentials"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash = result[0]
            # Check if password matches
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True
        return False
    
    def create_admin(self, username, password):
        """Create a new admin account"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()
            return True, "Admin created successfully"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Username already exists"
    
    def change_password(self, username, old_password, new_password):
        """Change admin password"""
        if self.verify_login(username, old_password):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE admins SET password_hash = ? WHERE username = ?",
                (new_hash, username)
            )
            conn.commit()
            conn.close()
            return True, "Password changed successfully"
        return False, "Current password is incorrect"

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()