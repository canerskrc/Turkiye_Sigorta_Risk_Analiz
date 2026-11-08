"""
ReportLab tabanlı profesyonel Dijital Risk Analiz ve Teftiş PDF Rapor Üreticisi.
Kurumsal renk paleti, Türkçe karakter desteği, skor kartları, öneri tablosu ve fotoğraf galerisi içerir.
"""
import os
from pathlib import Path
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import REPORTS_DIR
from src.models.client import Client
from src.models.inspection import Inspection, InspectionPhoto
from src.models.recommendation import Recommendation

# Türkçe karakter uyumlu TrueType font kaydı
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"

try:
    arial_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    arial_bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont("TurkishArial", arial_path))
        FONT_NAME = "TurkishArial"
        if os.path.exists(arial_bold_path):
            pdfmetrics.registerFont(TTFont("TurkishArial-Bold", arial_bold_path))
            FONT_NAME_BOLD = "TurkishArial-Bold"
        else:
            FONT_NAME_BOLD = "TurkishArial"
except Exception:
    pass


class NumberedCanvas(canvas.Canvas):
    """Alt bilgiye sayfa numarası ve yasal karar destek uyarısı basar."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_NAME, 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Üst çizgi
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 800, 555, 800)
        self.drawString(40, 805, "DİJİTAL RİSK ANALİZ FORMU — TEFTİŞ VE KARAR DESTEK RAPORU")
        
        # Alt çizgi ve sayfa no
        self.line(40, 45, 555, 45)
        self.drawString(40, 32, "UYARI: Bu rapor Underwriter karar desteği niteliğindedir. Otomatik teminat onayı teşkil etmez.")
        page_str = f"Sayfa {self._pageNumber} / {page_count}"
        self.drawRightString(555, 32, page_str)
        self.restoreState()


class RiskPDFGenerator:
    @classmethod
    def generate_report(
        cls,
        client: Client,
        inspection: Inspection,
        recommendations: List[Recommendation],
        output_filename: Optional[str] = None
    ) -> str:
        """Verilen teftiş ve öneriler için PDF raporu üretir, dosya yolunu döner."""
        if not output_filename:
            output_filename = f"Risk_Raporu_TF_{inspection.id or 0}_{client.synthetic_code}.pdf"
        
        pdf_path = REPORTS_DIR / output_filename
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=50,
            bottomMargin=55
        )

        styles = getSampleStyleSheet()
        
        # Özel Stiller
        title_style = ParagraphStyle(
            'DocTitle',
            fontName=FONT_NAME_BOLD,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0F172A")
        )
        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            fontName=FONT_NAME,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569")
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            fontName=FONT_NAME_BOLD,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=12,
            spaceAfter=6
        )
        normal_style = ParagraphStyle(
            'NormalText',
            fontName=FONT_NAME,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1E293B")
        )
        small_bold = ParagraphStyle(
            'SmallBold',
            fontName=FONT_NAME_BOLD,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A")
        )

        story = []

        # 1. Başlık & Rapor Künyesi
        header_data = [
            [
                Paragraph("<b>DİJİTAL RİSK TEFTİŞ RAPORU</b>", title_style),
                Paragraph(f"<b>Rapor No:</b> TR-RISK-{inspection.id or 101}<br/><b>Tarih:</b> {inspection.inspection_date}<br/><b>Mühendis:</b> {inspection.inspector_name}", subtitle_style)
            ]
        ]
        t_header = Table(header_data, colWidths=[330, 185])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t_header)
        story.append(Spacer(1, 10))

        # 2. Riziko ve Müşteri Özeti Tablosu
        story.append(Paragraph("1. Riziko ve Müşteri Künyesi", section_heading))
        client_table_data = [
            [Paragraph("<b>Müşteri Unvanı:</b>", small_bold), Paragraph(client.company_name, normal_style),
             Paragraph("<b>Sentetik Kod:</b>", small_bold), Paragraph(client.synthetic_code, normal_style)],
            [Paragraph("<b>Faaliyet / Sektör:</b>", small_bold), Paragraph(client.sector, normal_style),
             Paragraph("<b>Tehlike Sınıfı:</b>", small_bold), Paragraph(client.hazard_class, normal_style)],
            [Paragraph("<b>Lokasyon:</b>", small_bold), Paragraph(f"{client.city} / {client.district}", normal_style),
             Paragraph("<b>Sigorta Bedeli:</b>", small_bold), Paragraph(f"{client.insured_value:,.2f} TL", normal_style)],
            [Paragraph("<b>Yapı Tarzı:</b>", small_bold), Paragraph(inspection.building_construction or "-", normal_style),
             Paragraph("<b>Toplam Alan:</b>", small_bold), Paragraph(f"{inspection.total_area_sqm:,.0f} m²", normal_style)],
        ]
        t_client = Table(client_table_data, colWidths=[100, 160, 100, 155])
        t_client.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_client)
        story.append(Spacer(1, 12))

        # 3. Risk Skoru ve Korunum Kartı
        story.append(Paragraph("2. Risk Skoru ve Korunum Değerlendirmesi", section_heading))
        
        # Risk seviyesine göre arka plan rengi
        score_val = inspection.calculated_risk_score
        if score_val >= 80:
            badge_color = colors.HexColor("#DCFCE7")  # Yeşilimsi
            text_color = colors.HexColor("#166534")
        elif score_val >= 60:
            badge_color = colors.HexColor("#FEF9C3")  # Sarımsı
            text_color = colors.HexColor("#854D0E")
        else:
            badge_color = colors.HexColor("#FEE2E2")  # Kırmızımsı
            text_color = colors.HexColor("#991B1B")

        score_text = f"<b>GENEL KORUNUM SKORU: {score_val} / 100</b><br/>Durum: {inspection.risk_level}"
        score_box_style = ParagraphStyle(
            'ScoreBox',
            fontName=FONT_NAME_BOLD,
            fontSize=11,
            leading=15,
            textColor=text_color,
            alignment=1 # Center
        )
        
        score_table_data = [
            [
                Paragraph(score_text, score_box_style),
                Paragraph(f"<b>Teftiş Durumu:</b> {inspection.status}<br/><b>Underwriter Karar Notu:</b> {inspection.uw_notes or 'İnceleme bekliyor'}", normal_style)
            ]
        ]
        t_score = Table(score_table_data, colWidths=[240, 275])
        t_score.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), badge_color),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_score)
        story.append(Spacer(1, 12))

        # 4. AI Değerlendirme & Yönetici Özeti
        story.append(Paragraph("3. AI Destekli Risk Analisti Yönetici Özeti", section_heading))
        ai_summary_text = inspection.ai_executive_summary or "AI risk analizi teftiş esnasında henüz tetiklenmemiştir."
        t_ai = Table([[Paragraph(ai_summary_text.replace('\n', '<br/>'), normal_style)]], colWidths=[515])
        t_ai.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_ai)
        story.append(Spacer(1, 14))

        # 5. Öncelikli İyileştirme Önerileri (Recommendations Table)
        story.append(Paragraph("4. Tespit Edilen Riskler ve Önlem Aksiyonları (UW / Satış Takip)", section_heading))
        
        rec_rows = [
            [
                Paragraph("<b>Öncelik</b>", small_bold),
                Paragraph("<b>Kategori</b>", small_bold),
                Paragraph("<b>Tespit / Bulgu</b>", small_bold),
                Paragraph("<b>Gereken Önlem / Aksiyon</b>", small_bold),
                Paragraph("<b>Hedef</b>", small_bold),
                Paragraph("<b>Durum</b>", small_bold)
            ]
        ]
        
        if recommendations:
            for r in recommendations:
                p_color = "#DC2626" if r.priority in ["Kritik", "Yüksek"] else "#475569"
                rec_rows.append([
                    Paragraph(f"<font color='{p_color}'><b>{r.priority}</b></font>", normal_style),
                    Paragraph(r.category, normal_style),
                    Paragraph(r.finding, normal_style),
                    Paragraph(r.action_required, normal_style),
                    Paragraph(f"{r.target_deadline_days} gün", normal_style),
                    Paragraph(r.status, normal_style)
                ])
        else:
            rec_rows.append([
                Paragraph("-", normal_style),
                Paragraph("-", normal_style),
                Paragraph("Kritik eksiklik tespit edilmemiştir.", normal_style),
                Paragraph("Mevcut korunum önlemleri sürdürülmelidir.", normal_style),
                Paragraph("-", normal_style),
                Paragraph("Tamam", normal_style)
            ])

        t_recs = Table(rec_rows, colWidths=[55, 65, 145, 160, 45, 45])
        t_recs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_recs)
        story.append(Spacer(1, 14))

        # 6. Saha Fotoğrafları Galerisi (Varsa)
        if inspection.photos:
            story.append(Paragraph("5. Saha Teftiş Fotoğrafları ve Kanıtlar", section_heading))
            photo_grid = []
            row = []
            for photo in inspection.photos:
                if os.path.exists(photo.file_path):
                    try:
                        img = RLImage(photo.file_path, width=240, height=160)
                        caption = Paragraph(f"<b>[{photo.category}]</b> {photo.caption or 'Fotoğraf'}", normal_style)
                        row.append([img, caption])
                        if len(row) == 2:
                            # 2'li satır oluştur
                            cell1 = Table([[row[0][0]], [row[0][1]]], colWidths=[245])
                            cell2 = Table([[row[1][0]], [row[1][1]]], colWidths=[245])
                            photo_grid.append([cell1, cell2])
                            row = []
                    except Exception:
                        pass
            if row: # Tek kalan fotoğraf
                cell1 = Table([[row[0][0]], [row[0][1]]], colWidths=[245])
                photo_grid.append([cell1, ""])

            if photo_grid:
                t_photos = Table(photo_grid, colWidths=[255, 255])
                t_photos.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(KeepTogether(t_photos))

        doc.build(story, canvasmaker=NumberedCanvas)
        return str(pdf_path)
