import pytest
from unittest.mock import patch, MagicMock
from src.services.ai_advisor import AIAdvisorService

def test_fallback_generation_when_ollama_offline():
    service = AIAdvisorService(api_url="http://localhost:99999", timeout=1)
    
    summary, recs = service.generate_risk_analysis(
        company_name="Sentetik Sanayi A.Ş.",
        sector="Kimya",
        hazard_class="Yüksek",
        building_construction="Betonarme",
        total_score=54.5,
        risk_level="Yüksek Risk",
        fire_measures={"sprinkler_system": False, "smoke_heat_detectors": False},
        security_measures={"guard_24_7": False, "cctv_retention_days": 10},
        natural_hazard_measures={"grounding_report_valid": False}
    )

    assert "Sentetik Sanayi A.Ş." in summary
    assert "nihai sigorta kabul veya ret kararı teşkil etmez" in summary
    assert "Yangın Güvenliği" in recs
    assert "Hırsızlık" in recs

def test_llm_parsing_when_ollama_succeeds():
    service = AIAdvisorService()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "[YÖNETİCİ ÖZETİ]\nTesis yangın yükü yüksektir ancak tedbirler orta düzeydedir.\n\n[ÖNERİ VE AKSİYONLAR]\n1. Sprinkler kurunuz.\n2. Dedektörleri artırınız."
    }

    with patch.object(service, "is_ollama_available", return_value=True):
        with patch("requests.post", return_value=mock_response):
            summary, recs = service.generate_risk_analysis(
                company_name="Test Firma",
                sector="Lojistik",
                hazard_class="Orta",
                building_construction="Çelik",
                total_score=75.0,
                risk_level="Orta Risk",
                fire_measures={},
                security_measures={},
                natural_hazard_measures={}
            )

            assert "yangın yükü yüksektir" in summary
            assert "Sprinkler kurunuz" in recs
