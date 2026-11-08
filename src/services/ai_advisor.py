"""
Lokal LLM (Ollama) ve Sigorta Risk Mühendisi Danışman Katmanı.
Ollama REST API ile entegre çalışır. Ollama çevrimdışı olduğunda
akıllı kural tabanlı fallback motoruyla kesintisiz karar destek çıktısı sağlar.

KESİN KURAL: Sistem asla tek başına sigorta kabul/ret kararı vermez.
Yalnızca Underwriter ve Risk Mühendisi için karar destek notları üretir.
"""
import requests
import json
from typing import Dict, Any, Tuple
from config.settings import OLLAMA_API_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """Sen kıdemli bir Endüstriyel Yangın ve Risk Mühendisliği uzmanısın.
Görevlerin:
1. Verilen teftiş verilerine dayanarak Underwriter (UW) için objektif bir "Risk Değerlendirme Yönetici Özeti" hazırlamak.
2. Saha Satış ekibinin müşteriyle paylaşabileceği teknik ama yapıcı "İyileştirme Önerileri" sunmak.

KATI KURALLAR:
- ASLA kesin sigorta kabul, ret veya poliçe onay kararı verme. Nihai karar Underwriter'a aittir.
- Bilgilendirici, analitik, tehlike ve korunum dengesini vurgulayan profesyonel bir dil kullan.
- Türkçe yanıt ver.
"""

