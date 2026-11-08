import pytest
from src.models.client import Client
from src.models.inspection import Inspection, InspectionPhoto
from src.models.recommendation import Recommendation

def test_client_crud(temp_repo):
    client = Client(
        synthetic_code="TEST-001",
        company_name="Test Kimya Ltd.",
        sector="Kimya",
        city="İzmir",
        district="Aliağa",
        address="Sanayi Cad. No: 1",
        insured_value=15000000.0,
        hazard_class="Yüksek"
    )
    client_id = temp_repo.add_client(client)
    assert client_id > 0
    
    fetched = temp_repo.get_client_by_id(client_id)
    assert fetched is not None
    assert fetched.company_name == "Test Kimya Ltd."
    assert fetched.synthetic_code == "TEST-001"

def test_inspection_lifecycle(temp_repo):
    client = Client(
        synthetic_code="TEST-002",
        company_name="Test Depo A.Ş.",
        sector="Lojistik",
        city="Kocaeli",
        district="Gebze",
        insured_value=20000000.0
    )
    cid = temp_repo.add_client(client)
    
    insp = Inspection(
        client_id=cid,
        inspector_name="Ahmet Yılmaz",
        inspection_date="2026-11-08",
        occupancy_type="Depo",
        building_construction="Betonarme",
        total_area_sqm=3500.0,
        fire_measures={"sprinkler": True, "hydrant": True},
        calculated_risk_score=78.5,
        risk_level="Orta Risk",
        status="Taslak"
    )
    insp_id = temp_repo.create_inspection(insp)
    assert insp_id > 0
    
    # Fotoğraf Ekleme
    photo = InspectionPhoto(
        inspection_id=insp_id,
        file_path="/tmp/photo1.jpg",
        category="Yangın",
        caption="Yangın hidrofor odası"
    )
    pid = temp_repo.add_photo(photo)
    assert pid > 0
    
    # Güncelleme
    saved = temp_repo.get_inspection_by_id(insp_id)
    assert saved is not None
    assert len(saved.photos) == 1
    assert saved.fire_measures.get("sprinkler") is True
    
    saved.status = "UW İncelemesinde"
    saved.uw_notes = "Sprinkler test sertifikası talep edildi."
    update_res = temp_repo.update_inspection(saved)
    assert update_res is True
    
    updated = temp_repo.get_inspection_by_id(insp_id)
    assert updated.status == "UW İncelemesinde"
    assert updated.uw_notes == "Sprinkler test sertifikası talep edildi."

def test_recommendation_flow(temp_repo):
    client = Client(synthetic_code="TEST-003", company_name="Test Metal")
    cid = temp_repo.add_client(client)
    insp = Inspection(client_id=cid, inspector_name="Mehmet Risk", inspection_date="2026-11-08")
    iid = temp_repo.create_inspection(insp)
    
    rec = Recommendation(
        inspection_id=iid,
        priority="Kritik",
        category="Yangın",
        finding="Yangın tüpleri son kullanım tarihi geçmiş.",
        action_required="Tüm kuru kimyevi tozlu söndürücüler akredite kurumca yenilenmelidir.",
        target_deadline_days=15,
        status="Açık"
    )
    rid = temp_repo.add_recommendation(rec)
    assert rid > 0
    
    recs = temp_repo.get_recommendations_for_inspection(iid)
    assert len(recs) == 1
    assert recs[0].priority == "Kritik"
    
    # Durum güncelleme (Saha satış / Müşteri takibi)
    temp_repo.update_recommendation_status(rid, "Uygulandı")
    updated_recs = temp_repo.get_recommendations_for_inspection(iid)
    assert updated_recs[0].status == "Uygulandı"
