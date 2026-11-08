from dataclasses import dataclass
from typing import Optional

@dataclass
class Recommendation:
    id: Optional[int] = None
    inspection_id: int = 0
    priority: str = "Orta"  # Kritik, Yüksek, Orta, Düşük
    category: str = "Yangın" # Yangın, Güvenlik, Elektrik, Doğal Afet, İdari
    finding: str = ""       # Tespit edilen eksiklik/risk
    action_required: str = "" # Yapılması gereken önlem/aksiyon
    target_deadline_days: int = 30
    status: str = "Açık"    # Açık, Müşteri Bilgilendirildi, Uygulandı, İptal
    created_at: str = ""
