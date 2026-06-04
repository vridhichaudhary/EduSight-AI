"""
EduSight AI — PDF Report Generator

Generates professional performance reports using ReportLab.

Report Structure:
    Page 1: Cover page with student info and overall score
    Page 2: Performance statistics and subject scores
    Page 3: AI analysis (patterns, predictions, weak areas)
    Page 4: Study recommendations

Usage:
    from apps.analysis.pdf_generator import generate_student_report
    pdf_bytes = generate_student_report(student_id=1)
    # Returns bytes object ready for HTTP response
"""

import io
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger('apps.analysis')


# ── Colors (RGB 0-1 scale) ──
class Colors:
    BLACK       = (0.04, 0.04, 0.04)      # #0a0a0a
    WHITE       = (0.96, 0.96, 0.96)      # #f5f5f5
    ACCENT      = (0.31, 0.27, 0.90)      # #4f46e5
    SURFACE     = (0.07, 0.07, 0.07)      # #111111
    BORDER      = (0.12, 0.12, 0.12)      # #1f1f1f
    TEXT_MUTED  = (0.32, 0.32, 0.36)      # #52525b
    TEXT_SEC    = (0.63, 0.63, 0.67)      # #a1a1aa
    SUCCESS     = (0.13, 0.77, 0.37)      # #22c55e
    WARNING     = (0.96, 0.62, 0.04)      # #f59e0b
    DANGER      = (0.94, 0.27, 0.27)      # #ef4444
    LIGHT_BG    = (0.98, 0.98, 0.99)      # near white for PDF


def _get_grade_color(percentage: float) -> tuple:
    """Return color based on percentage score."""
    if percentage >= 80:
        return Colors.SUCCESS
    if percentage >= 60:
        return Colors.WARNING
    return Colors.DANGER


