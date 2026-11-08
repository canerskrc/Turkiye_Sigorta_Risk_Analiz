"""
Teftiş Takip ve Underwriter Karar Destek Konsolu.
Risk Mühendisi, Underwriter ve Saha Satış ekiplerinin teftişleri incelediği ve
Underwriter'ın risk notu / şartlı kabul şartlarını girdiği ekran.
"""
import streamlit as st
from src.database.repository import RiskRepository
from src.ui.components import render_score_badge
from config.settings import ROLE_UNDERWRITER, ROLE_RISK_ENGINEER, ROLE_FIELD_SALES

def render_dashboard_page(repo: RiskRepository):
    st.header("📊 Teftiş ve Risk Takip Konsolu")
    current_role = st.session_state.get("active_role")

    inspections = repo.get_all_inspections()
    if not inspections:
        st.info("Henüz sisteme kaydedilmiş bir risk teftişi bulunmamaktadır. 'Yeni Teftiş Formu' sayfasından teftiş oluşturabilirsiniz.")
        return

    # Özet Metrikler
    total_insp = len(inspections)
    pending_uw = sum(1 for i in inspections if i.status in ["Teftiş Tamamlandı", "UW İncelemesinde"])
    completed_uw = sum(1 for i in inspections if i.status == "Onaylandı")

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Toplam Teftiş", total_insp)
    col_m2.metric("UW İncelemesinde", pending_uw)
    col_m3.metric("Sonuçlandırılmış", completed_uw)
    st.markdown("---")

    # Teftiş Listesi ve Seçimi
    insp_dict = {}
    for i in inspections:
        client = repo.get_client_by_id(i.client_id)
        c_name = client.company_name if client else f"Müşteri #{i.client_id}"
        label = f"#{i.id} - {c_name} | {i.inspection_date} | {i.status} | Skor: {i.calculated_risk_score:.1f}"
        insp_dict[label] = (i, client)

    selected_label = st.selectbox("İncelemek İstediğiniz Teftişi Seçiniz:", list(insp_dict.keys()))
    insp, client = insp_dict[selected_label]

    # Teftiş Detay Kartı
    st.subheader(f"📌 Teftiş Detayı: {client.company_name if client else ''}")
    render_score_badge(insp.calculated_risk_score, insp.risk_level)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.write(f"**Teftiş Tarihi:** {insp.inspection_date}")
        st.write(f"**Mühendis:** {insp.inspector_name}")
    with c2:
        st.write(f"**Yapı Tarzı:** {insp.building_construction}")
        st.write(f"**Toplam Alan:** {insp.total_area_sqm:,.0f} m²")
    with c3:
        st.write(f"**Teftiş Durumu:** `{insp.status}`")
        st.write(f"**Sektör:** {client.sector if client else '-'}")

    # AI Özeti & Bulgular
    st.markdown("---")
    st.subheader("🤖 AI Risk Analisti Yönetici Özeti")
    st.info(insp.ai_executive_summary or "Özet bulunmuyor.")

    # Fotoğraflar
    photos = repo.get_photos_for_inspection(insp.id)
    if photos:
        st.markdown(f"**Saha Fotoğrafları ({len(photos)} Adet):**")
        p_cols = st.columns(min(len(photos), 3))
        for idx, p in enumerate(photos):
            with p_cols[idx % 3]:
                st.image(p.file_path, caption=f"[{p.category}] {p.caption}", use_container_width=True)

    # Underwriter İnceleme ve Karar Notu Alanı
    st.markdown("---")
    st.subheader("⚖️ Underwriter (UW) Karar Destek ve Şartlı Not Bölümü")

    if current_role == ROLE_UNDERWRITER:
        with st.form(f"uw_form_{insp.id}"):
            st.markdown(
                "ℹ️ **UW Talimatı:** Lütfen risk skorunu, yangın önlemlerini ve AI özetini değerlendiriniz. "
                "Otomatik kabul/ret uygulanmaz; risk şartlarınızı ve muafiyet/fiyatlama notlarınızı belirleyiniz."
            )
            uw_notes_input = st.text_area(
                "Underwriter Değerlendirme & Şartlı Kabul Notu:",
                value=insp.uw_notes,
                placeholder="Örn: Yangın tüpleri bakımı 15 gün içinde belgelenmek şartıyla %10 ko-sigorta ve 1.25 risk sürprimi ile teklif verilebilir."
            )
            new_status = st.selectbox(
                "Teftiş Süreç Durumu:",
                ["UW İncelemesinde", "Şartlı Teklif Verildi", "Risk İyileştirmesi Bekleniyor", "Onaylandı"],
                index=0
            )
            save_uw_btn = st.form_submit_button("💾 UW Karar Notunu ve Durumu Güncelle", type="primary")

        if save_uw_btn:
            insp.uw_notes = uw_notes_input
            insp.status = new_status
            repo.update_inspection(insp)
            st.success("✅ Underwriter değerlendirmesi başarıyla kaydedildi!")
            st.rerun()
    else:
        st.info(f"**Mevcut UW Notu:** {insp.uw_notes or 'Henüz UW inceleme notu girilmemiştir.'}")
        if current_role == ROLE_FIELD_SALES:
            st.caption("🔒 Saha Satış rolündesiniz. UW notlarını görüntüleyebilir, ancak düzenleyemezsiniz.")
        elif current_role == ROLE_RISK_ENGINEER:
            st.caption("🔒 Risk Mühendisi rolündesiniz. UW notları Underwriter tarafından düzenlenir.")
