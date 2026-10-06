from io import BytesIO
import os
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

try:  # Persian/Arabic letter joining + bidi ordering (reportlab does neither on its own)
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:  # pragma: no cover - dependency listed in requirements/base.txt
    arabic_reshaper = None
    get_display = None

_STATIC_FONTS = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'fonts')
# First existing pair wins. Vazirmatn/Noto may be dropped into backend/static/fonts; DejaVu ships with the Docker image.
FONT_CANDIDATES = [
    (os.path.join(_STATIC_FONTS, 'Vazirmatn-Regular.ttf'), os.path.join(_STATIC_FONTS, 'Vazirmatn-Bold.ttf')),
    (os.path.join(_STATIC_FONTS, 'NotoNaskhArabic-Regular.ttf'), os.path.join(_STATIC_FONTS, 'NotoNaskhArabic-Bold.ttf')),
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf'),
]


def register_persian_fonts():
    if getattr(register_persian_fonts, '_registered', False):
        return
    for regular, bold in FONT_CANDIDATES:
        if os.path.exists(regular):
            try:
                pdfmetrics.registerFont(TTFont('Persian', regular))
                pdfmetrics.registerFont(TTFont('PersianBold', bold if os.path.exists(bold) else regular))
                break
            except Exception:  # corrupt font: try the next candidate
                continue
    register_persian_fonts._registered = True


def get_persian_font():
    register_persian_fonts()
    return 'Persian' if 'Persian' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'


def get_persian_bold():
    register_persian_fonts()
    return 'PersianBold' if 'PersianBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'


def shape(text):
    """Return display-ordered text for reportlab: joined Persian letters, RTL runs reordered."""
    text = '' if text is None else str(text)
    if arabic_reshaper is None or not is_rtl_text(text):
        return text
    return get_display(arabic_reshaper.reshape(text))


def para(text):
    """XML-escape (user content must never be parsed as reportlab markup) and shape."""
    return escape(shape(text))


def is_rtl_text(text):
    if not text:
        return False
    for char in text:
        cp = ord(char)
        if (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F):
            return True
    return False

def _shape_rows(rows):
    return [[shape(cell) for cell in row] for row in rows]


def persian_style(font_size=10, bold=False, alignment=TA_RIGHT, color=black):
    font_name = get_persian_bold() if bold else get_persian_font()
    return ParagraphStyle(
        'PersianStyle',
        fontName=font_name,
        fontSize=font_size,
        leading=font_size * 1.5,
        alignment=alignment,
        textColor=color,
    )

def _draw_header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont(get_persian_bold(), 16)
    canvas_obj.drawRightString(A4[0] - 20 * mm, A4[1] - 20 * mm, shape('پلتفرم مدیریت بازرسی فنی'))
    canvas_obj.setFont(get_persian_font(), 8)
    canvas_obj.drawRightString(A4[0] - 20 * mm, A4[1] - 25 * mm, 'Technical Inspection Management Platform')
    canvas_obj.setStrokeColor(HexColor('#1a73e8'))
    canvas_obj.setLineWidth(2)
    canvas_obj.line(20 * mm, A4[1] - 30 * mm, A4[0] - 20 * mm, A4[1] - 30 * mm)
    canvas_obj.restoreState()

    canvas_obj.saveState()
    canvas_obj.setFont(get_persian_font(), 8)
    canvas_obj.drawString(20 * mm, 15 * mm, shape(f'صفحه {doc.page}'))
    canvas_obj.drawRightString(A4[0] - 20 * mm, 15 * mm, shape('مدیریت بازرسی فنی'))
    canvas_obj.restoreState()

