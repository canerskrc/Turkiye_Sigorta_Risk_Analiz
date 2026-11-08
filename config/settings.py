import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "generated_reports"
DB_PATH = DATA_DIR / "risk_analysis.db"

# Create directories if not exist
for path in [DATA_DIR, UPLOADS_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# User Roles
ROLE_RISK_ENGINEER = "Risk Mühendisi"
ROLE_UNDERWRITER = "Underwriter (UW)"
ROLE_FIELD_SALES = "Saha Satış Ekibi"
ALL_ROLES = [ROLE_RISK_ENGINEER, ROLE_UNDERWRITER, ROLE_FIELD_SALES]

# Risk Scoring Weights (Toplam 100 Puan)
RISK_WEIGHTS = {
    "fire_safety": 0.40,        # Yangın güvenlik önlemleri ağırlığı
    "physical_security": 0.25,  # Fiziksel güvenlik ve hırsızlık önlemleri
    "construction_quality": 0.20,# Yapısal dayanıklılık ve bina kalitesi
    "natural_hazard": 0.15      # Doğal afet ve çevresel riskler
}

# Risk Seviyeleri ve Sınırları
RISK_LEVEL_LOW = "Düşük Risk (İyi Korunum)"
RISK_LEVEL_MEDIUM = "Orta Risk (Kabul Edilebilir / Gelişime Açık)"
RISK_LEVEL_HIGH = "Yüksek Risk (Ciddi İyileştirme Gerekir)"

# LLM Ayarları
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
