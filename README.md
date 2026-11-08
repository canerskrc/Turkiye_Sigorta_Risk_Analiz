# Dijital Risk Analiz Formu (MVP)

Sigortacılık sektöründe endüstriyel ve ticari tesislerin saha riziko teftiş (risk inspection) süreçlerini dijitalleştiren, fotoğraflı bulguları kayıt altına alan, yangın ve fiziksel güvenlik önlemlerini skorlayan, Underwriter için karar destek notları üreten ve ReportLab ile kurumsal Türkçe PDF raporu hazırlayan bağımsız bir MVP uygulamasıdır.

---

## 🚀 Temel Özellikler
1. **Saha Riziko Teftiş Formu:** Yangın, güvenlik, yapısal ve doğal afet önlemlerini içeren kapsamlı teftiş kontrol listesi.
2. **Saha Fotoğrafı Yükleme & Sıkıştırma:** Fotoğrafları kategorilendirerek (Yangın, Elektrik, Depolama vb.) saklama ve rapora gömme.
3. **Şeffaf Risk Skorlama Motoru:** Ağırlıklı korunum puanı (0-100) ve risk seviyesi (Düşük, Orta, Yüksek) hesaplama.
4. **Ollama Lokal LLM / Akıllı Fallback Danışmanı:** Yerel LLM ile teftiş özeti ve iyileştirme tavsiyeleri üretimi (çevrimdışı fallback motoru dahil).
5. **ReportLab Profesyonel PDF Teftiş Raporu:** Türkçe karakter uyumlu, risk skor kartı, bulgular, aksiyon tablosu ve fotoğraf galerisi içeren kurumsal PDF çıktısı.
6. **Rol Bazlı Erişim (RBAC):**
   - **Risk Mühendisi:** Form doldurma, fotoğraf ekleme, risk skoru ve teknik analiz.
   - **Underwriter (UW):** Risk inceleme, şartlı kabul ve sürprim/muafiyet notu girişi (**Kesin otomatik kabul/ret kararı verilmez**).
   - **Saha Satış Ekibi:** Müşteri teftiş durumunu ve iyileştirme aksiyonlarının takibi.
7. **Sentetik Saha 360 Entegrasyonu:** Gerçek sistemlere bağlanmadan, güvenli sentetik kurumsal müşteri ve tesis profilleri sağlayan mock servis katmanı.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Sanal Ortamı Aktif Edin ve Bağımlılıkları Yükleyin
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın
```bash
streamlit run app.py
```
Tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacaktır.

### 3. Testleri Çalıştırın
```bash
pytest -v
```

---

## 🤖 Lokal LLM (Ollama) Yapılandırması (Opsiyonel)
Sistemde yerel Ollama çalışıyorsa otomatik olarak algılar ve kullanır:
```bash
ollama run llama3
```
*Not: Ollama kurulu olmasa veya servis kapalı olsa dahi, entegre akıllı kural tabanlı fallback motoru sayesinde sistem kesintisiz olarak yüksek kaliteli risk analizleri üretmeye devam eder.*

---

## 📂 Dizin Yapısı
- `app.py`: Streamlit ana giriş noktası ve menü yönlendiricisi
- `config/`: Ayarlar, roller, skor ağırlıkları ve dosya yolları
- `src/models/`: Client, Inspection, Recommendation veri modelleri
- `src/database/`: SQLite bağlantısı, SQL şeması ve Repository CRUD katmanı
- `src/services/`: Saha 360 Mock, Skorlama Motoru, AI Danışmanı ve PDF Motoru
- `src/ui/`: Sayfa arayüzleri (Teftiş formu, Dashboard, Öneri Takibi, Raporlama)
- `src/utils/`: Görsel işleme ve sıkıştırma yardımcıları
- `tests/`: Kapsamlı pytest birim ve entegrasyon testleri
