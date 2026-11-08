"""
Ortak UI Bileşenleri ve Arayüz Yardımcıları.
"""
import streamlit as st
from config.settings import (
    ROLE_RISK_ENGINEER,
    ROLE_UNDERWRITER,
    ROLE_FIELD_SALES,
    ALL_ROLES
)

def render_sidebar():
    """Kenar çubuğunu oluşturur; rol seçimi ve sistem bilgilerini sunar."""
    st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
    st.sidebar.title("Dijital Risk Analiz")
    st.sidebar.caption("Sigorta Riziko Teftiş & Karar Destek MVP")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Kullanıcı Profili / Rol")
    current_role = st.sidebar.selectbox(
        "Aktif Rolünüzü Seçiniz:",
        ALL_ROLES,
        index=0,
        help="Sistem rol bazlı yetkilendirme (RBAC) ile çalışmaktadır."
    )
    st.session_state["active_role"] = current_role
    
    # Rol Rozeti
    role_colors = {
        ROLE_RISK_ENGINEER: "orange",
        ROLE_UNDERWRITER: "red",
        ROLE_FIELD_SALES: "blue"
    }
    color = role_colors.get(current_role, "gray")
    st.sidebar.markdown(f":{color}[**Yetki:** {current_role}]")
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "ℹ️ **Yasal Bildirim:** Bu sistem Underwriter karar desteği sağlar; "
        "asla otomatik kabul/ret kararı vermez. Yalnızca sentetik veri kullanır."
    )
    return current_role

def render_score_badge(score: float, level: str):
    """Risk skoru için görsel metrik kartı çizer."""
    if score >= 80:
        color = "green"
        emoji = "🛡️"
    elif score >= 60:
        color = "orange"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "🚨"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Genel Korunum Skoru", value=f"{score:.1f} / 100")
    with col2:
        st.markdown(f"### {emoji} :{color}[{level}]")
