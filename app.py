
# import streamlit as st
# from datetime import datetime, date, timedelta
# from streamlit_option_menu import option_menu
# import requests
# import pandas as pd

# # Import utility modules
# from utils.db_manager import DatabaseManager
# from utils.pdf_manager import PDFManager
# from utils.api_client import APIClient

# # Page configuration
# st.set_page_config(
#     page_title="Fingerprint Attendance System",
#     page_icon="🔐",
#     layout="wide",
#     initial_sidebar_state="expanded"  # Always show sidebar by default
# )

# # Load custom CSS
# def load_css():
#     try:
#         with open('frontend/style.css') as f:
#             st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
#     except FileNotFoundError:
#         st.warning("style.css not found. Using default styling.")

# load_css()

# # Initialize services
# @st.cache_resource
# def init_services():
#     """Initialize database and API clients"""
#     db_url = st.secrets.get("DATABASE_URL", "")
#     api_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    
#     db_manager = DatabaseManager(db_url)
#     api_client = APIClient(api_url)
#     pdf_manager = PDFManager()
    
#     return db_manager, api_client, pdf_manager

# db_manager, api_client, pdf_manager = init_services()

# # Session state initialization
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False
# if 'current_page' not in st.session_state:
#     st.session_state.current_page = 'Home'

# # ==================== AUTHENTICATION ====================

# def verify_credentials(username: str, password: str) -> bool:
#     """Verify admin credentials (hardcoded in backend logic)"""
#     # Credentials validation happens on backend
#     # This calls the API login endpoint
#     success, token = api_client.login(username, password)
#     if success:
#         st.session_state.token = token
#         return True
#     return False

# def login_page():
#     """Secure login page - NO hints about credentials"""
    
#     # Center the login form
#     col1, col2, col3 = st.columns([1, 2, 1])
    
#     with col2:
#         st.markdown("""
#         <div class="login-container">
#             <h1 class="login-header">🔐 Fingerprint Attendance System</h1>
#             <p class="login-subheader">Secure Admin Portal</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         st.markdown("<div class='login-form'>", unsafe_allow_html=True)
        
#         # Check API health
#         if not api_client.health_check():
#             st.error("⚠️ Cannot connect to backend server. Please contact system administrator.")
#             st.stop()
        
#         with st.form("login_form", clear_on_submit=True):
#             username = st.text_input("Username", placeholder="Enter username", key="login_username")
#             password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            
#             submitted = st.form_submit_button("Login", use_container_width=True)
            
#             if submitted:
#                 if username and password:
#                     with st.spinner("Authenticating..."):
#                         if verify_credentials(username, password):
#                             st.session_state.authenticated = True
#                             st.session_state.username = username
#                             st.success("✅ Login successful!")
#                             st.rerun()
#                         else:
#                             st.error("❌ Invalid credentials")
#                 else:
#                     st.warning("⚠️ Please enter both username and password")
        
#         st.markdown("</div>", unsafe_allow_html=True)

# # ==================== SIDEBAR ====================

# def render_sidebar():
#     """Render sidebar with device status"""
    
#     st.sidebar.markdown("""
#     <div class="sidebar-header">
#         <h2>🔐 Attendance System</h2>
#     </div>
#     """, unsafe_allow_html=True)
    
#     st.sidebar.markdown("---")
    
#     # ESP32 Device Status - Fetched from API only
#     st.sidebar.markdown("### 🔌 Device Status")
    
#     with st.spinner("Checking device..."):
#         device_status = api_client.get_device_status()
    
#     if device_status and device_status.get('connected'):
#         # Online
#         st.sidebar.markdown("""
#         <div class="device-status online">
#             <span class="status-dot online-dot"></span>
#             <span class="status-text">Online</span>
#         </div>
#         """, unsafe_allow_html=True)
        
#         # Last seen timestamp
#         last_seen = device_status.get('last_seen', datetime.now().isoformat())
#         st.sidebar.caption(f"Last seen: {last_seen}")
#     else:
#         # Offline
#         st.sidebar.markdown("""
#         <div class="device-status offline">
#             <span class="status-dot offline-dot"></span>
#             <span class="status-text">Offline</span>
#         </div>
#         """, unsafe_allow_html=True)
        
#         last_seen = device_status.get('last_seen', 'Never') if device_status else 'Never'
#         st.sidebar.caption(f"Last seen: {last_seen}")
    
#     st.sidebar.markdown("---")
    
#     # User info
#     st.sidebar.markdown(f"**👤 Admin:** {st.session_state.get('username', 'User')}")
#     st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%Y-%m-%d')}")
    
#     st.sidebar.markdown("---")
    
#     # Logout button
#     if st.sidebar.button("🚪 Logout", use_container_width=True):
#         api_client.logout()
#         st.session_state.authenticated = False
#         st.session_state.token = None
#         st.rerun()

# # ==================== NAVIGATION ====================

# def render_navigation():
#     """Professional navigation bar using streamlit-option-menu"""
    
