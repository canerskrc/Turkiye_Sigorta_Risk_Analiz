"""
Risk İyileştirme Önerileri ve Aksiyon Takip Sayfası.
Saha Satış, Underwriter ve Risk Mühendisi ekiplerinin müşteriye iletilen risk önlemlerini
adım adım takip edebilmesini sağlar.
"""
import streamlit as st
from src.database.repository import RiskRepository
from src.models.recommendation import Recommendation
from config.settings import ROLE_FIELD_SALES, ROLE_RISK_ENGINEER, ROLE_UNDERWRITER

def render_recommendations_page(repo: RiskRepository):
    st.header("🎯 Risk İyileştirme Önerileri ve Aksiyon Takibi")
    current_role = st.session_state.get("active_role")

    st.markdown(
        "Teftiş sonrasında otomatik tespit edilen ve mühendis tarafından onaylanan "
        "yangın, fiziksel güvenlik ve doğal afet aksiyonlarının müşteri nezdinde takibi yapılır."
    )

    all_recs = repo.get_all_recommendations()
    if not all_recs:
        st.info("Sistemde henüz kayıtlı bir risk iyileştirme önerisi bulunmamaktadır.")
        return

    # Filtreler
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        priority_filter = st.multiselect(
            "Öncelik Seviyesine Göre Filtrele:",
            ["Kritik", "Yüksek", "Orta", "Düşük"],
            default=["Kritik", "Yüksek", "Orta", "Düşük"]
        )
    with c_f2:
        status_filter = st.multiselect(
            "Aksiyon Durumuna Göre Filtrele:",
            ["Açık", "Müşteri Bilgilendirildi", "Uygulandı", "İptal"],
            default=["Açık", "Müşteri Bilgilendirildi", "Uygulandı", "İptal"]
        )

    filtered_recs = [
        r for r in all_recs
        if r.priority in priority_filter and r.status in status_filter
    ]

    st.write(f"Toplam **{len(filtered_recs)}** aksiyon maddesi listeleniyor.")
    st.markdown("---")

    # Aksiyon Kartları
    for rec in filtered_recs:
        insp = repo.get_inspection_by_id(rec.inspection_id)
        client = repo.get_client_by_id(insp.client_id) if insp else None
        client_name = client.company_name if client else f"Teftiş #{rec.inspection_id}"

        # Renk ve İkon
        priority_icons = {
            "Kritik": "🔴",
            "Yüksek": "🟠",
            "Orta": "🟡",
            "Düşük": "🔵"
        }
        icon = priority_icons.get(rec.priority, "⚪")

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1.5])
            with col1:
                st.markdown(f"#### {icon} [{rec.category}] {client_name}")
                st.write(f"**Tespit:** {rec.finding}")
                st.markdown(f"**Gereken Aksiyon:** `{rec.action_required}`")
            with col2:
                st.write(f"**Öncelik:** {rec.priority}")
                st.write(f"**Termin:** {rec.target_deadline_days} Gün")
                st.write(f"**Durum:** `{rec.status}`")
            with col3:
                # Saha Satış veya Mühendis durum güncelleyebilir
                new_status = st.selectbox(
                    "Durumu Değiştir:",
                    ["Açık", "Müşteri Bilgilendirildi", "Uygulandı", "İptal"],
                    index=["Açık", "Müşteri Bilgilendirildi", "Uygulandı", "İptal"].index(rec.status),
                    key=f"status_select_{rec.id}"
                )
                if new_status != rec.status:
                    if st.button("Güncelle", key=f"btn_up_{rec.id}"):
                        repo.update_recommendation_status(rec.id, new_status)
                        st.success(f"Aksiyon #{rec.id} güncellendi!")
                        st.rerun()

            st.markdown("---")
