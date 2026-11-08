"""
Dijital Risk Analiz Formu - Streamlit Ana Giriş Noktası.
Riziko teftiş ziyaretinden dijital forma, fotoğraf ekleme, yangın ve güvenlik önlemleri skorlamasına,
AI analizi, PDF raporu ve öneri takibine uzanan bağımsız MVP uygulaması.
"""
import streamlit as st
from config.settings import DB_PATH
from src.database.connection import init_db
from src.database.repository import RiskRepository
from src.services.mock_saha360 import MockSaha360Service

from src.ui.components import render_sidebar
from src.ui.page_inspection import render_inspection_page
from src.ui.page_dashboard import render_dashboard_page
from src.ui.page_recommendations import render_recommendations_page
from src.ui.page_reports import render_reports_page

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Dijital Risk Analiz Formu - MVP",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Veritabanı ve Sentetik Veri Başlatma (Singleton)
@st.cache_resource
def setup_application():
    init_db(DB_PATH)
    repo = RiskRepository(DB_PATH)
    saha_service = MockSaha360Service(repo)
    saha_service.seed_synthetic_clients()
    return repo

def main():
    repo = setup_application()
    current_role = render_sidebar()

    # Sayfa Seçim Menüsü
    st.sidebar.subheader("📌 Navigasyon")
    menu = st.sidebar.radio(
        "Modül Seçiniz:",
        [
            "📋 Yeni Teftiş Formu",
            "📊 Teftiş & UW Konsolu",
            "🎯 Risk Önerileri & Aksiyon Takibi",
            "📑 PDF Raporu & Çıktı"
        ]
    )

    if menu == "📋 Yeni Teftiş Formu":
        render_inspection_page(repo)
    elif menu == "📊 Teftiş & UW Konsolu":
        render_dashboard_page(repo)
    elif menu == "🎯 Risk Önerileri & Aksiyon Takibi":
        render_recommendations_page(repo)
    elif menu == "📑 PDF Raporu & Çıktı":
        render_reports_page(repo)

if __name__ == "__main__":
    main()
