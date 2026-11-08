import pytest
from src.services.mock_saha360 import MockSaha360Service

def test_mock_saha360_seed_and_search(temp_repo):
    service = MockSaha360Service(temp_repo)
    count = service.seed_synthetic_clients()
    assert count >= 5
    
    # Tüm liste
    all_clients = service.search_clients()
    assert len(all_clients) == count
    
    # Filtreli arama (şehir)
    kocaeli_clients = service.search_clients("Kocaeli")
    assert len(kocaeli_clients) >= 1
    assert any("Atlas Kimya" in c.company_name for c in kocaeli_clients)
    
    # Sektör arama
    tekstil = service.search_clients("tekstil")
    assert len(tekstil) >= 1
    assert "Tekstil" in tekstil[0].sector

    # Sentetik kod arama
    code_match = service.search_clients("TR-001")
    assert len(code_match) == 1