def generate_inspection_report_pdf(report_data):
    register_persian_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=35 * mm,
        bottomMargin=25 * mm,
    )
    story = []

    title_style = persian_style(16, bold=True, alignment=TA_CENTER)
    story.append(Paragraph(para('گزارش بازرسی فنی'), title_style))
    story.append(Spacer(1, 5 * mm))

    header_data = [
        ['شماره گزارش:', report_data.get('report_number', '')],
        ['پروژه:', report_data.get('project_name', '')],
        ['مشتری:', report_data.get('client_name', '')],
        ['تاریخ بازرسی:', report_data.get('inspection_date', '')],
        ['بازرس:', report_data.get('inspector_name', '')],
        ['رشته:', report_data.get('discipline', '')],
        ['نوع بازرسی:', report_data.get('inspection_type', '')],
        ['وضعیت:', report_data.get('status', '')],
    ]

    header_table = Table(_shape_rows(header_data), colWidths=[50 * mm, 100 * mm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), get_persian_bold()),
        ('FONTNAME', (1, 0), (1, -1), get_persian_font()),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f5f5f5')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10 * mm))

    scope_text = report_data.get('scope', '')
    if scope_text:
        story.append(Paragraph(para('محدوده بازرسی:'), persian_style(12, bold=True)))
        story.append(Paragraph(para(scope_text), persian_style(10)))
        story.append(Spacer(1, 5 * mm))

    narrative = report_data.get('narrative', '')
    if narrative:
        story.append(Paragraph(para('روایت بازرسی:'), persian_style(12, bold=True)))
        story.append(Paragraph(para(narrative), persian_style(10)))
        story.append(Spacer(1, 5 * mm))

    findings = report_data.get('findings', [])
    if findings:
        story.append(Paragraph(para('یافته‌ها:'), persian_style(12, bold=True)))
        finding_data = [['ردیف', 'توضیحات', 'وضعیت']]
        for i, finding in enumerate(findings, 1):
            finding_data.append([str(i), finding.get('description', ''), finding.get('status', '')])
        finding_table = Table(_shape_rows(finding_data), colWidths=[15 * mm, 110 * mm, 35 * mm])
        finding_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), get_persian_bold()),
            ('FONTNAME', (0, 1), (-1, -1), get_persian_font()),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(finding_table)

    if report_data.get('content_hash'):
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph(escape('SHA-256: ' + report_data['content_hash']), ParagraphStyle('hash', fontName='Helvetica', fontSize=7, textColor=HexColor('#777777'), alignment=TA_LEFT)))

    doc.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)

    buffer.seek(0)
    return buffer

def generate_financial_statement_pdf(statement_data):
    register_persian_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=35 * mm,
        bottomMargin=25 * mm,
    )
    story = []

    title_style = persian_style(16, bold=True, alignment=TA_CENTER)
    story.append(Paragraph(para('صورت مالی'), title_style))
    story.append(Spacer(1, 5 * mm))

    header_data = [
        ['شماره صورت:', statement_data.get('statement_number', '')],
        ['پروژه:', statement_data.get('project_name', '')],
        ['دوره:', f"{statement_data.get('period_start', '')} تا {statement_data.get('period_end', '')}"],
        ['ارز:', statement_data.get('currency', 'IRR')],
        ['وضعیت:', statement_data.get('status', '')],
    ]

    header_table = Table(_shape_rows(header_data), colWidths=[50 * mm, 100 * mm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), get_persian_bold()),
        ('FONTNAME', (1, 0), (1, -1), get_persian_font()),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f5f5f5')),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10 * mm))

    lines = statement_data.get('lines', [])
    if lines:
        line_data = [['نوع', 'توضیحات', 'مبلغ', 'ارز']]
        for line in lines:
            line_data.append([
                line.get('line_type', ''),
                line.get('description', ''),
                f"{line.get('amount', 0):,.0f}",
                line.get('currency', 'IRR'),
            ])
        line_data.append(['جمع کل', '', f"{statement_data.get('total_billable', 0):,.0f}", statement_data.get('currency', 'IRR')])

        line_table = Table(_shape_rows(line_data), colWidths=[30 * mm, 70 * mm, 35 * mm, 25 * mm])
        line_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), get_persian_bold()),
            ('FONTNAME', (0, 1), (-1, -1), get_persian_font()),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(line_table)

    doc.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)

    buffer.seek(0)
    return buffer
