from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, timedelta
import io

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E3192'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
    
    def calculate_hours(self, check_in, check_out):
        """Calculate working hours between check-in and check-out"""
        if not check_in or not check_out:
            return "N/A"
        try:
            fmt = "%Y-%m-%d %H:%M:%S"
            td = datetime.strptime(check_out, fmt) - datetime.strptime(check_in, fmt)
            hours = td.total_seconds() / 3600
            return f"{hours:.2f}h"
        except:
            return "N/A"
    
    def generate_daily_report(self, records, date):
        """Generate daily attendance report PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Title
        title = Paragraph(f"Daily Attendance Report", self.title_style)
        story.append(title)
        
        # Date info
        date_text = Paragraph(f"<b>Date:</b> {date}", self.styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 0.2*inch))
        
        # Table data
        data = [['#', 'Name', 'Department', 'Time', 'Status']]
        
        for idx, record in enumerate(records, 1):
            data.append([
                str(idx),
                record[1],  # name
                record[2],  # department
                record[3].split()[1] if len(record[3].split()) > 1 else record[3],  # time only
                record[4]   # status
            ])
        
        # Create table
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.5*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Total Records: {len(records)}</i>",
            self.styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_range_report(self, summary_records, start_date, end_date):
        """Generate date range attendance report with working hours"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Title
        title = Paragraph(f"Attendance Report", self.title_style)
        story.append(title)
        
        # Date range
        date_text = Paragraph(
            f"<b>Period:</b> {start_date} to {end_date}",
            self.styles['Normal']
        )
        story.append(date_text)
        story.append(Spacer(1, 0.2*inch))
        
        # Table data
        data = [['#', 'Name', 'Department', 'Date', 'Check In', 'Check Out', 'Hours']]
        
        for idx, record in enumerate(summary_records, 1):
            hours = self.calculate_hours(record[4], record[5])
            data.append([
                str(idx),
                record[1],  # name
                record[2],  # department
                record[3],  # date
                record[4].split()[1] if record[4] and len(record[4].split()) > 1 else 'N/A',
                record[5].split()[1] if record[5] and len(record[5].split()) > 1 else 'N/A',
                hours
            ])
        
        # Create table
        table = Table(data, colWidths=[0.4*inch, 1.5*inch, 1.2*inch, 1*inch, 0.9*inch, 0.9*inch, 0.7*inch])
        table.setStyle(TableStyle([
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
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        total_days = len(set([r[3] for r in summary_records]))
        summary_text = Paragraph(
            f"<b>Summary:</b> {len(summary_records)} records | {total_days} working days",
            self.styles['Normal']
        )
        story.append(summary_text)
        
        # Footer
        footer = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            self.styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_user_report(self, user_name, user_dept, attendance_records):
        """Generate individual user attendance report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Title
        title = Paragraph(f"Individual Attendance Report", self.title_style)
        story.append(title)
        
        # User info
        user_info = Paragraph(
            f"<b>Employee:</b> {user_name}<br/><b>Department:</b> {user_dept}",
            self.styles['Normal']
        )
        story.append(user_info)
        story.append(Spacer(1, 0.2*inch))
        
        # Table data
        data = [['#', 'Date', 'Time', 'Status']]
        
        for idx, record in enumerate(attendance_records, 1):
            timestamp = record[1]
            date_part = timestamp.split()[0] if len(timestamp.split()) > 0 else timestamp
            time_part = timestamp.split()[1] if len(timestamp.split()) > 1 else ''
            
            data.append([
                str(idx),
                date_part,
                time_part,
                record[2]  # status
            ])
        
        # Create table
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E3192')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Total Records: {len(attendance_records)}</i>",
            self.styles['Normal']
        )
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer