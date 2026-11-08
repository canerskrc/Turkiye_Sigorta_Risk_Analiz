"""
PDF Teftiş Raporu Üretme ve İndirme Sayfası.
ReportLab motoruyla oluşturulan kurumsal PDF raporunun önizlenmesi ve indirilmesini sağlar.
"""
import streamlit as st
import os
from src.database.repository import RiskRepository
from src.services.pdf_generator import RiskPDFGenerator

def render_reports_page(repo: RiskRepository):
    st.header("📑 Teftiş Raporu ve PDF Üretimi")
    st.markdown("Tamamlanmış risk teftişleri için ReportLab motoru ile Türkçe karakter uyumlu, fotoğraflı resmi teftiş raporu üretiniz.")

    inspections = repo.get_all_inspections()
    if not inspections:
        st.info("Rapor oluşturulabilecek kayıtlı bir teftiş bulunmamaktadır.")
        return

    insp_dict = {}
    for i in inspections:
        client = repo.get_client_by_id(i.client_id)
        c_name = client.company_name if client else f"Müşteri #{i.client_id}"
        label = f"#{i.id} - {c_name} (Tarih: {i.inspection_date} | Skor: {i.calculated_risk_score:.1f})"
        insp_dict[label] = (i, client)

    selected_label = st.selectbox("Raporunu Üretmek İstediğiniz Teftişi Seçiniz:", list(insp_dict.keys()))
    insp, client = insp_dict[selected_label]
    recs = repo.get_recommendations_for_inspection(insp.id)

    # Özet Kartı
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Rapor Künyesi")
        st.write(f"**Müşteri:** {client.company_name if client else '-'}")
        st.write(f"**Teftiş No:** TR-RISK-{insp.id}")
        st.write(f"**Mühendis:** {insp.inspector_name}")
        st.write(f"**Teftiş Tarihi:** {insp.inspection_date}")
    with c2:
        st.subheader("Risk Göstergesi")
        st.write(f"**Korunum Skoru:** {insp.calculated_risk_score:.1f} / 100")
        st.write(f"**Risk Seviyesi:** {insp.risk_level}")
        st.write(f"**Toplam Aksiyon Maddesi:** {len(recs)} adet")
        st.write(f"**Ekli Fotoğraf Sayısı:** {len(insp.photos)} adet")

    st.markdown("---")
    
    # PDF Oluştur Butonu
    if st.button("📄 Profesyonel PDF Raporu Oluştur", type="primary"):
        with st.spinner("ReportLab ile kurumsal PDF raporu derleniyor..."):
            pdf_path = RiskPDFGenerator.generate_report(client, insp, recs)
            st.session_state["current_pdf_path"] = pdf_path
            st.success(f"✅ PDF Raporu başarıyla üretildi: `{os.path.basename(pdf_path)}`")

    # İndirme Butonu (PDF varsa)
    current_pdf = st.session_state.get("current_pdf_path")
    if current_pdf and os.path.exists(current_pdf):
        with open(current_pdf, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="⬇️ PDF Raporunu Bilgisayara İndir",
            data=pdf_bytes,
            file_name=os.path.basename(current_pdf),
            mime="application/pdf",
            type="secondary"
        )