#     selected = option_menu(
#         menu_title=None,
#         options=["Home", "About", "Contact"],
#         icons=["house", "info-circle", "envelope"],
#         menu_icon="cast",
#         default_index=0 if st.session_state.current_page == "Home" else 
#                       1 if st.session_state.current_page == "About" else 2,
#         orientation="horizontal",
#         styles={
#             "container": {"padding": "0!important", "background-color": "#1a1a2e"},
#             "icon": {"color": "#00d4ff", "font-size": "18px"},
#             "nav-link": {
#                 "font-size": "16px",
#                 "text-align": "center",
#                 "margin": "0px",
#                 "padding": "10px 20px",
#                 "--hover-color": "#16213e",
#             },
#             "nav-link-selected": {"background-color": "#2E3192"},
#         }
#     )
    
#     if selected != st.session_state.current_page:
#         st.session_state.current_page = selected
#         st.rerun()

# # ==================== HOME PAGE ====================

# def home_page():
#     """Admin Dashboard - Main page"""
    
#     st.markdown("<h1 class='page-title'>🏠 Admin Dashboard</h1>", unsafe_allow_html=True)
    
#     # Dashboard metrics
#     stats = api_client.get_dashboard_stats()
    
#     if stats:
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-icon">👥</div>
#                 <div class="metric-value">{stats.get('total_users', 0)}</div>
#                 <div class="metric-label">Total Users</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div class="metric-card metric-success">
#                 <div class="metric-icon">✅</div>
#                 <div class="metric-value">{stats.get('today_records', 0)}</div>
#                 <div class="metric-label">Today's Records</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div class="metric-card metric-info">
#                 <div class="metric-icon">📥</div>
#                 <div class="metric-value">{stats.get('checked_in', 0)}</div>
#                 <div class="metric-label">Checked In</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#             <div class="metric-card metric-warning">
#                 <div class="metric-icon">📤</div>
#                 <div class="metric-value">{stats.get('checked_out', 0)}</div>
#                 <div class="metric-label">Checked Out</div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Tabs
#     tab1, tab2 = st.tabs(["👥 Manage Users", "📊 Attendance Reports"])
    
#     with tab1:
#         manage_users_tab()
    
#     with tab2:
#         attendance_reports_tab()

# # ==================== MANAGE USERS TAB ====================

# def manage_users_tab():
#     """Data management - Display and update users"""
    
#     st.markdown("### 👥 User Management")
    
#     # Fetch all users from API
#     success, users_data = api_client.get_all_users()
    
#     if not success or not users_data or 'users' not in users_data:
#         st.info("ℹ️ No users found in the system.")
#         return
    
#     users_list = users_data['users']
    
#     if not users_list:
#         st.info("ℹ️ No users found in the system.")
#         return
    
#     df_data = []
#     for user in users_list:
#         df_data.append({
#             'User ID': user['user_id'],
#             'Name': user['name'],
#             'Slot IDs': ', '.join(map(str, user['slot_id'])),
#             'Salary (Daily)': user.get('salary') if user.get('salary') is not None else "",
#             'Templates': user['total_templates'],
#             'Enrolled': user['date'],
#             'Time': user['time']
#         })
    
#     users_df = pd.DataFrame(df_data)
    
#     # Display users in data table
#     st.markdown("#### All Users")
#     st.dataframe(users_df, hide_index=True, use_container_width=True)
    
#     st.markdown("---")
    
#     # Update user section
#     st.markdown("#### ✏️ Update User")
    
#     # User selection
#     user_options = {f"{user['name']} (ID: {user['user_id']})": user['user_id'] 
#                    for user in users_list}
    
#     if user_options:
#         selected_user = st.selectbox("Select User to Update", options=list(user_options.keys()))
#         user_id = user_options[selected_user]
        
#         # Get selected user data
#         selected_user_data = next((u for u in users_list if u['user_id'] == user_id), None)
        
#         if selected_user_data:
#             with st.form("update_user_form"):
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     new_name = st.text_input("Name", value=selected_user_data['name'])
#                     new_salary = st.number_input(
#                         "Salary (Daily)",
#                         min_value=0.0,
#                         value=float(selected_user_data['salary']) if selected_user_data.get('salary') is not None else 0.0,
#                         step=100.0
#                     )

#                 with col2:
#                     current_slots = selected_user_data.get('slot_id', [])
#                     slot_ids_str = ', '.join(map(str, current_slots)) if current_slots else ''
#                     new_slot_ids = st.text_input("Slot IDs (comma-separated)", value=slot_ids_str)
                
#                 submitted = st.form_submit_button("💾 Update User", use_container_width=True)
                
#                 if submitted:
#                     # Parse slot IDs
#                     try:
#                         slot_ids_list = [int(x.strip()) for x in new_slot_ids.split(',') if x.strip()]
#                     except ValueError:
#                         st.error("❌ Invalid slot IDs format. Use comma-separated numbers.")
#                         return
                    
