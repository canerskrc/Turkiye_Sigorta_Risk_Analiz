"""
Risk Skorlama ve Otomatik İyileştirme Önerisi Üretim Motoru.
Yangın, Fiziksel Güvenlik, Yapısal Özellikler ve Doğal Afet parametrelerini ağırlıklandırarak
şeffaf bir korunum ve risk seviyesi üretir.
Otomatik sigorta kabul/ret kararı VERMEZ; Underwriter için karar destek göstergesi üretir.
"""
from typing import Dict, Any, List, Tuple
from config.settings import (
    RISK_WEIGHTS,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH
)
from src.models.recommendation import Recommendation

class RiskScoringEngine:
    @staticmethod
    def calculate_fire_score(fire_measures: Dict[str, Any]) -> float:
        """Yangın güvenlik önlemleri skorunu hesaplar (0 - 100)."""
        score = 0.0
        # Otomatik Sprinkler Sistemi (30 Puan)
        if fire_measures.get("sprinkler_system", False):
            score += 30.0
        # Yangın Algılama ve Erken Uyarı Sistemi (20 Puan)
        if fire_measures.get("smoke_heat_detectors", False):
            score += 20.0
        # Yangın Dolapları ve Hidrant Hattı (15 Puan)
        if fire_measures.get("hydrant_hose_system", False):
            score += 15.0
        # Yangın Tüpleri ve Güncel Periyodik Bakım (15 Puan)
        if fire_measures.get("extinguishers_present", False):
            score += 5.0
            if fire_measures.get("extinguishers_maintained", False):
                score += 10.0
        # Yangın Kompartmantasyonu ve Yangın Kapıları (10 Puan)
        if fire_measures.get("fire_doors_compartmentation", False):
            score += 10.0
        # Yangın Eğitimi ve Tatbikatı (10 Puan)
        if fire_measures.get("fire_training_done", False):
            score += 10.0
        return min(100.0, score)

    @staticmethod
    def calculate_security_score(security_measures: Dict[str, Any]) -> float:
        """Fiziksel güvenlik ve hırsızlık önlemleri skorunu hesaplar (0 - 100)."""
        score = 0.0
        # 7/24 Fiziki Güvenlik / Bekçi (30 Puan)
        if security_measures.get("guard_24_7", False):
            score += 30.0
        elif security_measures.get("guard_night_only", False):
            score += 15.0
        # CCTV Kamera Sistemi ve Kayıt Süresi (30 Puan)
        if security_measures.get("cctv_present", False):
            score += 15.0
            retention = security_measures.get("cctv_retention_days", 0)
            if retention >= 30:
                score += 15.0
            elif retention >= 15:
                score += 8.0
        # Hırsız Alarmı ve Alarm İzleme Merkezi (AHM) Bağlantısı (25 Puan)
        if security_measures.get("burglar_alarm", False):
            score += 10.0
            if security_measures.get("alarm_monitoring_center", False):
                score += 15.0
        # Çevre Çiti ve Aydınlatma (15 Puan)
        if security_measures.get("perimeter_fence_lighting", False):
            score += 15.0
        return min(100.0, score)

    @staticmethod
    def calculate_construction_score(building_construction: str, occupancy_type: str) -> float:
        """Bina yapı tarzı ve kullanım amacına göre yapısal korunum skoru (0 - 100)."""
        construction_scores = {
            "Betonarme": 90.0,
            "Çelik Konstrüksiyon": 80.0,
            "Prefabrik Beton": 75.0,
            "Yığma Kagir": 55.0,
            "Ahşap / Karma": 35.0
        }
        score = construction_scores.get(building_construction, 65.0)
        
        # Yangın yükü yüksek sektör/kullanım cezası
        high_fire_load_occupancies = ["Kimya Deposu", "Tekstil İmalat", "Plastik Enjeksiyon", "Boya Atölyesi"]
        if occupancy_type in high_fire_load_occupancies:
            score = max(20.0, score - 15.0)
        return min(100.0, score)

    @staticmethod
    def calculate_natural_hazard_score(natural_hazard_measures: Dict[str, Any]) -> float:
        """Doğal afet ve çevresel koruma önlemleri skoru (0 - 100)."""
        score = 0.0
        # Paratoner / Yıldırımdan Korunma ve Topraklama (35 Puan)
        if natural_hazard_measures.get("lightning_rod_present", False):
            score += 20.0
            if natural_hazard_measures.get("grounding_report_valid", False):
                score += 15.0
        # Su Baskını / Sel Tahliye Pompaları ve Yüksek Depolama (35 Puan)
        if natural_hazard_measures.get("flood_drainage_pumps", False):
            score += 20.0
        if natural_hazard_measures.get("elevated_pallet_storage", False):
            score += 15.0
        # Çatı Eğim ve Kar Yükü / Fırtına Bakımı (30 Puan)
        if natural_hazard_measures.get("roof_maintenance_good", False):
            score += 30.0
        return min(100.0, score)

    @classmethod
    def evaluate_risk(
        cls,
        fire_measures: Dict[str, Any],
        security_measures: Dict[str, Any],
        natural_hazard_measures: Dict[str, Any],
        building_construction: str = "Betonarme",
        occupancy_type: str = "Genel"
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Tüm alt başlıkları ağırlıklandırarak genel korunum/güvenlik skorunu ve risk seviyesini hesaplar.
        Skor 100 üzerinden olup:
        80 - 100: Düşük Risk (İyi Korunum)
        60 - 79.9: Orta Risk (Kabul Edilebilir / Gelişime Açık)
        0 - 59.9: Yüksek Risk (Ciddi İyileştirme Gerekir)
        """
        fire = cls.calculate_fire_score(fire_measures)
        sec = cls.calculate_security_score(security_measures)
        const = cls.calculate_construction_score(building_construction, occupancy_type)
        nat = cls.calculate_natural_hazard_score(natural_hazard_measures)

        weighted_score = (
            fire * RISK_WEIGHTS["fire_safety"] +
            sec * RISK_WEIGHTS["physical_security"] +
            const * RISK_WEIGHTS["construction_quality"] +
            nat * RISK_WEIGHTS["natural_hazard"]
        )
        total_score = round(weighted_score, 1)

        if total_score >= 80.0:
            level = RISK_LEVEL_LOW
        elif total_score >= 60.0:
            level = RISK_LEVEL_MEDIUM
        else:
            level = RISK_LEVEL_HIGH

        sub_scores = {
            "fire_score": round(fire, 1),
            "security_score": round(sec, 1),
            "construction_score": round(const, 1),
            "natural_hazard_score": round(nat, 1),
            "total_score": total_score
        }
        return total_score, level, sub_scores

    @classmethod
    def generate_recommendations(
        cls,
        inspection_id: int,
        fire_measures: Dict[str, Any],
        security_measures: Dict[str, Any],
        natural_hazard_measures: Dict[str, Any]
    ) -> List[Recommendation]:
        """Tespit edilen koruma eksikliklerine göre otomatik aksiyon/öneri listesi üretir."""
        recs: List[Recommendation] = []

        # Yangın Önerileri
        if not fire_measures.get("sprinkler_system", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Yüksek",
                category="Yangın",
                finding="Depolama ve üretim alanlarında otomatik sprinkler (yağmurlama) sistemi bulunmamaktadır.",
                action_required="NFPA / Türkiye Yangından Korunma Yönetmeliği'ne uygun otomatik sprinkler projelendirilmelidir.",
                target_deadline_days=60
            ))

        if not fire_measures.get("smoke_heat_detectors", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Kritik",
                category="Yangın",
                finding="Erken yangın algılama ve duman/ısı dedektör ağı mevcut değildir.",
                action_required="Tüm kapalı alanları kapsayan adresli yangın algılama ve ihbar paneli kurulmalıdır.",
                target_deadline_days=30
            ))

        if not fire_measures.get("extinguishers_maintained", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Kritik",
                category="Yangın",
                finding="Taşınabilir yangın söndürme tüplerinin yıllık hidrostatik ve basınç testleri güncel değildir.",
                action_required="Tüm yangın söndürücülerin periyodik bakımı akredite bakım firmasına yaptırılmalı ve etiketlenmelidir.",
                target_deadline_days=15
            ))

        if not fire_measures.get("hydrant_hose_system", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Orta",
                category="Yangın",
                finding="Bina dışı çevre hidrant hattı veya bina içi yangın dolapları yetersizdir.",
                action_required="Yeterli debi ve basınca sahip yangın pompa grubu ve hidrant ring hattı oluşturulmalıdır.",
                target_deadline_days=45
            ))

        # Güvenlik Önerileri
        if not security_measures.get("guard_24_7", False) and not security_measures.get("alarm_monitoring_center", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Yüksek",
                category="Güvenlik",
                finding="Tesis gece ve tatil saatlerinde fiziksel veya uzaktan izleme olmaksızın korunmasız kalmaktadır.",
                action_required="Hırsız alarm sisteminin 7/24 Alarm İzleme Merkezi (AHM) aboneliği başlatılmalı veya gece nöbetçisi görevlendirilmelidir.",
                target_deadline_days=20
            ))

        retention = security_measures.get("cctv_retention_days", 0)
        if retention < 30:
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Orta",
                category="Güvenlik",
                finding=f"CCTV kamera kayıt saklama süresi ({retention} gün) sigorta teftiş standardı olan minimum 30 günün altındadır.",
                action_required="Kayıt cihazı (NVR) hard disk kapasitesi artırılarak geriye dönük minimum 30 günlük arşiv sağlanmalıdır.",
                target_deadline_days=30
            ))

        # Doğal Afet / Elektrik Önerileri
        if not natural_hazard_measures.get("grounding_report_valid", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Yüksek",
                category="Elektrik / Afet",
                finding="Elektrik iç tesisat kontrolü, topraklama ölçümleri ve paratoner geçerlilik raporu bulunmamaktadır.",
                action_required="Elektrik Mühendisleri Odası (EMO) onaylı periyodik topraklama ve paratoner ölçüm raporu temin edilmelidir.",
                target_deadline_days=30
            ))

        if not natural_hazard_measures.get("elevated_pallet_storage", False):
            recs.append(Recommendation(
                inspection_id=inspection_id,
                priority="Düşük",
                category="Depolama / Sel",
                finding="Depolanan emtiaların doğrudan zemin ile temas ettiği, paletsiz istifleme yapıldığı gözlemlenmiştir.",
                action_required="Muhtemel su baskını ve nem hasarlarını önlemek amacıyla tüm emtia minimum 10 cm yüksekliğinde palet üzerine alınmalıdır.",
                target_deadline_days=15
            ))

        return recs
