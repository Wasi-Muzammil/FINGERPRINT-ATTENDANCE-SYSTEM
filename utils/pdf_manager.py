
"""
PDF Manager - Modular PDF generation with ReportLab
Zero Streamlit dependencies
✅ WITH SALARY CALCULATIONS INTEGRATED
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, time as dt_time, timedelta
import io
import pandas as pd
from typing import Optional

class PDFManager:
    """Manages all PDF generation operations with salary calculations"""
    
    def __init__(self):
        """Initialize PDF manager with styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Custom heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        # Custom normal style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT
        )
        
        # Late arrival highlight color
        self.late_color = colors.HexColor('#ff6b6b')
        self.on_time_color = colors.HexColor('#51cf66')
        
        # ✅ Standard work hours (9:15 AM is the start time)
        self.standard_start_time = dt_time(9, 15)  # 9:15 AM
    
    def _create_header(self, title: str, subtitle: str = None) -> list:
        """Create PDF header with title and subtitle"""
        story = []
        
        # Title
        title_para = Paragraph(title, self.title_style)
        story.append(title_para)
        
        # Subtitle if provided
        if subtitle:
            subtitle_para = Paragraph(subtitle, self.normal_style)
            story.append(subtitle_para)
        
        # Generation timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_para = Paragraph(
            f"<i>Generated on: {timestamp}</i>",
            self.normal_style
        )
        story.append(timestamp_para)
        
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _calculate_hours(self, check_in, check_out) -> float:
        """
        Calculate working hours between check-in and check-out
        Returns float hours (e.g., 8.5) or 0 if invalid
        """
        if pd.isna(check_in) or pd.isna(check_out) or check_in is None or check_out is None:
            return 0.0
        
        try:
            # Handle time strings in HH:MM format
            if isinstance(check_in, str):
                check_in_time = datetime.strptime(check_in, "%H:%M").time()
            else:
                check_in_time = check_in
            
            if isinstance(check_out, str):
                check_out_time = datetime.strptime(check_out, "%H:%M").time()
            else:
                check_out_time = check_out
            
            # Convert to datetime for calculation
            today = datetime.now().date()
            dt_in = datetime.combine(today, check_in_time)
            dt_out = datetime.combine(today, check_out_time)
            
            # Handle overnight shifts
            if dt_out < dt_in:
                dt_out = dt_out + timedelta(days=1)
            
            hours = (dt_out - dt_in).total_seconds() / 3600
            return hours
        except:
            return 0.0
    
    def _format_hours(self, hours: float) -> str:
        """Format hours as string"""
        return f"{hours:.2f}h" if hours > 0 else "N/A"
    
    def _is_late_arrival(self, check_in) -> bool:
        """
        Check if check-in time is after 9:15 AM
        ✅ Returns True if late, False otherwise
        """
        if pd.isna(check_in) or check_in is None or check_in == 'N/A':
            return False
        
        try:
            if isinstance(check_in, str):
                check_in_time = datetime.strptime(check_in, "%H:%M").time()
            else:
                check_in_time = check_in
            
            return check_in_time > self.standard_start_time
        except:
            return False
    
    def _calculate_daily_salary(self, salary: float, check_in, check_out) -> float:
        """
        ✅ Calculate daily salary based on hours worked
        Formula: (Daily Salary / 8) * Hours Worked
        
        Args:
            salary: Daily salary
            check_in: Check-in time
            check_out: Check-out time
        
        Returns:
            Calculated salary for the day
        """
        if salary is None or salary <= 0:
            return 0.0
        
        hours_worked = self._calculate_hours(check_in, check_out)
        
        if hours_worked <= 0:
            return 0.0
        
        # Formula: (Salary / 8) * hours_worked
        salary_value = float(salary)
        hourly_rate = salary_value / 8.0
        daily_total = hourly_rate * hours_worked
        
        return daily_total
    
    def generate_daily_report(
        self,
        attendance_data: pd.DataFrame,
        date_str: str,
        user_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        ✅ Generate daily attendance PDF report WITH SALARY
        
        Args:
            attendance_data: DataFrame with attendance records (must include 'salary' column)
            date_str: Date in DD/MM format
            user_name: Optional user name filter
        
        Returns:
            PDF as bytes or None if failed
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            story = []
            
            # Header
            title = "Daily Attendance Report"
            subtitle = f"<b>Date:</b> {date_str}"
            if user_name:
                subtitle += f" | <b>User:</b> {user_name}"
            
            story.extend(self._create_header(title, subtitle))
            
            # ✅ Prepare table data with SALARY and TOTAL columns
            table_data = [['#', 'Name', 'Date', 'Check In', 'Check Out', 'Hours', 'Salary', 'Total', 'Status']]
            
            total_salary_sum = 0.0
            
            for idx, row in attendance_data.iterrows():
                # Format times
                check_in_time = row.get('checked_in_time', 'N/A')
                check_out_time = row.get('checked_out_time', 'N/A')
                status = "Present" if row.get('is_present', False) else "Absent"
                
                # Calculate hours
                hours = self._calculate_hours(check_in_time, check_out_time)
                hours_str = self._format_hours(hours)
                
                # ✅ Get salary and calculate total
                salary = row.get('salary')
                salary_str = f"{float(salary):.2f}" if salary is not None and salary > 0 else ""
                
                daily_total = self._calculate_daily_salary(salary, check_in_time, check_out_time)
                total_str = f"{daily_total:.2f}" if daily_total > 0 else ""
                
                if daily_total > 0:
                    total_salary_sum += daily_total
                
                table_data.append([
                    str(idx + 1),
                    str(row['name']),
                    str(row['date']),
                    check_in_time if check_in_time and check_in_time != 'N/A' else 'N/A',
                    check_out_time if check_out_time and check_out_time != 'N/A' else 'N/A',
                    hours_str,
                    salary_str,
                    total_str,
                    status
                ])
            
            # Create table
            table = Table(
                table_data,
                colWidths=[0.3*inch, 1.5*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.7*inch]
            )
            
            # Table styling
            table_style = [
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Body
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Footer with statistics
            story.append(Spacer(1, 0.3*inch))
            
            total_records = len(attendance_data)
            present_count = attendance_data['is_present'].sum() if 'is_present' in attendance_data else 0
            
            footer_text = f"""
            <b>Summary:</b><br/>
            • Total Records: {total_records}<br/>
            • Present: {present_count}<br/>
            • Total Salary Paid: Rs. {total_salary_sum:.2f}
            """
            footer_para = Paragraph(footer_text, self.normal_style)
            story.append(footer_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating daily report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_user_range_report(
        self,
        attendance_data: pd.DataFrame,
        start_date: str,
        end_date: str,
        user_name: str
    ) -> Optional[bytes]:
        """
        ✅ Generate date range report for SINGLE USER with salary calculations
        Shows ALL records including absent days
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                rightMargin=0.5 * inch
            )

            story = []

            title = f"Attendance Report - {user_name}"
            subtitle = f"<b>Period:</b> {start_date} to {end_date}"
            story.extend(self._create_header(title, subtitle))

            table_data = [
                ['#', 'Name', 'Date', 'Check In', 'Check Out', 'Hours', 'Salary', 'Total', 'Status']
            ]

            # ==========================
            # ✅ FIXED DATE PARSING (DD/MM)
            # ==========================
            current_year = datetime.now().year

            start_dt = datetime.strptime(f"{start_date}/{current_year}", "%d/%m/%Y").date()
            end_dt = datetime.strptime(f"{end_date}/{current_year}", "%d/%m/%Y").date()

            # Handle year rollover (e.g. 27/12 → 03/01)
            if end_dt < start_dt:
                end_dt = end_dt.replace(year=current_year + 1)

            all_dates = pd.date_range(start=start_dt, end=end_dt)

            attendance_map = {
                str(row['date']): row
                for _, row in attendance_data.iterrows()
            }

            grand_total = 0.0
            total_hours = 0.0
            present_count = 0
            absent_count = 0
            row_index = 1

            for day in all_dates:
                date_str = day.strftime("%d/%m")
                row = attendance_map.get(date_str)

                if row is not None:
                    check_in = row.get('checked_in_time', 'N/A')
                    check_out = row.get('checked_out_time', 'N/A')
                    is_present = row.get('is_present', False)
                    salary = row.get('salary')
                    name = row.get('name', user_name)
                else:
                    check_in = 'N/A'
                    check_out = 'N/A'
                    is_present = False
                    salary = attendance_data.iloc[0].get('salary') if not attendance_data.empty else None
                    name = user_name

                status = "Present" if is_present else "Absent"

                if is_present:
                    present_count += 1
                else:
                    absent_count += 1

                hours = self._calculate_hours(check_in, check_out)
                total_hours += hours
                hours_str = self._format_hours(hours)

                salary_str = f"{float(salary):.2f}" if salary is not None and salary > 0 else ""
                daily_total = self._calculate_daily_salary(salary, check_in, check_out)
                total_str = f"{daily_total:.2f}" if daily_total > 0 else ""

                grand_total += daily_total

                table_data.append([
                    str(row_index),
                    name,
                    date_str,
                    check_in,
                    check_out,
                    hours_str,
                    salary_str,
                    total_str,
                    status
                ])

                row_index += 1

            table = Table(
                table_data,
                colWidths=[
                    0.3 * inch, 1.5 * inch, 0.7 * inch,
                    0.8 * inch, 0.8 * inch, 0.7 * inch,
                    0.8 * inch, 0.8 * inch, 0.7 * inch
                ]
            )

            # Table styling 
            table_style = [ 
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), 
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), 
            ('FONTSIZE', (0, 0), (-1, 0), 9), 
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12), 
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige), 
            ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), 
            ('FONTSIZE', (0, 1), (-1, -1), 8), 
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
            [colors.white, colors.lightgrey]) 
            ]
            table.setStyle(TableStyle(table_style))

            story.append(table)
            story.append(Spacer(1, 0.3 * inch))

            total_days = len(all_dates)
            avg_hours = total_hours / total_days if total_days else 0

            story.append(Paragraph(f"""
            <b>Summary Statistics:</b><br/>
            • Total Days: {total_days}<br/>
            • Present: {present_count}<br/>
            • Absent: {absent_count}<br/>
            • Total Hours: {total_hours:.2f}h<br/>
            • Average Hours/Day: {avg_hours:.2f}h<br/>
            • <b>GRAND TOTAL SALARY: Rs. {grand_total:.2f}</b>
            """, self.normal_style))

            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            print(f"Error generating user range report: {e}")
            import traceback
            traceback.print_exc()
            return None


    
    def generate_combined_users_summary(
        self,
        attendance_data: pd.DataFrame,
        start_date: str,
        end_date: str
    ) -> Optional[bytes]:
        """
        ✅ Generate date range summary for ALL USERS COMBINED with salary calculations
        One row per user with: Employee, Salary (Daily), Present Days, Absent Days, Total Salary
        Total Salary = Sum of daily salaries for all days in range using the formula
        
        Args:
            attendance_data: DataFrame with all users' attendance records (must include 'salary' column)
            start_date: Start date in DD/MM format
            end_date: End date in DD/MM format
        
        Returns:
            PDF as bytes or None if failed
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            story = []
            
            # Header
            title = "Attendance Summary Report - All Employees"
            subtitle = f"<b>Period:</b> {start_date} to {end_date}"
            
            story.extend(self._create_header(title, subtitle))
            
            # ✅ Calculate summary for each user
            summary_data = []
            
            for user_id in attendance_data['user_id'].unique():
                user_records = attendance_data[attendance_data['user_id'] == user_id]
                
                if user_records.empty:
                    continue
                
                employee_name = user_records.iloc[0]['name']
                
                # Get salary (should be same for all records of this user)
                salary = user_records.iloc[0].get('salary')
                salary_value = float(salary) if salary is not None and salary > 0 else 0.0
                
                # Count present/absent days
                present_days = user_records['is_present'].sum() if 'is_present' in user_records else 0
                total_days = len(user_records)
                absent_days = total_days - present_days
                
                # ✅ Calculate total salary for this employee in the range
                total_salary_earned = 0.0
                
                for _, row in user_records.iterrows():
                    check_in = row.get('checked_in_time')
                    check_out = row.get('checked_out_time')
                    
                    daily_total = self._calculate_daily_salary(salary_value, check_in, check_out)
                    total_salary_earned += daily_total
                
                summary_data.append({
                    'employee': employee_name,
                    'salary': salary_value,
                    'present': present_days,
                    'absent': absent_days,
                    'total_salary': total_salary_earned
                })
            
            # Create table
            table_data = [['#', 'Employee', 'Salary (Daily)', 'Present Days', 'Absent Days', 'Total Salary']]
            
            grand_total_paid = 0.0
            
            for idx, summary in enumerate(summary_data, 1):
                salary_str = f"{summary['salary']:.2f}" if summary['salary'] > 0 else ""
                total_str = f"{summary['total_salary']:.2f}" if summary['total_salary'] > 0 else "0.00"
                
                grand_total_paid += summary['total_salary']
                
                table_data.append([
                    str(idx),
                    summary['employee'],
                    salary_str,
                    str(summary['present']),
                    str(summary['absent']),
                    total_str
                ])
            
            # Create table
            table = Table(
                table_data,
                colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch]
            )
            
            # Table styling
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Overall summary
            story.append(Spacer(1, 0.3*inch))
            
            total_employees = len(summary_data)
            total_present = sum(s['present'] for s in summary_data)
            total_absent = sum(s['absent'] for s in summary_data)
            
            summary_text = f"""
            <b>Overall Statistics:</b><br/>
            • Total Employees: {total_employees}<br/>
            • Total Present Days: {total_present}<br/>
            • Total Absent Days: {total_absent}<br/>
            • <b>TOTAL PAID TO ALL EMPLOYEES: Rs. {grand_total_paid:.2f}</b>
            """
            
            summary_para = Paragraph(summary_text, self.normal_style)
            story.append(summary_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating combined users summary: {e}")
            import traceback
            traceback.print_exc()
            return None