class AIAdvisorService:
    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = OLLAMA_MODEL, timeout: int = 4):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_ollama_available(self) -> bool:
        """Lokal Ollama servisinin erişilebilir olup olmadığını kontrol eder."""
        try:
            resp = requests.get(f"{self.api_url}/api/tags", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    def generate_risk_analysis(
        self,
        company_name: str,
        sector: str,
        hazard_class: str,
        building_construction: str,
        total_score: float,
        risk_level: str,
        fire_measures: Dict[str, Any],
        security_measures: Dict[str, Any],
        natural_hazard_measures: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Risk analizi özeti ve iyileştirme tavsiyeleri üretir.
        Dönüş: (ai_executive_summary, ai_recommendations)
        """
        # Prompt oluştur
        user_prompt = f"""
Riziko Bilgileri:
- Müşteri: {company_name}
- Faaliyet / Sektör: {sector}
- Tehlike Sınıfı: {hazard_class}
- Yapı Tarzı: {building_construction}
- Hesaplanmış Güvenlik Skoru: {total_score} / 100 ({risk_level})

Yangın Önlemleri:
- Sprinkler: {'Var' if fire_measures.get('sprinkler_system') else 'YOK'}
- Yangın Algılama & Dedektör: {'Var' if fire_measures.get('smoke_heat_detectors') else 'YOK'}
- Yangın Dolabı / Hidrant: {'Var' if fire_measures.get('hydrant_hose_system') else 'YOK'}
- Yangın Tüpü Bakımı: {'Güncel' if fire_measures.get('extinguishers_maintained') else 'GÜNCEL DEĞİL VEYA EKSİK'}

Fiziksel Güvenlik Önlemleri:
- 7/24 Fiziki Bekçi: {'Var' if security_measures.get('guard_24_7') else 'YOK'}
- CCTV Kamera Sistemi: {'Var' if security_measures.get('cctv_present') else 'YOK'} (Kayıt Saklama: {security_measures.get('cctv_retention_days', 0)} gün)
- Hırsız Alarmı & AHM: {'Var' if security_measures.get('alarm_monitoring_center') else 'YOK / AHM BAĞLANTISIZ'}

Doğal Afet ve Tesisat Önlemleri:
- EMO Topraklama ve Paratoner Raporu: {'Geçerli' if natural_hazard_measures.get('grounding_report_valid') else 'YOK / SÜRESİ DOLMUŞ'}
- Yüksekte Paletli Depolama: {'Uygulanıyor' if natural_hazard_measures.get('elevated_pallet_storage') else 'UYGULANMIYOR'}

Lütfen yukarıdaki verilere göre şu formatta yanıt ver:
[YÖNETİCİ ÖZETİ]
(Buraya Underwriter için risk özeti ve kritik eksiklikler)

[ÖNERİ VE AKSİYONLAR]
(Buraya Saha Satış ve Müşteri için somut tavsiyeler)
"""
        # 1. Ollama dene
        if self.is_ollama_available():
            try:
                payload = {
                    "model": self.model,
                    "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                    "stream": False
                }
                resp = requests.post(f"{self.api_url}/api/generate", json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    text = resp.json().get("response", "")
                    if text:
                        return self._parse_llm_response(text)
            except Exception:
                pass  # Fallback'e düşecek

        # 2. Akıllı Kural Tabanlı Fallback Motoru
        return self._generate_fallback_analysis(
            company_name, sector, hazard_class, total_score, risk_level,
            fire_measures, security_measures, natural_hazard_measures
        )

    def _parse_llm_response(self, text: str) -> Tuple[str, str]:
        """LLM çıktısını yönetici özeti ve öneriler olarak iki bölüme ayırır."""
        summary_part = ""
        recs_part = ""
        if "[ÖNERİ VE AKSİYONLAR]" in text:
            parts = text.split("[ÖNERİ VE AKSİYONLAR]")
            summary_part = parts[0].replace("[YÖNETİCİ ÖZETİ]", "").strip()
            recs_part = parts[1].strip()
        else:
            summary_part = text.strip()
            recs_part = "Belirlenen öncelikli tavsiyeler teknik raporda listelenmiştir."
        return summary_part, recs_part

    def _generate_fallback_analysis(
        self,
        company_name: str,
        sector: str,
        hazard_class: str,
        total_score: float,
        risk_level: str,
        fire_measures: Dict[str, Any],
        security_measures: Dict[str, Any],
        natural_hazard_measures: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Ollama çevrimdışıyken deterministik, yüksek kaliteli uzman risk analizi üretir."""
        
        # Risk Özeti İnşası
        summary_lines = [
            f"{company_name} tesisinde gerçekleştirilen risk teftişinde genel korunum skoru 100 üzerinden {total_score} ({risk_level}) olarak hesaplanmıştır.",
            f"Tesis '{sector}' sektöründe faaliyet göstermekte olup baz tehlike sınıfı '{hazard_class}' düzeyindedir."
        ]
        
        fire_findings = []
        if not fire_measures.get("sprinkler_system"):
            fire_findings.append("otomatik sprinkler sisteminin bulunmaması")
        if not fire_measures.get("smoke_heat_detectors"):
            fire_findings.append("erken algılama dedektör ağının yetersizliği")
        if not fire_measures.get("extinguishers_maintained"):
            fire_findings.append("yangın tüplerinin güncel periyodik bakımının olmaması")

        if fire_findings:
            summary_lines.append(f"Yangın riski açısından en belirgin zafiyetler: {', '.join(fire_findings)} olarak öne çıkmaktadır.")
        else:
            summary_lines.append("Tesisin yangın korunum ve söndürme altyapısı standartlara uygun seviyede korunmaktadır.")

        sec_findings = []
        if not security_measures.get("guard_24_7") and not security_measures.get("alarm_monitoring_center"):
            sec_findings.append("gece saatlerinde aktif izleme veya bekçi korumasının bulunmaması")
        if security_measures.get("cctv_retention_days", 0) < 30:
            sec_findings.append("kamera kayıt süresinin 30 günün altında kalması")

        if sec_findings:
            summary_lines.append(f"Hırsızlık ve fiziksel güvenlik tarafında {', '.join(sec_findings)} risk faktörü oluşturmaktadır.")

        summary_lines.append("Not: Bu değerlendirme Underwriter incelemesi için karar destek amaçlı olup nihai sigorta kabul veya ret kararı teşkil etmez.")
        executive_summary = "\n\n".join(summary_lines)

        # Öneri İnşası
        rec_lines = [
            "1. Yangın Güvenliği: Eksik algılama ve söndürme altyapısının tamamlanması, periyodik bakım sözleşmelerinin yenilenmesi.",
            "2. Hırsızlık & Tesis Korunumu: Alarm sisteminin akredite bir Alarm İzleme Merkezi'ne (AHM) yönlendirilmesi ve NVR kayıt kapasitesinin artırılması.",
            "3. Elektrik & Afet: EMO onaylı topraklama ve paratoner ölçüm raporlarının tamamlanması, açıkta depolanan emtiaların ivedilikle palet üzerine alınması."
        ]
        recommendations = "\n".join(rec_lines)

        return executive_summary, recommendations