def _wrap_text(text: str, max_chars: int = 90) -> list:
    """Wrap long text into lines."""
    if not text:
        return []
    words = text.split()
    lines = []
    current = ''
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_student_report(student_id: int) -> Optional[bytes]:
    """
    Generate complete PDF performance report for a student.

    Args:
        student_id: ID of the student

    Returns:
        PDF as bytes, or None if generation failed
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm

        # ── Load data ──
        data = _load_report_data(student_id)
        if not data:
            logger.error(f"No data for student {student_id}")
            return None

        # ── Setup PDF ──
        buffer    = io.BytesIO()
        page_w, page_h = A4
        c         = canvas.Canvas(buffer, pagesize=A4)
        margin    = 20 * mm
        content_w = page_w - (2 * margin)

        # ── Draw pages ──
        _draw_cover_page(c, data, page_w, page_h, margin, content_w)
        c.showPage()

        _draw_stats_page(c, data, page_w, page_h, margin, content_w)
        c.showPage()

        if data.get('analysis'):
            _draw_analysis_page(
                c, data, page_w, page_h, margin, content_w
            )
            c.showPage()

        if data.get('recommendations'):
            _draw_recommendations_page(
                c, data, page_w, page_h, margin, content_w
            )
            c.showPage()

        # ── Finalize ──
        c.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(
            f"PDF generated: student {student_id}, "
            f"{len(pdf_bytes)} bytes"
        )
        return pdf_bytes

    except ImportError:
        logger.error("ReportLab not installed. pip install reportlab")
        return None
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return None


def _load_report_data(student_id: int) -> Optional[dict]:
    """Load all data needed for PDF report."""
    try:
        from apps.students.models import (
            Student, Marks, Prediction,
            WeakArea, Recommendation, AnalysisLog
        )
        from django.db.models import Avg, Max, Min, Count

        student = Student.objects.get(pk=student_id)
        marks_qs = Marks.objects.filter(
            student=student
        ).select_related('subject')

        stats = marks_qs.aggregate(
            avg=Avg('percentage'),
            high=Max('percentage'),
            low=Min('percentage'),
            total=Count('id'),
        )

        subject_scores = list(
            marks_qs.values('subject__name')
            .annotate(avg=Avg('percentage'))
            .order_by('-avg')
        )

        predictions = list(
            Prediction.objects.filter(student=student)
            .select_related('subject')
            .values('subject__name', 'predicted_marks', 'confidence_score')
            .order_by('-predicted_marks')
        )

        weak_areas = list(
            WeakArea.objects.filter(student=student)
            .select_related('subject')
            .values('subject__name', 'current_percentage',
                    'severity', 'reason')
            .order_by('priority_rank')[:5]
        )

        recs = list(
            Recommendation.objects.filter(
                student=student, is_active=True
            ).select_related('subject')
            .values('subject__name', 'title',
                    'description', 'study_hours_suggested')[:5]
        )

        # Get latest AI analysis
        latest_log = AnalysisLog.objects.filter(
            student=student,
            agent_name='supervisor',
            status='completed',
        ).order_by('-completed_at').first()

        analysis = {}
        if latest_log and latest_log.output_data:
            od = latest_log.output_data
            analysis = {
                'final_report':      od.get('final_report', ''),
                'pattern_findings':  od.get('pattern_findings', ''),
                'weak_area_insights': od.get('weak_area_insights', ''),
            }

        return {
            'student':        student,
            'stats':          stats,
            'subject_scores': subject_scores,
            'predictions':    predictions,
            'weak_areas':     weak_areas,
            'recommendations': recs,
            'analysis':       analysis,
            'generated_at':   datetime.now().strftime('%B %d, %Y'),
        }

    except Exception as e:
        logger.error(f"Data load failed: {e}")
        return None


def _draw_cover_page(c, data, page_w, page_h, margin, content_w):
    """Draw PDF cover page."""
    student = data['student']
    stats   = data['stats']
    avg     = float(stats.get('avg') or 0)

    # ── Background ──
    c.setFillColorRGB(*Colors.BLACK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Accent bar (top) ──
    c.setFillColorRGB(*Colors.ACCENT)
    c.rect(0, page_h - 8, page_w, 8, fill=1, stroke=0)

    # ── Logo area ──
    c.setFillColorRGB(*Colors.ACCENT)
    c.roundRect(margin, page_h - 60, 36, 36, 6, fill=1, stroke=0)

    c.setFillColorRGB(*Colors.WHITE)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(margin + 11, page_h - 38, 'E')

    # ── Brand name ──
    c.setFont('Helvetica-Bold', 16)
    c.setFillColorRGB(*Colors.WHITE)
    c.drawString(margin + 46, page_h - 38, 'EduSight')
    c.setFillColorRGB(*Colors.ACCENT)
    c.drawString(margin + 108, page_h - 38, 'AI')

    # ── Report title ──
    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 10)
    c.drawString(margin, page_h - 75, 'STUDENT PERFORMANCE REPORT')

    # ── Student name (large) ──
    c.setFillColorRGB(*Colors.WHITE)
    c.setFont('Helvetica-Bold', 32)
    name = student.name
    if len(name) > 24:
        name = name[:22] + '...'
    c.drawString(margin, page_h - 180, name)

    # ── Grade + School ──
    c.setFillColorRGB(*Colors.TEXT_SEC)
    c.setFont('Helvetica', 12)
    info_line = f"Grade {student.grade_level}"
    if getattr(student, 'school', None):
        info_line += f"  ·  {student.school}"
    c.drawString(margin, page_h - 202, info_line)

    # ── Divider ──
    c.setStrokeColorRGB(*Colors.BORDER)
    c.setLineWidth(0.5)
    c.line(margin, page_h - 220, margin + content_w, page_h - 220)

    # ── Big score circle ──
    center_x = page_w / 2
    center_y = page_h / 2 - 20

    c.setFillColorRGB(0.09, 0.09, 0.09)
    c.circle(center_x, center_y, 90, fill=1, stroke=0)

    color = _get_grade_color(avg)
    c.setStrokeColorRGB(*color)
    c.setLineWidth(3)
    c.circle(center_x, center_y, 90, fill=0, stroke=1)

    c.setFillColorRGB(*Colors.WHITE)
    c.setFont('Helvetica-Bold', 48)
    avg_str = f"{avg:.1f}%"
    text_w  = c.stringWidth(avg_str, 'Helvetica-Bold', 48)
    c.drawString(center_x - text_w / 2, center_y - 12, avg_str)

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 11)
    label = 'OVERALL AVERAGE'
    label_w = c.stringWidth(label, 'Helvetica', 11)
    c.drawString(center_x - label_w / 2, center_y - 32, label)

    # ── Stats row ──
    stats_y = center_y - 140
    stat_items = [
        ('Total Exams', str(stats.get('total') or 0)),
        ('Highest',     f"{float(stats.get('high') or 0):.1f}%"),
        ('Lowest',      f"{float(stats.get('low') or 0):.1f}%"),
        ('Subjects',    str(len(data['subject_scores']))),
    ]
    col_w = content_w / 4
    for i, (label, value) in enumerate(stat_items):
        x = margin + (i * col_w) + (col_w / 2)

        c.setFillColorRGB(0.09, 0.09, 0.09)
        c.roundRect(
            margin + i * col_w + 4, stats_y - 28,
            col_w - 8, 52, 6, fill=1, stroke=0
        )

        c.setFillColorRGB(*Colors.WHITE)
        c.setFont('Helvetica-Bold', 16)
        val_w = c.stringWidth(value, 'Helvetica-Bold', 16)
        c.drawString(x - val_w / 2, stats_y + 10, value)

        c.setFillColorRGB(*Colors.TEXT_MUTED)
        c.setFont('Helvetica', 8)
        lab_w = c.stringWidth(label, 'Helvetica', 8)
        c.drawString(x - lab_w / 2, stats_y - 8, label)

    # ── Footer ──
    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 8)
    c.drawString(margin, 28, f'Generated by EduSight AI  ·  {data["generated_at"]}')
    page_w_str = f'Page 1'
    c.drawRightString(margin + content_w, 28, page_w_str)


def _draw_stats_page(c, data, page_w, page_h, margin, content_w):
    """Draw statistics and subject scores page."""
    subject_scores = data['subject_scores']
    predictions    = data['predictions']

    # ── Background ──
    c.setFillColorRGB(*Colors.BLACK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # ── Header bar ──
    c.setFillColorRGB(*Colors.ACCENT)
    c.rect(0, page_h - 8, page_w, 8, fill=1, stroke=0)

    y = page_h - 50

    # ── Page title ──
    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 9)
    c.drawString(margin, y, 'PERFORMANCE BREAKDOWN')
    y -= 8

    c.setStrokeColorRGB(*Colors.BORDER)
    c.setLineWidth(0.5)
    c.line(margin, y, margin + content_w, y)
    y -= 20

    # ── Subject Scores Table ──
    c.setFillColorRGB(*Colors.WHITE)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(margin, y, 'Subject-wise Performance')
    y -= 20

    # Table header
    col_widths = [content_w * 0.4, content_w * 0.2,
                  content_w * 0.2, content_w * 0.2]
    headers    = ['Subject', 'Average Score', 'Grade', 'Status']
    header_y   = y

    c.setFillColorRGB(0.09, 0.09, 0.09)
    c.rect(margin, header_y - 14, content_w, 22, fill=1, stroke=0)

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica-Bold', 8)
    x = margin + 8
    for i, (h, w) in enumerate(zip(headers, col_widths)):
        c.drawString(x, header_y - 4, h.upper())
        x += w

    y = header_y - 14

    # Table rows
    def get_grade(pct):
        if pct >= 90: return 'A'
        if pct >= 80: return 'B'
        if pct >= 70: return 'C'
        if pct >= 60: return 'D'
        return 'F'

    for i, subj in enumerate(subject_scores[:10]):
        avg_pct = float(subj.get('avg') or 0)
        color   = _get_grade_color(avg_pct)
        row_y   = y - (i * 22)

        if i % 2 == 0:
            c.setFillColorRGB(0.07, 0.07, 0.07)
            c.rect(margin, row_y - 14, content_w, 22, fill=1, stroke=0)

        c.setFillColorRGB(*Colors.WHITE)
        c.setFont('Helvetica', 10)
        x = margin + 8
        c.drawString(x, row_y - 4, str(subj.get('subject__name', '')))
        x += col_widths[0]

        c.setFillColorRGB(*color)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(x, row_y - 4, f"{avg_pct:.1f}%")
        x += col_widths[1]

        c.drawString(x, row_y - 4, get_grade(avg_pct))
        x += col_widths[2]

        status = 'Excellent' if avg_pct >= 80 else (
            'Good' if avg_pct >= 70 else (
                'Average' if avg_pct >= 60 else 'Needs Help'
            )
        )
        c.drawString(x, row_y - 4, status)

    y -= (min(len(subject_scores), 10) * 22) + 30

    # ── Predictions section ──
    if predictions and y > 150:
        c.setStrokeColorRGB(*Colors.BORDER)
        c.setLineWidth(0.5)
        c.line(margin, y + 10, margin + content_w, y + 10)

        c.setFillColorRGB(*Colors.WHITE)
        c.setFont('Helvetica-Bold', 13)
        c.drawString(margin, y, 'ML Predictions — Next Exam')
        y -= 20

        for pred in predictions[:6]:
            pred_pct   = float(pred.get('predicted_marks') or 0)
            conf       = float(pred.get('confidence_score') or 0.85)
            pred_color = _get_grade_color(pred_pct)
            subj_name  = pred.get('subject__name', '')

            c.setFillColorRGB(*Colors.TEXT_SEC)
            c.setFont('Helvetica', 10)
            c.drawString(margin + 8, y, subj_name)

            c.setFillColorRGB(*pred_color)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(
                margin + 200, y,
                f"{pred_pct:.1f}% (conf: {round(conf*100)}%)"
            )

            risk_label = 'AT RISK' if pred_pct < 60 else 'ON TRACK'
            risk_color = Colors.DANGER if pred_pct < 60 else Colors.SUCCESS
            c.setFillColorRGB(*risk_color)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(margin + 350, y, risk_label)

            y -= 18
            if y < 50:
                break

    # ── Footer ──
    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 8)
    c.drawString(
        margin, 28,
        f'EduSight AI  ·  {data["generated_at"]}'
    )
    c.drawRightString(margin + content_w, 28, 'Page 2')


def _draw_analysis_page(c, data, page_w, page_h, margin, content_w):
    """Draw AI analysis page."""
    analysis = data.get('analysis', {})
    weak     = data.get('weak_areas', [])

    c.setFillColorRGB(*Colors.BLACK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColorRGB(*Colors.ACCENT)
    c.rect(0, page_h - 8, page_w, 8, fill=1, stroke=0)

    y = page_h - 50

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 9)
    c.drawString(margin, y, 'AI ANALYSIS')
    y -= 8

    c.setStrokeColorRGB(*Colors.BORDER)
    c.setLineWidth(0.5)
    c.line(margin, y, margin + content_w, y)
    y -= 20

    def draw_section(title, text, accent_color=None):
        nonlocal y
        if not text or y < 80:
            return

        # Section title
        c.setFillColorRGB(*(accent_color or Colors.ACCENT))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(margin, y, title)
        y -= 4

        c.setStrokeColorRGB(*(accent_color or Colors.ACCENT))
        c.setLineWidth(1)
        c.line(margin, y, margin + 60, y)
        y -= 14

        # Text
        c.setFillColorRGB(*Colors.TEXT_SEC)
        c.setFont('Helvetica', 9)
        lines = _wrap_text(text, max_chars=105)
        for line in lines[:12]:
            if y < 60:
                break
            c.drawString(margin + 4, y, line)
            y -= 13
        y -= 10

    # Final Report
    final = analysis.get('final_report', '')
    if final:
        draw_section('Performance Report', final, Colors.ACCENT)

    # Pattern Findings
    patterns = analysis.get('pattern_findings', '')
    if patterns and y > 120:
        draw_section('Pattern Analysis', patterns, Colors.SUCCESS)

    # Weak Areas
    if weak and y > 120:
        c.setFillColorRGB(*Colors.DANGER)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(margin, y, 'Identified Weak Areas')
        y -= 18

        for w in weak[:4]:
            if y < 60:
                break
            pct      = float(w.get('current_percentage') or 0)
            severity = w.get('severity', 'moderate')
            color    = _get_grade_color(pct)

            c.setFillColorRGB(*color)
            c.circle(margin + 6, y + 3, 4, fill=1, stroke=0)

            c.setFillColorRGB(*Colors.WHITE)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(
                margin + 16, y,
                f"{w.get('subject__name', '')}  —  {pct:.1f}%"
            )

            c.setFillColorRGB(*Colors.TEXT_MUTED)
            c.setFont('Helvetica', 8)
            c.drawString(margin + 200, y, f"({severity})")

            y -= 18

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 8)
    c.drawString(margin, 28, f'EduSight AI  ·  {data["generated_at"]}')
    c.drawRightString(margin + content_w, 28, 'Page 3')


def _draw_recommendations_page(
    c, data, page_w, page_h, margin, content_w
):
    """Draw study recommendations page."""
    recs = data.get('recommendations', [])

    c.setFillColorRGB(*Colors.BLACK)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColorRGB(*Colors.ACCENT)
    c.rect(0, page_h - 8, page_w, 8, fill=1, stroke=0)

    y = page_h - 50

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 9)
    c.drawString(margin, y, 'STUDY RECOMMENDATIONS')
    y -= 8

    c.setStrokeColorRGB(*Colors.BORDER)
    c.setLineWidth(0.5)
    c.line(margin, y, margin + content_w, y)
    y -= 20

    if not recs:
        c.setFillColorRGB(*Colors.TEXT_MUTED)
        c.setFont('Helvetica', 11)
        c.drawString(
            margin, y,
            'Run AI analysis to generate personalized recommendations.'
        )
    else:
        for i, rec in enumerate(recs[:5]):
            if y < 80:
                break

            # Rec card background
            card_h = 75
            c.setFillColorRGB(0.09, 0.09, 0.09)
            c.roundRect(
                margin, y - card_h + 12,
                content_w, card_h,
                6, fill=1, stroke=0
            )

            # Subject badge
            c.setFillColorRGB(*Colors.ACCENT)
            c.roundRect(
                margin + 8, y - 4,
                60, 16,
                3, fill=1, stroke=0
            )
            c.setFillColorRGB(*Colors.WHITE)
            c.setFont('Helvetica-Bold', 8)
            subj = str(rec.get('subject__name', ''))[:10]
            c.drawString(margin + 12, y + 1, subj)

            # Title
            c.setFillColorRGB(*Colors.WHITE)
            c.setFont('Helvetica-Bold', 11)
            title = str(rec.get('title', ''))[:70]
            c.drawString(margin + 8, y - 18, title)

            # Description
            c.setFillColorRGB(*Colors.TEXT_SEC)
            c.setFont('Helvetica', 9)
            desc  = str(rec.get('description', ''))
            lines = _wrap_text(desc, max_chars=100)
            for j, line in enumerate(lines[:2]):
                c.drawString(margin + 8, y - 30 - (j * 12), line)

            # Hours badge
            hours = rec.get('study_hours_suggested', 3)
            c.setFillColorRGB(*Colors.TEXT_MUTED)
            c.setFont('Helvetica', 8)
            c.drawString(
                margin + 8, y - 54,
                f'{hours} hours/week recommended'
            )

            y -= card_h + 12

    c.setFillColorRGB(*Colors.TEXT_MUTED)
    c.setFont('Helvetica', 8)
    c.drawString(margin, 28, f'EduSight AI  ·  {data["generated_at"]}')
    c.drawRightString(margin + content_w, 28, 'Page 4')