#                     # Call API to update user
#                     with st.spinner("Updating user..."):
#                         success, message = api_client.update_user(
#                         user_id=user_id,
#                         name=new_name,
#                         slot_ids=slot_ids_list,
#                         salary=new_salary if new_salary > 0 else None
#                     )
                    
#                     if success:
#                         st.success(f"✅ {message}")
#                         st.rerun()
#                     else:
#                         st.error(f"❌ {message}")

# # ==================== ATTENDANCE REPORTS TAB ====================

# def attendance_reports_tab():
#     """Reporting engine with PDF generation"""
    
#     st.markdown("### 📊 Attendance Reports")
    
#     # Report type selection
#     report_type = st.radio(
#         "Select Report Type",
#         ["📅 Single Day Report", "📆 Date Range Report"],
#         horizontal=True
#     )
    
#     st.markdown("---")
    
#     if report_type == "📅 Single Day Report":
#         single_day_report()
#     else:
#         date_range_report()

# def single_day_report():
#     """Single day report with user filter - UPDATED LAYOUT"""
    
#     # Date and User Filter in columns
#     col1, col2 = st.columns(2)
    
#     with col1:
#         selected_date = st.date_input("Select Date", value=date.today(), max_value=date.today())
    
#     with col2:
#         # Get user list for dropdown from API
#         success, users_data = api_client.get_all_users()
#         user_options = {"All Users Combined": None}
        
#         if success and users_data and 'users' in users_data:
#             for user in users_data['users']:
#                 user_options[f"{user['name']} (ID: {user['user_id']})"] = user['user_id']
        
#         selected_user = st.selectbox("User Filter", options=list(user_options.keys()))
#         user_id = user_options[selected_user]
    
#     # Generate PDF button below filters
#     generate_btn = st.button("📄 Generate PDF", use_container_width=True, type="primary")
    
#     if generate_btn:
#         # Convert to DD/MM format for backend
#         date_str = selected_date.strftime("%d/%m")
        
#         with st.spinner("Generating report..."):
#             # Fetch attendance data from database
#             if user_id:
#                 attendance_data = db_manager.get_user_attendance(user_id, date_str, date_str)
#             else:
#                 attendance_data = db_manager.get_attendance_by_date(date_str)
            
#             if attendance_data is None or attendance_data.empty:
#                 st.warning(f"⚠️ No attendance records found for {date_str}")
#                 return
            
#             # Generate PDF
#             pdf_bytes = pdf_manager.generate_daily_report(
#                 attendance_data,
#                 date_str,
#                 user_name=selected_user if user_id else None
#             )
            
#             if pdf_bytes:
#                 st.success("✅ Report generated successfully!")
                
#                 # Download button
#                 st.download_button(
#                     label="⬇️ Download Report",
#                     data=pdf_bytes,
#                     file_name=f"attendance_report_{date_str.replace('/', '_')}.pdf",
#                     mime="application/pdf",
#                     use_container_width=True
#                 )
                
#                 # Preview data
#                 st.markdown("#### 👁️ Preview")
                
#                 # Show preview with proper columns
#                 preview_data = []
#                 for _, row in attendance_data.iterrows():
#                     check_in = row.get('checked_in_time', 'N/A')
#                     check_out = row.get('checked_out_time', 'N/A')
                    
#                     # Calculate hours
#                     hours = pdf_manager._calculate_hours(check_in, check_out)
#                     status = "Present" if row.get('is_present', False) else "Absent"
                    
#                     preview_data.append({
#                         'Name': row['name'],
#                         'Date': row['date'],
#                         'Check In': check_in if check_in else 'N/A',
#                         'Check Out': check_out if check_out else 'N/A',
#                         'Hours': hours,
#                         'Status': status
#                     })
                
#                 preview_df = pd.DataFrame(preview_data)
#                 st.dataframe(preview_df, use_container_width=True, hide_index=True)
#             else:
#                 st.error("❌ Failed to generate PDF")

# def date_range_report():
#     """Date range report with user filter - UPDATED"""
    
#     # Date range and user filter
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
    
#     with col2:
#         end_date = st.date_input("End Date", value=date.today(), max_value=date.today())
    
#     with col3:
#         # Get user list for dropdown from API
#         success, users_data = api_client.get_all_users()
#         user_options = {"All Users Combined": None}
        
#         if success and users_data and 'users' in users_data:
#             for user in users_data['users']:
#                 user_options[f"{user['name']} (ID: {user['user_id']})"] = user['user_id']
        
#         selected_user = st.selectbox("User Filter", options=list(user_options.keys()), key="range_user")
#         user_id = user_options[selected_user]
    
#     # Generate button below filters
#     generate_btn = st.button("📄 Generate PDF", use_container_width=True, type="primary", key="range_btn")
    
#     if generate_btn:
#         if start_date > end_date:
#             st.error("❌ Start date must be before end date")
#             return
        
#         # Convert to DD/MM format for backend
#         start_str = start_date.strftime("%d/%m")
#         end_str = end_date.strftime("%d/%m")
        
#         with st.spinner("Generating report..."):
#             # Fetch attendance data from database
#             if user_id:
#                 # Single user - show all records
#                 attendance_data = db_manager.get_user_attendance(user_id, start_str, end_str)
                
#                 if attendance_data is None or attendance_data.empty:
#                     st.warning(f"⚠️ No attendance records found for {start_str} to {end_str}")
#                     return
                
#                 # Generate single user PDF
#                 pdf_bytes = pdf_manager.generate_user_range_report(
#                     attendance_data,
#                     start_str,
#                     end_str,
#                     selected_user
#                 )
                
#             else:
#                 # All users combined - show summary
#                 attendance_data = db_manager.get_attendance_range(start_str, end_str)
                
#                 if attendance_data is None or attendance_data.empty:
#                     st.warning(f"⚠️ No attendance records found for {start_str} to {end_str}")
#                     return
                
#                 # Generate combined users summary PDF
#                 pdf_bytes = pdf_manager.generate_combined_users_summary(
#                     attendance_data,
#                     start_str,
#                     end_str
#                 )
            
#             if pdf_bytes:
#                 st.success("✅ Report generated successfully!")
                
#                 # Download button
#                 filename = f"attendance_{selected_user.split('(')[0].strip() if user_id else 'all_users'}_{start_str.replace('/', '_')}_to_{end_str.replace('/', '_')}.pdf"
#                 st.download_button(
#                     label="⬇️ Download Report",
#                     data=pdf_bytes,
#                     file_name=filename,
#                     mime="application/pdf",
#                     use_container_width=True
#                 )
                
#                 # Statistics
#                 st.markdown("#### 📈 Summary")
#                 col_a, col_b, col_c = st.columns(3)
#                 with col_a:
#                     st.metric("Total Records", len(attendance_data))
#                 with col_b:
#                     unique_users = attendance_data['user_id'].nunique() if 'user_id' in attendance_data else 0
#                     st.metric("Unique Users", unique_users)
#                 with col_c:
#                     unique_days = attendance_data['date'].nunique() if 'date' in attendance_data else 0
#                     st.metric("Days Covered", unique_days)
                
#                 # Preview data
#                 st.markdown("#### 👁️ Preview")
#                 st.dataframe(attendance_data.head(20), use_container_width=True, hide_index=True)
                
#                 if len(attendance_data) > 20:
#                     st.info(f"Showing first 20 of {len(attendance_data)} records. Download PDF for complete report.")
                
#             else:
#                 st.error("❌ Failed to generate PDF")

# # ==================== ABOUT PAGE ====================

# def about_page():
#     """About page with system information"""
    
#     st.markdown("<h1 class='page-title'>ℹ️ About the System</h1>", unsafe_allow_html=True)
    
#     st.markdown("""
#     ## 🔐 Fingerprint Attendance System
    
#     A modern, secure biometric attendance management system powered by:
#     - **Frontend:** Streamlit with custom dark theme
#     - **Backend:** FastAPI RESTful API
#     - **Database:** Neon PostgreSQL (Cloud-hosted)
#     - **Hardware:** ESP32-S3 Fingerprint Module
    
#     ### ✨ Key Features
    
#     - **Secure Authentication:** Admin portal with session management
#     - **User Management:** Full CRUD operations via API
#     - **Multi-Slot Support:** Users can have multiple fingerprint slots
#     - **Real-time Tracking:** Live attendance monitoring
#     - **Advanced Reporting:** PDF reports with late arrival highlighting
#     - **Device Monitoring:** Real-time ESP32 status tracking
    
#     ### 🛠 Technology Stack
    
#     **Frontend Architecture:**
#     - Streamlit (Modern Python web framework)
#     - Custom CSS (Dark security theme)
#     - Responsive design (Mobile-first approach)
    
#     **Backend Services:**
#     - FastAPI (High-performance API framework)
#     - SQLAlchemy ORM (Database abstraction)
#     - Neon PostgreSQL (Serverless database)
    
#     **Hardware Integration:**
#     - ESP32-S3-N16R8 Microcontroller
#     - Capacitive Fingerprint Sensor
#     - WiFi Connectivity
    
#     ### 📊 System Capabilities
    
#     - **Scalable:** Cloud-hosted database with auto-scaling
#     - **Secure:** JWT authentication, encrypted passwords
#     - **Reliable:** API-driven architecture with error handling
#     - **Professional:** Production-ready with clean code separation
    
#     ### 🎯 Use Cases
    
#     - Office attendance tracking
#     - School/University attendance systems
#     - Factory shift management
#     - Secure facility access logging
#     - Remote work monitoring
#     """)

# # ==================== CONTACT PAGE ====================

# def contact_page():
#     """Contact page"""
    
#     st.markdown("<h1 class='page-title'>📞 Contact & Support</h1>", unsafe_allow_html=True)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         ### 🏢 System Information
        
#         **System:** Fingerprint Attendance System  
#         **Version:** 2.0 (Neon PostgreSQL)  
#         **Architecture:** FastAPI + Streamlit  
#         **Status:** Production Ready 🟢
        
#         ---
        
#         ### 📧 Technical Support
        
#         For technical assistance or system issues:
        
#         **Email:** admin@attendance-system.com  
#         **Response Time:** Within 24 hours  
#         **Support Hours:** Monday - Friday, 9 AM - 6 PM
        
#         ---
        
#         ### 🔧 System Administrator
        
#         For administrative access or configuration:
        
#         **Contact:** System Administrator  
#         **Department:** IT Operations
#         """)
    
#     with col2:
#         st.markdown("""
#         ### 🆘 Quick Help
        
#         **Q: Can't login?**  
#         A: Contact your system administrator for credentials.
        
#         **Q: Device showing offline?**  
#         A: Check ESP32 power and network connection.
        
#         **Q: Reports not generating?**  
#         A: Verify date range has attendance records.
        
#         **Q: User update fails?**  
#         A: Ensure slot IDs are comma-separated numbers.
        
#         ---
        
#         ### 📖 Documentation
        
#         - [API Documentation](#)
#         - [User Manual](#)
#         - [Hardware Setup Guide](#)
#         - [Troubleshooting](#)
        
#         ---
        
#         ### 🐛 Report an Issue
#         """)
        
#         with st.form("contact_form"):
#             issue_type = st.selectbox("Issue Type", 
#                 ["Bug Report", "Feature Request", "Hardware Issue", "Other"])
#             description = st.text_area("Description", 
#                 placeholder="Describe the issue in detail...")
            
#             if st.form_submit_button("Submit Report"):
#                 st.success("✅ Report submitted successfully!")
#                 st.info("Our team will review it shortly.")

# # ==================== MAIN APPLICATION ====================

# def main():
#     """Main application logic"""
    
#     # Authentication check
#     if not st.session_state.authenticated:
#         login_page()
#         return
    
#     # Verify token is still valid
#     if not api_client.verify_token():
#         st.error("⚠️ Session expired. Please login again.")
#         st.session_state.authenticated = False
#         st.rerun()
#         return
    
#     # Render sidebar
#     render_sidebar()
    
#     # Render navigation
#     render_navigation()
    
#     # Route to appropriate page
#     if st.session_state.current_page == 'Home':
#         home_page()
#     elif st.session_state.current_page == 'About':
#         about_page()
#     elif st.session_state.current_page == 'Contact':
#         contact_page()

# if __name__ == "__main__":
#     main()




import streamlit as st
from datetime import datetime, date, timedelta
from streamlit_option_menu import option_menu
import requests
import pandas as pd

# Import utility modules
from utils.db_manager import DatabaseManager
from utils.pdf_manager import PDFManager
from utils.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="Fingerprint Attendance System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"  # Always show sidebar by default
)

# Load custom CSS
def load_css():
    try:
        with open('frontend/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("style.css not found. Using default styling.")

load_css()

# Initialize services
@st.cache_resource
def init_services():
    """Initialize database and API clients"""
    db_url = st.secrets.get("DATABASE_URL", "")
    api_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    
    db_manager = DatabaseManager(db_url)
    api_client = APIClient(api_url)
    pdf_manager = PDFManager()
    
    return db_manager, api_client, pdf_manager

db_manager, api_client, pdf_manager = init_services()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# ==================== AUTHENTICATION ====================

def verify_credentials(username: str, password: str) -> bool:
    """Verify admin credentials (hardcoded in backend logic)"""
    # Credentials validation happens on backend
    # This calls the API login endpoint
    success, token = api_client.login(username, password)
    if success:
        st.session_state.token = token
        return True
    return False

def login_page():
    """Secure login page - NO hints about credentials"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <h1 class="login-header">🔐 Fingerprint Attendance System</h1>
            <p class="login-subheader">Secure Admin Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='login-form'>", unsafe_allow_html=True)
        
        # Check API health
        if not api_client.health_check():
            st.error("⚠️ Cannot connect to backend server. Please contact system administrator.")
            st.stop()
        
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username", placeholder="Enter username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    with st.spinner("Authenticating..."):
                        if verify_credentials(username, password):
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== SIDEBAR ====================

def render_sidebar():
    """Render sidebar with device status"""
    
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>🔐 Attendance System</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # ESP32 Device Status - Fetched from API only
    st.sidebar.markdown("### 🔌 Device Status")
    
    with st.spinner("Checking device..."):
        device_status = api_client.get_device_status()
    
    if device_status and device_status.get('connected'):
        # Online
        st.sidebar.markdown("""
        <div class="device-status online">
            <span class="status-dot online-dot"></span>
            <span class="status-text">Online</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Last seen timestamp
        last_seen = device_status.get('last_seen', datetime.now().isoformat())
        st.sidebar.caption(f"Last seen: {last_seen}")
    else:
        # Offline
        st.sidebar.markdown("""
        <div class="device-status offline">
            <span class="status-dot offline-dot"></span>
            <span class="status-text">Offline</span>
        </div>
        """, unsafe_allow_html=True)
        
        last_seen = device_status.get('last_seen', 'Never') if device_status else 'Never'
        st.sidebar.caption(f"Last seen: {last_seen}")
    
    st.sidebar.markdown("---")
    
    # User info
    st.sidebar.markdown(f"**👤 Admin:** {st.session_state.get('username', 'User')}")
    st.sidebar.markdown(f"**📅 Date:** {datetime.now().strftime('%Y-%m-%d')}")
    
    st.sidebar.markdown("---")
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        api_client.logout()
        st.session_state.authenticated = False
        st.session_state.token = None
        st.rerun()

# ==================== NAVIGATION ====================

def render_navigation():
    """Professional navigation bar using streamlit-option-menu"""
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "About", "Contact"],
        icons=["house", "info-circle", "envelope"],
        menu_icon="cast",
        default_index=0 if st.session_state.current_page == "Home" else 
                      1 if st.session_state.current_page == "About" else 2,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#1a1a2e"},
            "icon": {"color": "#00d4ff", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "padding": "10px 20px",
                "--hover-color": "#16213e",
            },
            "nav-link-selected": {"background-color": "#2E3192"},
        }
    )
    
    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.rerun()

