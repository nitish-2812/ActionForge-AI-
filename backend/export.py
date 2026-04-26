"""
export.py — Export action plans to PDF and CSV formats.
Handles formatting and file generation for ActionForge AI results.
"""

import csv
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_csv_export(data: dict, meeting_date: str = None) -> str:
    """
    Generate a CSV export of the action plan.
    
    Args:
        data: The action plan response dict containing tasks, deadlines, assigned, etc.
        meeting_date: Optional meeting date string.
    
    Returns:
        CSV content as string.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["ActionForge AI — Action Plan Export"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    if meeting_date:
        writer.writerow([f"Meeting Date: {meeting_date}"])
    writer.writerow([])
    
    # Summary
    writer.writerow(["MEETING SUMMARY"])
    writer.writerow([data.get("summary", "")])
    writer.writerow([])
    
    # Tasks
    writer.writerow(["ACTION ITEMS"])
    writer.writerow(["#", "Task", "Priority", "Owner"])
    tasks = data.get("tasks", [])
    assigned = data.get("assigned", [])
    for i, task in enumerate(tasks, 1):
        owner = "Team"
        for assign in assigned:
            if assign.get("task") and task.get("task"):
                if assign["task"].lower() in task["task"].lower() or task["task"].lower() in assign["task"].lower():
                    owner = assign["person"]
                    break
        writer.writerow([i, task.get("task", ""), task.get("priority", ""), owner])
    writer.writerow([])
    
    # Deadlines
    writer.writerow(["DEADLINES"])
    writer.writerow(["Item", "Deadline", "Urgency"])
    for deadline in data.get("deadlines", []):
        writer.writerow([
            deadline.get("item", ""),
            deadline.get("deadline", ""),
            deadline.get("urgency", "")
        ])
    writer.writerow([])
    
    # Assignments
    writer.writerow(["ROLE ASSIGNMENTS"])
    writer.writerow(["Person", "Responsibility", "Task"])
    for assignment in data.get("assigned", []):
        writer.writerow([
            assignment.get("person", ""),
            assignment.get("responsibility", ""),
            assignment.get("task", "")
        ])
    writer.writerow([])
    
    # Email
    writer.writerow(["FOLLOW-UP EMAIL"])
    writer.writerow([data.get("email", "")])
    
    return output.getvalue()


def generate_pdf_export(data: dict, meeting_date: str = None) -> bytes:
    """
    Generate a PDF export of the action plan.
    
    Args:
        data: The action plan response dict.
        meeting_date: Optional meeting date string.
    
    Returns:
        PDF content as bytes.
    """
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="ActionForge AI Action Plan"
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#f97316'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#f97316'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("ActionForge AI", title_style))
    story.append(Paragraph("Action Plan Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    meta_text = f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if meeting_date:
        meta_text += f"<br/><b>Meeting Date:</b> {meeting_date}"
    story.append(Paragraph(meta_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary
    story.append(Paragraph("Meeting Summary", heading_style))
    story.append(Paragraph(data.get("summary", ""), normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Tasks Table
    story.append(Paragraph("Action Items", heading_style))
    tasks = data.get("tasks", [])
    assigned = data.get("assigned", [])
    
    task_data = [["#", "Task", "Priority", "Owner"]]
    for i, task in enumerate(tasks, 1):
        owner = "Team"
        for assign in assigned:
            if assign.get("task") and task.get("task"):
                if assign["task"].lower() in task["task"].lower() or task["task"].lower() in assign["task"].lower():
                    owner = assign["person"]
                    break
        task_data.append([
            str(i),
            task.get("task", ""),
            task.get("priority", ""),
            owner
        ])
    
    task_table = Table(task_data, colWidths=[0.4*inch, 2.5*inch, 0.8*inch, 1.2*inch])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(task_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Deadlines Table
    story.append(Paragraph("Deadlines", heading_style))
    deadlines = data.get("deadlines", [])
    deadline_data = [["Item", "Deadline", "Urgency"]]
    for deadline in deadlines:
        deadline_data.append([
            deadline.get("item", ""),
            deadline.get("deadline", ""),
            deadline.get("urgency", "")
        ])
    
    deadline_table = Table(deadline_data, colWidths=[2.2*inch, 1.5*inch, 1.2*inch])
    deadline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(deadline_table)
    story.append(PageBreak())
    
    # Assignments
    story.append(Paragraph("Role Assignments", heading_style))
    assigned_list = data.get("assigned", [])
    assignment_data = [["Person", "Responsibility", "Task"]]
    for assignment in assigned_list:
        assignment_data.append([
            assignment.get("person", ""),
            assignment.get("responsibility", ""),
            assignment.get("task", "")
        ])
    
    assignment_table = Table(assignment_data, colWidths=[1.5*inch, 1.8*inch, 1.6*inch])
    assignment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f97316')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))
    story.append(assignment_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Email
    story.append(Paragraph("Follow-up Email", heading_style))
    email_text = data.get("email", "").replace("\n", "<br/>")
    story.append(Paragraph(email_text, normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
