import pytest
import os
from pathlib import Path
from PIL import Image

from src.models.client import Client
from src.models.inspection import Inspection, InspectionPhoto
from src.models.recommendation import Recommendation
from src.services.pdf_generator import RiskPDFGenerator

def test_pdf_generation_flow(tmp_path):
    # Sentetik Test Müşterisi
    client = Client(
        synthetic_code="SAHA360-TR-TEST",
        company_name="Test Sanayi ve Ticaret A.Ş.",
        sector="Tekstil İmalat",
        city="Bursa",
        district="Nilüfer OSB",
        insured_value=40000000.0,
        hazard_class="Yüksek"
    )

    # Sentetik Test Fotoğrafı Oluştur
    test_img_path = tmp_path / "test_photo.jpg"
    img = Image.new("RGB", (300, 200), color=(73, 109, 137))
    img.save(test_img_path)

    # Teftiş
    inspection = Inspection(
        id=101,
        client_id=1,
        inspector_name="Caner Şekerci (Risk Mühendisi)",
        inspection_date="2026-11-08",
        occupancy_type="İplik & Dokuma Fabrikası",
        building_construction="Prefabrik Beton",
        total_area_sqm=8500.0,
        calculated_risk_score=72.5,
        risk_level="Orta Risk (Kabul Edilebilir / Gelişime Açık)",
        ai_executive_summary="Tesis genel yangın güvenliği orta seviyededir. İplik tozuna karşı emiş sistemi ve yangın kompartmantasyonu güçlendirilmelidir.",
        uw_notes="Otomatik sprinkler montaj şartı ve %10 muafiyet ile kabul edilebilir.",
        status="UW İncelemesinde",
        photos=[
            InspectionPhoto(
                inspection_id=101,
                file_path=str(test_img_path),
                category="Yangın",
                caption="Yangın hidrofor ve pompa istasyonu"
            )
        ]
    )

    recs = [
        Recommendation(
            inspection_id=101,
            priority="Kritik",
            category="Yangın",
            finding="Üretim holünde iplik tozu birikimi mevcut.",
            action_required="Hava kanalları periyodik temizlenmeli, kıvılcım dedektörleri takılmalıdır.",
            target_deadline_days=15,
            status="Açık"
        ),
        Recommendation(
            inspection_id=101,
            priority="Yüksek",
            category="Güvenlik",
            finding="Kamera kayıt süresi 15 gündür.",
            action_required="Kayıt kapasitesi 30 güne yükseltilmelidir.",
            target_deadline_days=30,
            status="Müşteri Bilgilendirildi"
        )
    ]

    pdf_filename = "test_output_report.pdf"
    pdf_path = RiskPDFGenerator.generate_report(client, inspection, recs, output_filename=pdf_filename)

    assert os.path.exists(pdf_path)
    file_size = os.path.getsize(pdf_path)
    assert file_size > 1000  # PDF en az birkaç kilobayt olmalı