# ==================== HOME PAGE ====================

def home_page():
    """Admin Dashboard - Main page"""
    
    st.markdown("<h1 class='page-title'>🏠 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    # Dashboard metrics
    stats = api_client.get_dashboard_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">👥</div>
                <div class="metric-value">{stats.get('total_users', 0)}</div>
                <div class="metric-label">Total Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card metric-success">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{stats.get('today_records', 0)}</div>
                <div class="metric-label">Today's Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card metric-info">
                <div class="metric-icon">📥</div>
                <div class="metric-value">{stats.get('checked_in', 0)}</div>
                <div class="metric-label">Checked In</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card metric-warning">
                <div class="metric-icon">📤</div>
                <div class="metric-value">{stats.get('checked_out', 0)}</div>
                <div class="metric-label">Checked Out</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["👥 Manage Users", "📊 Attendance Reports"])
    
    with tab1:
        manage_users_tab()
    
    with tab2:
        attendance_reports_tab()

# ==================== MANAGE USERS TAB ====================

def manage_users_tab():
    """Data management - Display and update users"""
    
    st.markdown("### 👥 User Management")
    
    # Fetch all users from API
    success, users_data = api_client.get_all_users()
    
    if not success or not users_data or 'users' not in users_data:
        st.info("ℹ️ No users found in the system.")
        return
    
    users_list = users_data['users']
    
    if not users_list:
        st.info("ℹ️ No users found in the system.")
        return
    
    df_data = []
    for user in users_list:
        df_data.append({
            'User ID': user['user_id'],
            'Name': user['name'],
            'Slot IDs': ', '.join(map(str, user['slot_id'])),
            'Salary (Daily)': user.get('salary') if user.get('salary') is not None else "",
            'Templates': user['total_templates'],
            'Enrolled': user['date'],
            'Time': user['time']
        })
    
    users_df = pd.DataFrame(df_data)
    
    # Display users in data table
    st.markdown("#### All Users")
    st.dataframe(users_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Update user section
    st.markdown("#### ✏️ Update User")
    
    # User selection
    user_options = {f"{user['name']} (ID: {user['user_id']})": user['user_id'] 
                   for user in users_list}
    
    if user_options:
        selected_user = st.selectbox("Select User to Update", options=list(user_options.keys()))
        user_id = user_options[selected_user]
        
        # Get selected user data
        selected_user_data = next((u for u in users_list if u['user_id'] == user_id), None)
        
        if selected_user_data:
            with st.form("update_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Name", value=selected_user_data['name'])
                    new_salary = st.number_input(
                        "Salary (Daily)",
                        min_value=0.0,
                        value=float(selected_user_data['salary']) if selected_user_data.get('salary') is not None else 0.0,
                        step=100.0
                    )

                with col2:
                    current_slots = selected_user_data.get('slot_id', [])
                    slot_ids_str = ', '.join(map(str, current_slots)) if current_slots else ''
                    new_slot_ids = st.text_input("Slot IDs (comma-separated)", value=slot_ids_str)
                
                submitted = st.form_submit_button("💾 Update User", use_container_width=True)
                
                if submitted:
                    # Parse slot IDs
                    try:
                        slot_ids_list = [int(x.strip()) for x in new_slot_ids.split(',') if x.strip()]
                    except ValueError:
                        st.error("❌ Invalid slot IDs format. Use comma-separated numbers.")
                        return
                    
                    # Call API to update user
                    with st.spinner("Updating user..."):
                        success, message = api_client.update_user(
                        user_id=user_id,
                        name=new_name,
                        slot_ids=slot_ids_list,
                        salary=new_salary if new_salary > 0 else None
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

# ==================== ATTENDANCE REPORTS TAB ====================

def attendance_reports_tab():
    """Reporting engine with PDF generation"""
    
    st.markdown("### 📊 Attendance Reports")
    
    # Report type selection
    report_type = st.radio(
        "Select Report Type",
        ["📅 Single Day Report", "📆 Date Range Report"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if report_type == "📅 Single Day Report":
        single_day_report()
    else:
        date_range_report()

def single_day_report():
    """Single day report with user filter - UPDATED LAYOUT"""
    
    # Date and User Filter in columns
    col1, col2 = st.columns(2)
    
    with col1:
        selected_date = st.date_input("Select Date", value=date.today(), max_value=date.today())
    
    with col2:
        # Get user list for dropdown from API
        success, users_data = api_client.get_all_users()
        user_options = {"All Users Combined": None}
        
        if success and users_data and 'users' in users_data:
            for user in users_data['users']:
                user_options[f"{user['name']} (ID: {user['user_id']})"] = user['user_id']
        
        selected_user = st.selectbox("User Filter", options=list(user_options.keys()))
        user_id = user_options[selected_user]
    
    # Generate PDF button below filters
    generate_btn = st.button("📄 Generate PDF", use_container_width=True, type="primary")
    
    if generate_btn:
        # Convert to DD/MM format for backend
        date_str = selected_date.strftime("%d/%m")
        
        with st.spinner("Generating report..."):
            # Fetch attendance data from database
            if user_id:
                attendance_data = db_manager.get_user_attendance(user_id, date_str, date_str)
            else:
                attendance_data = db_manager.get_attendance_by_date(date_str)
            
            if attendance_data is None or attendance_data.empty:
                st.warning(f"⚠️ No attendance records found for {date_str}")
                return
            
            # Generate PDF
            pdf_bytes = pdf_manager.generate_daily_report(
                attendance_data,
                date_str,
                user_name=selected_user if user_id else None
            )
            
            if pdf_bytes:
                st.success("✅ Report generated successfully!")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Report",
                    data=pdf_bytes,
                    file_name=f"attendance_report_{date_str.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Preview data
                st.markdown("#### 👁️ Preview")
                
                # Show preview with proper columns
                preview_data = []
                for _, row in attendance_data.iterrows():
                    check_in = row.get('checked_in_time', 'N/A')
                    check_out = row.get('checked_out_time', 'N/A')
                    
                    # Calculate hours
                    hours = pdf_manager._calculate_hours(check_in, check_out)
                    status = "Present" if row.get('is_present', False) else "Absent"
                    
                    preview_data.append({
                        'Name': row['name'],
                        'Date': row['date'],
                        'Check In': check_in if check_in else 'N/A',
                        'Check Out': check_out if check_out else 'N/A',
                        'Hours': hours,
                        'Status': status
                    })
                
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
            else:
                st.error("❌ Failed to generate PDF")

def date_range_report():
    """Date range report with user filter - UPDATED"""
    
    # Date range and user filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
    
    with col2:
        end_date = st.date_input("End Date", value=date.today(), max_value=date.today())
    
    with col3:
        # Get user list for dropdown from API
        success, users_data = api_client.get_all_users()
        user_options = {"All Users Combined": None}
        
        if success and users_data and 'users' in users_data:
            for user in users_data['users']:
                user_options[f"{user['name']} (ID: {user['user_id']})"] = user['user_id']
        
        selected_user = st.selectbox("User Filter", options=list(user_options.keys()), key="range_user")
        user_id = user_options[selected_user]
    
    # Generate button below filters
    generate_btn = st.button("📄 Generate PDF", use_container_width=True, type="primary", key="range_btn")
    
    if generate_btn:
        if start_date > end_date:
            st.error("❌ Start date must be before end date")
            return
        
        # Convert to DD/MM format for backend
        start_str = start_date.strftime("%d/%m")
        end_str = end_date.strftime("%d/%m")
        
        with st.spinner("Generating report..."):
            # Fetch attendance data from database
            if user_id:
                # Single user - show all records
                attendance_data = db_manager.get_user_attendance(user_id, start_str, end_str)
                
                if attendance_data is None or attendance_data.empty:
                    st.warning(f"⚠️ No attendance records found for {start_str} to {end_str}")
                    return
                
                # Generate single user PDF
                pdf_bytes = pdf_manager.generate_user_range_report(
                    attendance_data,
                    start_str,
                    end_str,
                    selected_user
                )
                
            else:
                # All users combined - show summary
                attendance_data = db_manager.get_attendance_range(start_str, end_str)
                
                if attendance_data is None or attendance_data.empty:
                    st.warning(f"⚠️ No attendance records found for {start_str} to {end_str}")
                    return
                
                # Generate combined users summary PDF
                pdf_bytes = pdf_manager.generate_combined_users_summary(
                    attendance_data,
                    start_str,
                    end_str
                )
            
            if pdf_bytes:
                st.success("✅ Report generated successfully!")
                
                # Download button
                filename = f"attendance_{selected_user.split('(')[0].strip() if user_id else 'all_users'}_{start_str.replace('/', '_')}_to_{end_str.replace('/', '_')}.pdf"
                st.download_button(
                    label="⬇️ Download Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Statistics
                st.markdown("#### 📈 Summary")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Records", len(attendance_data))
                with col_b:
                    unique_users = attendance_data['user_id'].nunique() if 'user_id' in attendance_data else 0
                    st.metric("Unique Users", unique_users)
                with col_c:
                    unique_days = attendance_data['date'].nunique() if 'date' in attendance_data else 0
                    st.metric("Days Covered", unique_days)
                
                # Preview data
                st.markdown("#### 👁️ Preview")
                st.dataframe(attendance_data.head(20), use_container_width=True, hide_index=True)
                
                if len(attendance_data) > 20:
                    st.info(f"Showing first 20 of {len(attendance_data)} records. Download PDF for complete report.")
                
            else:
                st.error("❌ Failed to generate PDF")

# ==================== ABOUT PAGE ====================

def about_page():
    """About page with system information"""
    
    st.markdown("<h1 class='page-title'>ℹ️ About the System</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ## 🔐 Fingerprint Attendance System
    
    A modern, secure biometric attendance management system powered by:
    - **Frontend:** Streamlit with custom dark theme
    - **Backend:** FastAPI RESTful API
    - **Database:** Neon PostgreSQL (Cloud-hosted)
    - **Hardware:** ESP32-S3 Fingerprint Module
    
    ### ✨ Key Features
    
    - **Secure Authentication:** Admin portal with session management
    - **User Management:** Full CRUD operations via API
    - **Multi-Slot Support:** Users can have multiple fingerprint slots
    - **Real-time Tracking:** Live attendance monitoring
    - **Advanced Reporting:** PDF reports with late arrival highlighting
    - **Device Monitoring:** Real-time ESP32 status tracking
    
    ### 🛠 Technology Stack
    
    **Frontend Architecture:**
    - Streamlit (Modern Python web framework)
    - Custom CSS (Dark security theme)
    - Responsive design (Mobile-first approach)
    
    **Backend Services:**
    - FastAPI (High-performance API framework)
    - SQLAlchemy ORM (Database abstraction)
    - Neon PostgreSQL (Serverless database)
    
    **Hardware Integration:**
    - ESP32-S3-N16R8 Microcontroller
    - Capacitive Fingerprint Sensor
    - WiFi Connectivity
    
    ### 📊 System Capabilities
    
    - **Scalable:** Cloud-hosted database with auto-scaling
    - **Secure:** JWT authentication, encrypted passwords
    - **Reliable:** API-driven architecture with error handling
    - **Professional:** Production-ready with clean code separation
    
    ### 🎯 Use Cases
    
    - Office attendance tracking
    - School/University attendance systems
    - Factory shift management
    - Secure facility access logging
    - Remote work monitoring
    """)

# ==================== CONTACT PAGE ====================

def contact_page():
    """Contact page"""
    
    st.markdown("<h1 class='page-title'>📞 Contact & Support</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏢 System Information
        
        **System:** Fingerprint Attendance System  
        **Version:** 2.0 (Neon PostgreSQL)  
        **Architecture:** FastAPI + Streamlit  
        **Status:** Production Ready 🟢
        
        ---
        
        ### 📧 Technical Support
        
        For technical assistance or system issues:
        
        **Email:** admin@attendance-system.com  
        **Response Time:** Within 24 hours  
        **Support Hours:** Monday - Friday, 9 AM - 6 PM
        
        ---
        
        ### 🔧 System Administrator
        
        For administrative access or configuration:
        
        **Contact:** System Administrator  
        **Department:** IT Operations
        """)
    
    with col2:
        st.markdown("""
        ### 🆘 Quick Help
        
        **Q: Can't login?**  
        A: Contact your system administrator for credentials.
        
        **Q: Device showing offline?**  
        A: Check ESP32 power and network connection.
        
        **Q: Reports not generating?**  
        A: Verify date range has attendance records.
        
        **Q: User update fails?**  
        A: Ensure slot IDs are comma-separated numbers.
        
        ---
        
        ### 📖 Documentation
        
        - [API Documentation](#)
        - [User Manual](#)
        - [Hardware Setup Guide](#)
        - [Troubleshooting](#)
        
        ---
        
        ### 🐛 Report an Issue
        """)
        
        with st.form("contact_form"):
            issue_type = st.selectbox("Issue Type", 
                ["Bug Report", "Feature Request", "Hardware Issue", "Other"])
            description = st.text_area("Description", 
                placeholder="Describe the issue in detail...")
            
            if st.form_submit_button("Submit Report"):
                st.success("✅ Report submitted successfully!")
                st.info("Our team will review it shortly.")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application logic"""
    
    # Authentication check
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Verify token is still valid
    if not api_client.verify_token():
        st.error("⚠️ Session expired. Please login again.")
        st.session_state.authenticated = False
        st.rerun()
        return
    
    # Render sidebar
    render_sidebar()
    
    # Render navigation
    render_navigation()
    
    # Route to appropriate page
    if st.session_state.current_page == 'Home':
        home_page()
    elif st.session_state.current_page == 'About':
        about_page()
    elif st.session_state.current_page == 'Contact':
        contact_page()

if __name__ == "__main__":
    main()