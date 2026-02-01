
"""
PDF Manager - Modular PDF generation with ReportLab
Zero Streamlit dependencies
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import pandas as pd
from typing import Optional

class PDFManager:
    """Manages all PDF generation operations"""
    
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
    
    def _calculate_hours(self, check_in, check_out) -> str:
        """Calculate working hours between check-in and check-out"""
        if pd.isna(check_in) or pd.isna(check_out) or check_in is None or check_out is None:
            return "N/A"
        
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
                dt_out = datetime.combine(today, check_out_time) + pd.Timedelta(days=1)
            
            hours = (dt_out - dt_in).total_seconds() / 3600
            return f"{hours:.2f}h"
        except:
            return "N/A"
    
    def generate_daily_report(
        self,
        attendance_data: pd.DataFrame,
        date_str: str,
        user_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate daily attendance PDF report
        
        Args:
            attendance_data: DataFrame with attendance records
            date_str: Date in YYYY-MM-DD format
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
            
            # Prepare table data
            table_data = [['#', 'Name', 'Date', 'Check In', 'Check Out', 'Status']]
            
            for idx, row in attendance_data.iterrows():
                # Format times
                check_in_time = row.get('checked_in_time', 'N/A')
                check_out_time = row.get('checked_out_time', 'N/A')
                status = "Present" if row.get('is_present', False) else "Absent"
                
                table_data.append([
                    str(idx + 1),
                    str(row['name']),
                    str(row['date']),  # DD/MM format
                    check_in_time if check_in_time else 'N/A',
                    check_out_time if check_out_time else 'N/A',
                    status
                ])
            
            # Create table
            table = Table(
                table_data,
                colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1*inch, 1*inch]
            )
            
            # Table styling
            table_style = [
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Body
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
            
            # Highlight late arrivals
            for idx, row in attendance_data.iterrows():
                if row.get('is_late', False):
                    table_style.append(
                        ('BACKGROUND', (-1, idx + 1), (-1, idx + 1), self.late_color)
                    )
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Footer with statistics
            story.append(Spacer(1, 0.3*inch))
            
            total_records = len(attendance_data)
            late_count = attendance_data['is_late'].sum() if 'is_late' in attendance_data else 0
            
            footer_text = f"<b>Summary:</b> Total Records: {total_records} | Late Arrivals: {late_count}"
            footer_para = Paragraph(footer_text, self.normal_style)
            story.append(footer_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating daily report: {e}")
            return None
    
    def generate_range_report(
        self,
        attendance_data: pd.DataFrame,
        start_date: str,
        end_date: str,
        user_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate date range attendance PDF report with working hours
        
        Args:
            attendance_data: DataFrame with attendance records
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
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
            title = "Attendance Report"
            subtitle = f"<b>Period:</b> {start_date} to {end_date}"
            if user_name:
                subtitle += f" | <b>User:</b> {user_name}"
            
            story.extend(self._create_header(title, subtitle))
            
            # Group data by user and date to show daily summary
            summary_data = []
            
            for (user_id, name, dept, date), group in attendance_data.groupby(['user_id', 'name', 'department', 'date']):
                # Get first IN and last OUT
                check_in = group[group['status'] == 'IN']['time'].min() if 'IN' in group['status'].values else None
                check_out = group[group['status'] == 'OUT']['time'].max() if 'OUT' in group['status'].values else None
                
                # Calculate hours
                hours = self._calculate_hours(check_in, check_out)
                
                # Check if late
                is_late = group['is_late'].any() if 'is_late' in group else False
                
                summary_data.append({
                    'name': name,
                    'department': dept,
                    'date': date,
                    'check_in': check_in.strftime("%H:%M") if check_in else "N/A",
                    'check_out': check_out.strftime("%H:%M") if check_out else "N/A",
                    'hours': hours,
                    'is_late': is_late
                })
            
            # Create table
            table_data = [['#', 'Name', 'Department', 'Date', 'Check In', 'Check Out', 'Hours', 'Late']]
            
            for idx, row in enumerate(summary_data, 1):
                late_indicator = "⚠️" if row['is_late'] else "✓"
                
                table_data.append([
                    str(idx),
                    row['name'],
                    row['department'],
                    str(row['date']),
                    row['check_in'],
                    row['check_out'],
                    row['hours'],
                    late_indicator
                ])
            
            # Create table
            table = Table(
                table_data,
                colWidths=[0.4*inch, 1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.5*inch]
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
            
            # Highlight late arrivals
            for idx, row in enumerate(summary_data):
                if row['is_late']:
                    table_style.append(
                        ('BACKGROUND', (-1, idx + 1), (-1, idx + 1), self.late_color)
                    )
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Statistics
            story.append(Spacer(1, 0.3*inch))
            
            total_days = len(set([r['date'] for r in summary_data]))
            total_records = len(summary_data)
            late_count = sum([1 for r in summary_data if r['is_late']])
            
            stats_text = f"""
            <b>Summary Statistics:</b><br/>
            • Total Records: {total_records}<br/>
            • Days Covered: {total_days}<br/>
            • Late Arrivals: {late_count}<br/>
            • On-Time: {total_records - late_count}
            """
            
            stats_para = Paragraph(stats_text, self.normal_style)
            story.append(stats_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating range report: {e}")
            return None
    
    def generate_user_range_report(
        self,
        attendance_data: pd.DataFrame,
        start_date: str,
        end_date: str,
        user_name: str
    ) -> Optional[bytes]:
        """
        Generate date range report for SINGLE USER with all records
        Shows ALL attendance rows with pagination (max 31 per page)
        Columns: Name, Date, Check In, Check Out, Hours, Status
        
        Args:
            attendance_data: DataFrame with user's attendance records
            start_date: Start date in DD/MM format
            end_date: End date in DD/MM format
            user_name: User's name
        
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
            title = f"Attendance Report - {user_name}"
            subtitle = f"<b>Period:</b> {start_date} to {end_date}"
            
            story.extend(self._create_header(title, subtitle))
            
            # Process records in chunks of 31 (for pagination)
            RECORDS_PER_PAGE = 31
            total_records = len(attendance_data)
            
            for chunk_start in range(0, total_records, RECORDS_PER_PAGE):
                chunk_end = min(chunk_start + RECORDS_PER_PAGE, total_records)
                chunk_data = attendance_data.iloc[chunk_start:chunk_end]
                
                # Table header
                table_data = [['#', 'Name', 'Date', 'Check In', 'Check Out', 'Hours', 'Status']]
                
                for idx, row in chunk_data.iterrows():
                    # Get times
                    check_in = row.get('checked_in_time', 'N/A')
                    check_out = row.get('checked_out_time', 'N/A')
                    
                    # Calculate hours
                    hours = self._calculate_hours(check_in, check_out)
                    
                    # Status
                    status = "Present" if row.get('is_present', False) else "Absent"
                    
                    table_data.append([
                        str(chunk_start + len(table_data)),
                        str(row['name']),
                        str(row['date']),
                        check_in if check_in else 'N/A',
                        check_out if check_out else 'N/A',
                        hours,
                        status
                    ])
                
                # Create table
                table = Table(
                    table_data,
                    colWidths=[0.4*inch, 1.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.9*inch]
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
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
                
                table.setStyle(TableStyle(table_style))
                story.append(table)
                
                # Add page break if more chunks exist
                if chunk_end < total_records:
                    story.append(Spacer(1, 0.5*inch))
            
            # Summary at the end
            story.append(Spacer(1, 0.3*inch))
            
            present_count = attendance_data['is_present'].sum() if 'is_present' in attendance_data else 0
            absent_count = total_records - present_count
            
            # Calculate total hours
            total_hours = 0
            hours_count = 0
            for _, row in attendance_data.iterrows():
                check_in = row.get('checked_in_time')
                check_out = row.get('checked_out_time')
                if check_in and check_out:
                    hours_str = self._calculate_hours(check_in, check_out)
                    if hours_str != "N/A":
                        try:
                            hours_val = float(hours_str.replace('h', ''))
                            total_hours += hours_val
                            hours_count += 1
                        except:
                            pass
            
            avg_hours = total_hours / hours_count if hours_count > 0 else 0
            
            summary_text = f"""
            <b>Summary Statistics:</b><br/>
            • Total Days: {total_records}<br/>
            • Present: {present_count}<br/>
            • Absent: {absent_count}<br/>
            • Total Hours: {total_hours:.2f}h<br/>
            • Average Hours/Day: {avg_hours:.2f}h
            """
            
            summary_para = Paragraph(summary_text, self.normal_style)
            story.append(summary_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating user range report: {e}")
            return None
    
    def generate_combined_users_summary(
        self,
        attendance_data: pd.DataFrame,
        start_date: str,
        end_date: str
    ) -> Optional[bytes]:
        """
        Generate date range summary for ALL USERS COMBINED
        One row per user with: Employee, Present Days, Absent Days, Avg Hours/Day, Late Arrivals
        
        Args:
            attendance_data: DataFrame with all users' attendance records
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
            
            # Calculate summary for each user
            summary_data = []
            
            for user_id in attendance_data['user_id'].unique():
                user_records = attendance_data[attendance_data['user_id'] == user_id]
                
                if user_records.empty:
                    continue
                
                employee_name = user_records.iloc[0]['name']
                
                # Count present/absent days
                present_days = user_records['is_present'].sum() if 'is_present' in user_records else 0
                total_days = len(user_records)
                absent_days = total_days - present_days
                
                # Calculate average hours
                total_hours = 0
                hours_count = 0
                late_arrivals = 0
                
                for _, row in user_records.iterrows():
                    check_in = row.get('checked_in_time')
                    check_out = row.get('checked_out_time')
                    
                    if check_in and check_out:
                        hours_str = self._calculate_hours(check_in, check_out)
                        if hours_str != "N/A":
                            try:
                                hours_val = float(hours_str.replace('h', ''))
                                total_hours += hours_val
                                hours_count += 1
                            except:
                                pass
                    
                    # Check for late arrival (after 9:00 AM)
                    if check_in and check_in != 'N/A':
                        try:
                            check_in_time = datetime.strptime(check_in, "%H:%M").time()
                            if check_in_time > datetime.strptime("09:00", "%H:%M").time():
                                late_arrivals += 1
                        except:
                            pass
                
                avg_hours = total_hours / hours_count if hours_count > 0 else 0
                
                summary_data.append({
                    'employee': employee_name,
                    'present': present_days,
                    'absent': absent_days,
                    'avg_hours': avg_hours,
                    'late': late_arrivals
                })
            
            # Create table
            table_data = [['#', 'Employee', 'Present Days', 'Absent Days', 'Avg Hours/Day', 'Late Arrivals']]
            
            for idx, summary in enumerate(summary_data, 1):
                table_data.append([
                    str(idx),
                    summary['employee'],
                    str(summary['present']),
                    str(summary['absent']),
                    f"{summary['avg_hours']:.2f}h",
                    str(summary['late'])
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
            
            # Highlight high late arrivals
            for idx, summary in enumerate(summary_data):
                if summary['late'] > 3:  # More than 3 late arrivals
                    table_style.append(
                        ('BACKGROUND', (-1, idx + 1), (-1, idx + 1), self.late_color)
                    )
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Overall summary
            story.append(Spacer(1, 0.3*inch))
            
            total_employees = len(summary_data)
            total_present = sum(s['present'] for s in summary_data)
            total_absent = sum(s['absent'] for s in summary_data)
            total_late = sum(s['late'] for s in summary_data)
            overall_avg_hours = sum(s['avg_hours'] for s in summary_data) / total_employees if total_employees > 0 else 0
            
            summary_text = f"""
            <b>Overall Statistics:</b><br/>
            • Total Employees: {total_employees}<br/>
            • Total Present Days: {total_present}<br/>
            • Total Absent Days: {total_absent}<br/>
            • Average Hours/Day (All): {overall_avg_hours:.2f}h<br/>
            • Total Late Arrivals: {total_late}
            """
            
            summary_para = Paragraph(summary_text, self.normal_style)
            story.append(summary_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating combined users summary: {e}")
            return None
            """
            Generate individual user attendance PDF report
            
            Args:
                user_name: User's full name
                user_dept: User's department
                attendance_data: DataFrame with user's attendance records
            
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
            title = "Individual Attendance Report"
            subtitle = f"<b>Employee:</b> {user_name}<br/><b>Department:</b> {user_dept}"
            
            story.extend(self._create_header(title, subtitle))
            
            # Create table
            table_data = [['#', 'Date', 'Time', 'Status', 'Late']]
            
            for idx, row in attendance_data.iterrows():
                time_str = row['time'].strftime("%H:%M:%S") if hasattr(row['time'], 'strftime') else str(row['time'])
                late_indicator = "⚠️" if row.get('is_late', False) else "✓"
                
                table_data.append([
                    str(idx + 1),
                    str(row['date']),
                    time_str,
                    str(row['status']),
                    late_indicator
                ])
            
            # Create table
            table = Table(
                table_data,
                colWidths=[0.5*inch, 1.5*inch, 1.2*inch, 1*inch, 0.6*inch]
            )
            
            # Table styling
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
            
            # Highlight late arrivals
            for idx, row in attendance_data.iterrows():
                if row.get('is_late', False):
                    table_style.append(
                        ('BACKGROUND', (-1, idx + 1), (-1, idx + 1), self.late_color)
                    )
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
            
            # Statistics
            story.append(Spacer(1, 0.3*inch))
            
            total_records = len(attendance_data)
            late_count = attendance_data['is_late'].sum() if 'is_late' in attendance_data else 0
            on_time_count = total_records - late_count
            
            stats_text = f"""
            <b>Performance Summary:</b><br/>
            • Total Records: {total_records}<br/>
            • Late Arrivals: {late_count}<br/>
            • On-Time: {on_time_count}<br/>
            • Punctuality Rate: {(on_time_count/total_records*100):.1f}%
            """
            
            stats_para = Paragraph(stats_text, self.normal_style)
            story.append(stats_para)
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error generating user report: {e}")
            return None

