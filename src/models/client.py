from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Client:
    id: Optional[int] = None
    synthetic_code: str = ""
    company_name: str = ""
    sector: str = ""
    city: str = ""
    district: str = ""
    address: str = ""
    insured_value: float = 0.0
    hazard_class: str = "Orta"  # Düşük, Orta, Yüksek
