import pytest
from src.services.scoring_engine import RiskScoringEngine
from config.settings import RISK_LEVEL_LOW, RISK_LEVEL_HIGH, RISK_LEVEL_MEDIUM

def test_high_protection_facility():
    fire_measures = {
        "sprinkler_system": True,
        "smoke_heat_detectors": True,
        "hydrant_hose_system": True,
        "extinguishers_present": True,
        "extinguishers_maintained": True,
        "fire_doors_compartmentation": True,
        "fire_training_done": True
    }
    security_measures = {
        "guard_24_7": True,
        "cctv_present": True,
        "cctv_retention_days": 45,
        "burglar_alarm": True,
        "alarm_monitoring_center": True,
        "perimeter_fence_lighting": True
    }
    natural_measures = {
        "lightning_rod_present": True,
        "grounding_report_valid": True,
        "flood_drainage_pumps": True,
        "elevated_pallet_storage": True,
        "roof_maintenance_good": True
    }

    score, level, sub_scores = RiskScoringEngine.evaluate_risk(
        fire_measures, security_measures, natural_measures,
        building_construction="Betonarme",
        occupancy_type="Depo"
    )

    assert score >= 85.0
    assert level == RISK_LEVEL_LOW
    assert sub_scores["fire_score"] == 100.0
    assert sub_scores["security_score"] == 100.0
    assert sub_scores["natural_hazard_score"] == 100.0

def test_poor_protection_facility():
    fire_measures = {
        "sprinkler_system": False,
        "smoke_heat_detectors": False,
        "hydrant_hose_system": False,
        "extinguishers_present": True,
        "extinguishers_maintained": False,
        "fire_doors_compartmentation": False,
        "fire_training_done": False
    }
    security_measures = {
        "guard_24_7": False,
        "cctv_present": False,
        "burglar_alarm": False
    }
    natural_measures = {
        "lightning_rod_present": False,
        "grounding_report_valid": False,
        "elevated_pallet_storage": False
    }

    score, level, sub_scores = RiskScoringEngine.evaluate_risk(
        fire_measures, security_measures, natural_measures,
        building_construction="Ahşap / Karma",
        occupancy_type="Kimya Deposu"
    )

    assert score < 50.0
    assert level == RISK_LEVEL_HIGH

def test_recommendation_generation():
    fire_measures = {
        "sprinkler_system": False,
        "smoke_heat_detectors": False,
        "extinguishers_maintained": False
    }
    security_measures = {
        "guard_24_7": False,
        "alarm_monitoring_center": False,
        "cctv_retention_days": 10
    }
    natural_measures = {
        "grounding_report_valid": False,
        "elevated_pallet_storage": False
    }

    recs = RiskScoringEngine.generate_recommendations(
        inspection_id=99,
        fire_measures=fire_measures,
        security_measures=security_measures,
        natural_hazard_measures=natural_measures
    )

    assert len(recs) >= 5
    categories = [r.category for r in recs]
    assert "Yangın" in categories
    assert "Güvenlik" in categories
    assert "Elektrik / Afet" in categories
    
    # Öncelik kontrolleri
    critical_recs = [r for r in recs if r.priority == "Kritik"]
    assert len(critical_recs) >= 1
