import os
import pytest
from PIL import Image

from src.models.client import Client
from src.models.inspection import Inspection, InspectionPhoto
from src.services.mock_saha360 import MockSaha360Service
from src.services.scoring_engine import RiskScoringEngine
from src.services.ai_advisor import AIAdvisorService
from src.services.pdf_generator import RiskPDFGenerator

def test_full_end_to_end_inspection_flow(temp_repo, tmp_path):
    # 1. Sentetik Müşteri Yükleme
    saha_service = MockSaha360Service(temp_repo)
    saha_service.seed_synthetic_clients()
    clients = saha_service.search_clients("Atlas Kimya")
    assert len(clients) > 0
    client = clients[0]

    # 2. Risk Parametreleri
    fire_measures = {
        "sprinkler_system": False,
        "smoke_heat_detectors": True,
        "hydrant_hose_system": True,
        "extinguishers_present": True,
        "extinguishers_maintained": False,
        "fire_doors_compartmentation": False,
        "fire_training_done": True
    }
    security_measures = {
        "guard_24_7": True,
        "cctv_present": True,
        "cctv_retention_days": 30,
        "burglar_alarm": True,
        "alarm_monitoring_center": True,
        "perimeter_fence_lighting": True
    }
    natural_measures = {
        "lightning_rod_present": True,
        "grounding_report_valid": False,
        "flood_drainage_pumps": True,
        "elevated_pallet_storage": False,
        "roof_maintenance_good": True
    }

    # 3. Skorlama
    score, level, sub_scores = RiskScoringEngine.evaluate_risk(
        fire_measures, security_measures, natural_measures,
        building_construction="Prefabrik Beton",
        occupancy_type="Kimya Deposu"
    )
    assert 50.0 <= score <= 80.0

    # 4. AI Değerlendirmesi
    ai_service = AIAdvisorService()
    summary, recs_text = ai_service.generate_risk_analysis(
        client.company_name, client.sector, client.hazard_class,
        "Prefabrik Beton", score, level,
        fire_measures, security_measures, natural_measures
    )
    assert len(summary) > 50

    # 5. Teftiş Kaydı
    insp = Inspection(
        client_id=client.id,
        inspector_name="Test Risk Mühendisi",
        inspection_date="2026-11-08",
        occupancy_type="Kimya Deposu",
        building_construction="Prefabrik Beton",
        total_area_sqm=6000.0,
        fire_measures=fire_measures,
        security_measures=security_measures,
        natural_hazard_measures=natural_measures,
        calculated_risk_score=score,
        risk_level=level,
        ai_executive_summary=summary,
        ai_recommendations=recs_text,
        status="Teftiş Tamamlandı"
    )
    insp_id = temp_repo.create_inspection(insp)
    assert insp_id > 0

    # 6. Fotoğraf Ekleme
    photo_file = tmp_path / "e2e_photo.jpg"
    Image.new("RGB", (400, 300), color=(100, 150, 200)).save(photo_file)
    photo = InspectionPhoto(
        inspection_id=insp_id,
        file_path=str(photo_file),
        category="Yangın",
        caption="Kimyasal depolama havalandırma ünitesi"
    )
    pid = temp_repo.add_photo(photo)
    assert pid > 0

    # 7. Otomatik Öneri Üretimi ve Kaydı
    recs = RiskScoringEngine.generate_recommendations(
        insp_id, fire_measures, security_measures, natural_measures
    )
    assert len(recs) >= 3
    for r in recs:
        temp_repo.add_recommendation(r)

    saved_recs = temp_repo.get_recommendations_for_inspection(insp_id)
    assert len(saved_recs) == len(recs)

    # 8. Underwriter Notu ve Durum Güncellemesi
    saved_insp = temp_repo.get_inspection_by_id(insp_id)
    saved_insp.uw_notes = "Sprinkler şartı aranmaksızın 50.000 TL muafiyet ve %25 ek primle onaylanabilir."
    saved_insp.status = "UW İncelemesinde"
    temp_repo.update_inspection(saved_insp)

    updated_insp = temp_repo.get_inspection_by_id(insp_id)
    assert updated_insp.status == "UW İncelemesinde"
    assert "50.000 TL muafiyet" in updated_insp.uw_notes

    # 9. PDF Rapor Üretimi
    pdf_path = RiskPDFGenerator.generate_report(client, updated_insp, saved_recs, output_filename="e2e_report.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 2000
