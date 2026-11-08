"""
Saha Teftiş ve Risk Analiz Formu Sayfası.
Risk Mühendisi tarafından saha teftiş bulgularını girmek, fotoğraf yüklemek,
skor hesaplamak ve AI analizini başlatmak için kullanılır.
"""
import streamlit as st
import datetime
from src.database.repository import RiskRepository
from src.services.mock_saha360 import MockSaha360Service
from src.services.scoring_engine import RiskScoringEngine
from src.services.ai_advisor import AIAdvisorService
from src.utils.image_handler import save_and_compress_image
from src.models.inspection import Inspection, InspectionPhoto
from config.settings import ROLE_RISK_ENGINEER

def render_inspection_page(repo: RiskRepository):
    st.header("📋 Yeni Saha Riziko Teftiş Formu")
    current_role = st.session_state.get("active_role")

    if current_role != ROLE_RISK_ENGINEER:
        st.warning(f"🔒 Bu form yalnızca **{ROLE_RISK_ENGINEER}** rolü tarafından doldurulabilir ve düzenlenebilir. Aktif rolünüz: **{current_role}**")
        st.info("Sol menüden rolünüzü 'Risk Mühendisi' olarak değiştirerek formu test edebilirsiniz.")
        return

    saha_service = MockSaha360Service(repo)
    clients = repo.get_all_clients()
    if not clients:
        saha_service.seed_synthetic_clients()
        clients = repo.get_all_clients()

    # Müşteri Seçimi (Saha 360 Entegrasyonu)
    st.subheader("1. Riziko Lokasyonu ve Müşteri Seçimi (Saha 360)")
    client_options = {f"{c.company_name} ({c.synthetic_code} - {c.city})": c for c in clients}
    selected_label = st.selectbox("Sentetik Saha 360 Müşterisi Seçiniz:", list(client_options.keys()))
    selected_client = client_options[selected_label]

    with st.expander("📌 Seçilen Müşteri Künyesi Detayı", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Sektör:** {selected_client.sector}")
        c1.write(f"**Adres:** {selected_client.address}")
        c2.write(f"**Şehir / İlçe:** {selected_client.city} / {selected_client.district}")
        c2.write(f"**Tehlike Sınıfı:** {selected_client.hazard_class}")
        c3.write(f"**Sigorta Bedeli:** {selected_client.insured_value:,.2f} TL")
        c3.write(f"**Sentetik Kod:** {selected_client.synthetic_code}")

    st.markdown("---")

    # Form Başlangıcı
    with st.form("inspection_form"):
        st.subheader("2. Genel & Yapısal Özellikler")
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            inspector_name = st.text_input("Risk Mühendisi Adı Soyadı", value="Caner Şekerci")
            inspection_date = st.date_input("Teftiş Tarihi", value=datetime.date.today()).strftime("%Y-%m-%d")
        with col_g2:
            occupancy_type = st.selectbox("Tesis Faaliyeti / Kullanım Amacı", [
                "Üretim ve İmalat", "Depolama ve Antrepo", "Kimya Deposu", "Tekstil İmalat",
                "Metal / Mekanik Atölye", "Bilişim ve Ofis", "Plastik Enjeksiyon"
            ])
            building_construction = st.selectbox("Bina Yapı Tarzı", [
                "Betonarme", "Çelik Konstrüksiyon", "Prefabrik Beton", "Yığma Kagir", "Ahşap / Karma"
            ])
        with col_g3:
            total_area_sqm = st.number_input("Toplam Kapalı Alan (m²)", min_value=100.0, max_value=500000.0, value=3500.0, step=100.0)
            number_of_floors = st.number_input("Kat Sayısı", min_value=1, max_value=50, value=2)

        st.markdown("---")
        st.subheader("3. Yangın Önlemleri ve Söndürme Sistemleri")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sprinkler = st.checkbox("Otomatik Sprinkler (Yağmurlama) Sistemi Mevcut", value=False)
            smoke_detectors = st.checkbox("Yangın Algılama & Duman Dedektör Ağı Mevcut", value=True)
            hydrant_hose = st.checkbox("Bina Dışı Yangın Hidrantı / İçi Yangın Dolabı Var", value=True)
        with col_f2:
            extinguishers_present = st.checkbox("Yeterli Sayıda Taşınabilir Yangın Tüpü Var", value=True)
            extinguishers_maintained = st.checkbox("Yangın Tüplerinin Periyodik Bakımı Güncel", value=False)
            fire_doors = st.checkbox("Yangın Kompartmantasyonu & Yangın Kapıları Mevcut", value=False)
            fire_training = st.checkbox("Personel Yangın Eğitimi ve Tahliye Tatbikatı Yapılmış", value=True)

        st.markdown("---")
        st.subheader("4. Fiziksel Güvenlik ve Hırsızlık Önlemleri")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            guard_24_7 = st.checkbox("7/24 Özel Güvenlik Görevlisi / Bekçi Mevcut", value=False)
            guard_night = st.checkbox("Yalnızca Gece / Tatil Nöbetçisi Mevcut", value=True)
            cctv_present = st.checkbox("CCTV Kapalı Devre Kamera Sistemi Mevcut", value=True)
        with col_s2:
            cctv_retention = st.slider("CCTV Kamera Kayıt Saklama Süresi (Gün)", min_value=0, max_value=90, value=15)
            burglar_alarm = st.checkbox("Hırsız Alarm Sistemi Mevcut", value=True)
            alarm_monitoring = st.checkbox("Alarm Sistemi 7/24 Alarm İzleme Merkezine (AHM) Bağlı", value=False)
            perimeter_fence = st.checkbox("Çevre Çiti, Tel Örgü ve Gece Çevre Aydınlatması Tam", value=True)

        st.markdown("---")
        st.subheader("5. Doğal Afet, Elektrik ve Çevresel Önlemler")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            lightning_rod = st.checkbox("Paratoner (Yıldırımlık) Sistemi Mevcut", value=True)
            grounding_report = st.checkbox("EMO Onaylı Topraklama Ölçüm Raporu Güncel", value=False)
        with col_n2:
            flood_drainage = st.checkbox("Sel / Su Tahliye Pompaları ve Drenaj Kanalları Mevcut", value=True)
            elevated_storage = st.checkbox("Emtia Depolaması Palet Üzerinde (Min 10 cm Yükseklik)", value=False)
            roof_maintenance = st.checkbox("Çatı Bakımı ve Kar Yükü Mukavemeti İyi Durumda", value=True)

        submit_btn = st.form_submit_button("💾 Teftiş Verilerini Kaydet ve Risk Skorunu Hesapla", type="primary")

    # Form Gönderildiğinde
    if submit_btn:
        fire_measures = {
            "sprinkler_system": sprinkler,
            "smoke_heat_detectors": smoke_detectors,
            "hydrant_hose_system": hydrant_hose,
            "extinguishers_present": extinguishers_present,
            "extinguishers_maintained": extinguishers_maintained,
            "fire_doors_compartmentation": fire_doors,
            "fire_training_done": fire_training
        }
        security_measures = {
            "guard_24_7": guard_24_7,
            "guard_night_only": guard_night,
            "cctv_present": cctv_present,
            "cctv_retention_days": cctv_retention,
            "burglar_alarm": burglar_alarm,
            "alarm_monitoring_center": alarm_monitoring,
            "perimeter_fence_lighting": perimeter_fence
        }
        natural_measures = {
            "lightning_rod_present": lightning_rod,
            "grounding_report_valid": grounding_report,
            "flood_drainage_pumps": flood_drainage,
            "elevated_pallet_storage": elevated_storage,
            "roof_maintenance_good": roof_maintenance
        }

        # Skor Hesapla
        score, level, sub_scores = RiskScoringEngine.evaluate_risk(
            fire_measures, security_measures, natural_measures,
            building_construction, occupancy_type
        )

        # AI Analizini Al (Ollama / Fallback)
        with st.spinner("AI Risk Analisti değerlendirme hazırlıyor (Ollama / Lokal Fallback)..."):
            ai_service = AIAdvisorService()
            summary, ai_recs = ai_service.generate_risk_analysis(
                selected_client.company_name, selected_client.sector,
                selected_client.hazard_class, building_construction,
                score, level, fire_measures, security_measures, natural_measures
            )

        # Teftiş Nesnesi Oluştur
        inspection = Inspection(
            client_id=selected_client.id,
            inspector_name=inspector_name,
            inspection_date=inspection_date,
            occupancy_type=occupancy_type,
            building_construction=building_construction,
            total_area_sqm=total_area_sqm,
            number_of_floors=number_of_floors,
            fire_measures=fire_measures,
            security_measures=security_measures,
            natural_hazard_measures=natural_measures,
            calculated_risk_score=score,
            risk_level=level,
            ai_executive_summary=summary,
            ai_recommendations=ai_recs,
            status="Teftiş Tamamlandı"
        )

        insp_id = repo.create_inspection(inspection)
        st.session_state["last_created_inspection_id"] = insp_id

        # Otomatik Önerileri Türet ve DB'ye Ekle
        generated_recs = RiskScoringEngine.generate_recommendations(
            insp_id, fire_measures, security_measures, natural_measures
        )
        for r in generated_recs:
            repo.add_recommendation(r)

        st.success(f"✅ Teftiş No #{insp_id} başarıyla kaydedildi! Otomatik {len(generated_recs)} iyileştirme önerisi oluşturuldu.")

    # Fotoğraf Yükleme Bölümü (Kayıtlı Teftiş Varsa)
    last_id = st.session_state.get("last_created_inspection_id")
    if last_id:
        st.markdown("---")
        st.subheader(f"📸 Saha Fotoğrafı Ekle (Teftiş #{last_id})")
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            uploaded_file = st.file_uploader("Saha Fotoğrafı Seçiniz (JPG / PNG):", type=["jpg", "jpeg", "png"])
            caption = st.text_input("Fotoğraf Açıklaması / Not:", placeholder="Örn: Sprinkler vana istasyonu ve basınç saati")
        with col_p2:
            photo_cat = st.selectbox("Fotoğraf Kategorisi:", ["Yangın", "Güvenlik", "Elektrik", "Depolama", "Bina / Çevre", "Genel"])
            upload_btn = st.button("📤 Fotoğrafı Teftişe Ekle", type="secondary")

        if upload_btn and uploaded_file is not None:
            file_bytes = uploaded_file.read()
            saved_path = save_and_compress_image(file_bytes, uploaded_file.name)
            photo = InspectionPhoto(
                inspection_id=last_id,
                file_path=saved_path,
                category=photo_cat,
                caption=caption
            )
            repo.add_photo(photo)
            st.success("📷 Fotoğraf başarıyla teftişe eklendi!")

        # Eklenmiş Fotoğrafları Göster
        current_photos = repo.get_photos_for_inspection(last_id)
        if current_photos:
            st.markdown(f"**Yüklenmiş Fotoğraflar ({len(current_photos)} adet):**")
            p_cols = st.columns(min(len(current_photos), 4))
            for idx, p in enumerate(current_photos):
                with p_cols[idx % 4]:
                    st.image(p.file_path, caption=f"[{p.category}] {p.caption}", use_container_width=True)
