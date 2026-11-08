from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json

@dataclass
class InspectionPhoto:
    id: Optional[int] = None
    inspection_id: Optional[int] = None
    file_path: str = ""
    category: str = "Genel"  # Yangın, Güvenlik, Depolama, Elektrik, vb.
    caption: str = ""
    uploaded_at: str = ""

@dataclass
class Inspection:
    id: Optional[int] = None
    client_id: int = 0
    inspector_name: str = ""
    inspection_date: str = ""
    occupancy_type: str = ""           # Üretim, Depo, Ofis, Atölye vb.
    building_construction: str = ""    # Betonarme, Çelik Konstrüksiyon, Yığma
    total_area_sqm: float = 0.0
    number_of_floors: int = 1
    
    # Detaylı önlem parametreleri (JSON olarak saklanır)
    fire_measures: Dict[str, Any] = field(default_factory=dict)
    security_measures: Dict[str, Any] = field(default_factory=dict)
    natural_hazard_measures: Dict[str, Any] = field(default_factory=dict)
    
    # Skor ve AI Değerlendirmesi
    calculated_risk_score: float = 0.0
    risk_level: str = ""
    ai_executive_summary: str = ""
    ai_recommendations: str = ""
    
    # Underwriter & Satış Notları
    uw_notes: str = ""
    status: str = "Taslak"  # Taslak, Teftiş Tamamlandı, UW İncelemesinde, Onaylandı
    created_at: str = ""
    photos: List[InspectionPhoto] = field(default_factory=list)
