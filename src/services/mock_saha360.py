"""
Sentetik Saha 360 Mock Entegrasyon Servisi.
Dış dünyadaki gerçek sistemlere bağlanmaz, tamamen sentetik ve kurgusal kurumsal müşteri/riziko verisi sağlar.
"""
from typing import List, Dict, Any
from src.models.client import Client
from src.database.repository import RiskRepository

SYNTHETIC_CLIENTS_DATA = [
    {
        "synthetic_code": "SAHA360-TR-001",
        "company_name": "Atlas Kimya ve Boya Sanayi A.Ş.",
        "sector": "Kimya / Tehlikeli Madde",
        "city": "Kocaeli",
        "district": "Gebze Organize Sanayi Bölgesi",
        "address": "GOSB İhsan Dede Cad. No: 12",
        "insured_value": 85000000.0,
        "hazard_class": "Yüksek"
    },
    {
        "synthetic_code": "SAHA360-TR-002",
        "company_name": "Marmara Lojistik ve Antrepo Hizmetleri Ltd.",
        "sector": "Depolama ve Lojistik",
        "city": "İstanbul",
        "district": "Tuzla",
        "address": "Tepeören Mah. Lojistik Parkı C Blok",
        "insured_value": 45000000.0,
        "hazard_class": "Orta"
    },
    {
        "synthetic_code": "SAHA360-TR-003",
        "company_name": "Ege Tekstil ve Konfeksiyon San. Tic. A.Ş.",
        "sector": "Tekstil İmalat",
        "city": "Bursa",
        "district": "Nilüfer OSB",
        "address": "NOSAB 102. Sokak No: 8",
        "insured_value": 62000000.0,
        "hazard_class": "Yüksek"
    },
    {
        "synthetic_code": "SAHA360-TR-004",
        "company_name": "Anadolu Pres ve Otomotiv Yan Sanayi Ltd.",
        "sector": "Metal ve Makine İmalatı",
        "city": "Sakarya",
        "district": "Arifiye 1. OSB",
        "address": "1. OSB 4. Yol No: 15",
        "insured_value": 38000000.0,
        "hazard_class": "Orta"
    },
    {
        "synthetic_code": "SAHA360-TR-005",
        "company_name": "Zirve Gıda Ambalaj ve Plastik Sanayi",
        "sector": "Plastik ve Ambalaj",
        "city": "Manisa",
        "district": "Yunusemre OSB",
        "address": "Manisa OSB 2. Kısım Keçiliköy OSB Mah.",
        "insured_value": 29000000.0,
        "hazard_class": "Yüksek"
    },
    {
        "synthetic_code": "SAHA360-TR-006",
        "company_name": "Modern Teknoloji ve Veri Merkezi A.Ş.",
        "sector": "Bilişim / Veri Merkezi",
        "city": "Ankara",
        "district": "ODTÜ Teknokent",
        "address": "Üniversiteler Mah. Dumlupınar Bulv. No: 280",
        "insured_value": 110000000.0,
        "hazard_class": "Düşük"
    }
]

class MockSaha360Service:
    def __init__(self, repo: RiskRepository):
        self.repo = repo

    def seed_synthetic_clients(self) -> int:
        """Veritabanında sentetik müşteriler yoksa ekler."""
        created_count = 0
        for item in SYNTHETIC_CLIENTS_DATA:
            client = Client(**item)
            self.repo.add_client(client)
            created_count += 1
        return created_count

    def search_clients(self, query: str = "") -> List[Client]:
        """Sentetik müşteri listesinde arama yapar."""
        all_clients = self.repo.get_all_clients()
        if not query:
            return all_clients
        q = query.lower().strip()
        return [
            c for c in all_clients
            if q in c.company_name.lower()
            or q in c.sector.lower()
            or q in c.city.lower()
            or q in c.synthetic_code.lower()
        ]
