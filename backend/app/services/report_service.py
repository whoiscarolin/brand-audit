"""
app/services/report_service.py
Генерация PDF-отчёта по бренду через reportlab.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.review import Review

# ---------------------------------------------------------------------------
# Цвета
# ---------------------------------------------------------------------------
COLOR_PRIMARY   = colors.HexColor("#6C63FF")
COLOR_POSITIVE  = colors.HexColor("#00C9A7")
COLOR_NEGATIVE  = colors.HexColor("#FF6B6B")
COLOR_NEUTRAL   = colors.HexColor("#F5C542")
COLOR_BG_HEADER = colors.HexColor("#F4F4FB")
COLOR_MUTED     = colors.HexColor("#6B6B80")
COLOR_DARK      = colors.HexColor("#1E1E24")

# ---------------------------------------------------------------------------
# Шрифты — DejaVu с поддержкой кириллицы
# ---------------------------------------------------------------------------
import os as _os

_BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont("DejaVu",     _os.path.join(_BASE_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", _os.path.join(_BASE_DIR, "DejaVuSans-Bold.ttf")))

FONT_REGULAR = "DejaVu"
FONT_BOLD    = "DejaVu-Bold"


def _styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "ReportTitle",
        fontName=FONT_BOLD,
        fontSize=22,
        textColor=COLOR_PRIMARY,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    subtitle = ParagraphStyle(
        "ReportSubtitle",
        fontName=FONT_REGULAR,
        fontSize=11,
        textColor=COLOR_MUTED,
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    section = ParagraphStyle(
        "SectionHeader",
        fontName=FONT_BOLD,
        fontSize=13,
        textColor=COLOR_DARK,
        spaceBefore=14,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyText",
        fontName=FONT_REGULAR,
        fontSize=10,
        textColor=COLOR_DARK,
        spaceAfter=4,
        leading=14,
    )
    cell = ParagraphStyle(
        "CellText",
        fontName=FONT_REGULAR,
        fontSize=9,
        textColor=COLOR_DARK,
        leading=12,
    )
    return title, subtitle, section, body, cell


# ---------------------------------------------------------------------------
# Основная функция генерации
# ---------------------------------------------------------------------------
def generate_pdf(
    brand: "Brand",
    reviews: list["Review"],
    summary: dict,
) -> bytes:
    """
    Генерирует PDF-отчёт и возвращает байты.

    Args:
        brand:   объект Brand из БД
        reviews: список Review объектов
        summary: словарь из get_sentiment_summary()

    Returns:
        bytes — готовый PDF
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Brand Audit — {brand.name}",
        author="Brand Audit Service",
    )

    title_style, subtitle_style, section_style, body_style, cell_style = _styles()
    story = []

    # ------------------------------------------------------------------
    # 1. Шапка
    # ------------------------------------------------------------------
    story.append(Paragraph(f"Brand Audit Report", title_style))
    story.append(Paragraph(brand.name, ParagraphStyle(
        "BrandName", fontName=FONT_BOLD, fontSize=16,
        textColor=COLOR_DARK, spaceAfter=2,
    )))

    meta_parts = []
    if brand.city:
        meta_parts.append(brand.city)
    if brand.category:
        meta_parts.append(brand.category)
    meta_parts.append(f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y')}")
    story.append(Paragraph("  •  ".join(meta_parts), subtitle_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY))
    story.append(Spacer(1, 0.4 * cm))

    # ------------------------------------------------------------------
    # 2. Сводка
    # ------------------------------------------------------------------
    story.append(Paragraph("Сводка", section_style))

    rated = [r.rating for r in reviews if r.rating is not None]
    avg_rating = round(sum(rated) / len(rated), 2) if rated else None
    dates = [r.reviewed_at for r in reviews if r.reviewed_at is not None]
    last_date = max(dates).strftime("%d.%m.%Y") if dates else "—"

    summary_data = [
        ["Показатель", "Значение"],
        ["Всего отзывов",         str(len(reviews))],
        ["Средний рейтинг",       str(avg_rating) if avg_rating else "—"],
        ["Дата последнего отзыва", last_date],
        ["Отзывов проанализировано", str(summary.get("total_analyzed", 0))],
    ]

    summary_table = Table(summary_data, colWidths=[9 * cm, 7 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  COLOR_BG_HEADER),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  COLOR_PRIMARY),
        ("FONTNAME",    (0, 0), (-1, 0),  FONT_BOLD),
        ("FONTSIZE",    (0, 0), (-1, 0),  10),
        ("FONTNAME",    (0, 1), (-1, -1), FONT_REGULAR),
        ("FONTSIZE",    (0, 1), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_HEADER]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0EE")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.4 * cm))

    # ------------------------------------------------------------------
    # 3. Тональность
    # ------------------------------------------------------------------
    if summary.get("total_analyzed", 0) > 0:
        story.append(Paragraph("Анализ тональности", section_style))

        sentiment_data = [
            ["Тональность", "Количество", "Доля"],
            ["😊 Позитивные", str(summary["positive_count"]), f"{summary['positive_pct']}%"],
            ["😞 Негативные", str(summary["negative_count"]), f"{summary['negative_pct']}%"],
            ["😐 Нейтральные", str(summary["neutral_count"]),  f"{summary['neutral_pct']}%"],
        ]

        sent_table = Table(sentiment_data, colWidths=[7 * cm, 4.5 * cm, 4.5 * cm])
        sent_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  COLOR_BG_HEADER),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  COLOR_PRIMARY),
            ("FONTNAME",    (0, 0), (-1, 0),  FONT_BOLD),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("FONTNAME",    (0, 1), (-1, -1), FONT_REGULAR),
            ("TEXTCOLOR",   (0, 1), (0, 1),   COLOR_POSITIVE),
            ("TEXTCOLOR",   (0, 2), (0, 2),   COLOR_NEGATIVE),
            ("TEXTCOLOR",   (0, 3), (0, 3),   COLOR_NEUTRAL),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_HEADER]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0EE")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(sent_table)
        story.append(Spacer(1, 0.4 * cm))

    # ------------------------------------------------------------------
    # 4. Таблица отзывов
    # ------------------------------------------------------------------
    story.append(Paragraph("Отзывы", section_style))

    SENTIMENT_LABELS = {
        "positive": "Позитив",
        "negative": "Негатив",
        "neutral":  "Нейтрал",
    }

    review_data = [["Автор", "Рейтинг", "Тональность", "Текст"]]
    for r in reviews:
        text_preview = (r.text or "")[:200]
        if len(r.text or "") > 200:
            text_preview += "..."

        sentiment = SENTIMENT_LABELS.get(r.sentiment_label or "", "—")
        review_data.append([
            Paragraph(r.author or "—", cell_style),
            str(r.rating) if r.rating else "—",
            sentiment,
            Paragraph(text_preview, cell_style),
        ])

    review_table = Table(
        review_data,
        colWidths=[3 * cm, 2 * cm, 2.5 * cm, 8.5 * cm],
    )
    review_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  COLOR_BG_HEADER),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  COLOR_PRIMARY),
        ("FONTNAME",    (0, 0), (-1, 0),  FONT_BOLD),
        ("FONTSIZE",    (0, 0), (-1, 0),  10),
        ("FONTNAME",    (0, 1), (-1, -1), FONT_REGULAR),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG_HEADER]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0EE")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("ALIGN",       (1, 0), (2, -1),  "CENTER"),
    ]))
    story.append(review_table)
    story.append(Spacer(1, 0.6 * cm))

    # ------------------------------------------------------------------
    # 5. Футер
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_MUTED))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Сгенерировано сервисом Brand Audit • {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ParagraphStyle("Footer", fontName=FONT_REGULAR, fontSize=8,
                       textColor=COLOR_MUTED, alignment=TA_CENTER),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
