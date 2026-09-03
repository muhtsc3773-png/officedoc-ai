import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader

# Web Sayfasının Başlığı ve Kurumsal Tasarımı
st.set_page_config(page_title="OfficeDoc AI - Pro", page_icon="🏢", layout="wide")

st.title("🏢 OfficeDoc AI — Kurumsal Doküman Yönetim Paneli")
st.write("Şirket içi dağınık bilgiyi tek bir noktadan yönetin, özetleyin ve görevleri otomatik ayıklayın.")

# 🔑 SENİN ALDIĞIN CANLI YAPAY ZEKA ŞİFREN
YAPAY_ZEKA_ANAHTARI = "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"
client = Groq(api_key=YAPAY_ZEKA_ANAHTARI)

def pdf_metnini_oku(yuklenen_dosya):
    """Yüklenen PDF dosyasındaki tüm metinleri okur."""
    text = ""
    try:
        reader = PdfReader(yuklenen_dosya)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"PDF okunurken bir sorun oluştu: {e}")
        return None

def yapay_zeka_talebi(dokuman_metni, gorev_tipi, ek_soru=""):
    """Groq dokümantasyonundaki en güncel aktif modele kurumsal talimatları gönderir."""
    talimatlar = {
        "arama": (
            "Sen OfficeDoc AI arama asistanısın. Sana verilen döküman içeriğine göre kullanıcının sorusunu Türkçe yanıtla. "
            "Kritik Kural: Eğer sorunun cevabı dökümanda yoksa, asla dışarıdan bilgi uydurma. "
            "'Bu bilgi yüklenen dökümanlarda bulunamadı' şeklinde cevap ver."
        ),
        "ozet": (
            "Sen bir döküman özetleme asistanısın. Sana verilen uzun dökümanı analiz et. "
            "Çalışanın tüm dökümanı okumasına gerek kalmaması için en kritik noktaları, "
            "onay süreçlerini ve önemli başlıkları kısa, anlaşılır maddeler halinde Türkçe özetle."
        ),
        "govev_cikarma": (
            "Sen kurumsal bir analiz uzmanısın. Toplantı notu veya dökümandaki görevleri (action items) ayıkla. "
            "Kimin ne yapacağını, önemli tarihleri ve alınan kararları GÖREVLER ve ÖNEMLİ TARİHLER başlıkları altında liste halinde Türkçe çıkar."
        ),
        "versiyon": (
            "Sen bir döküman versiyon kontrol uzmanısın. Bu dökümanın metnini incele. "
            "Dökümanın içinde geçen tarihi, versiyon numarasını (V1, V2, FINAL vb.) bul ve güncellik durumunu raporla."
        )
    }
    
    sistem_talimati = talimatlar.get(gorev_tipi, talimatlar["arama"])
    kullanici_icerigi = f"DÖKÜMAN İÇERİĞİ:\n{dokuman_metni}\n\nKULLANICI SORUSU: {ek_soru}" if gorev_tipi == "arama" else f"DÖKÜMAN İÇERİĞİ:\n{dokuman_metni}"
        
    try:
        # 🎯 Resmi Groq listesindeki en güncel aktif üretim modeli: qwen/qwen3.6-27b
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": sistem_talimati},
                {"role": "user", "content": kullanici_icerigi}
            ],
            temperature=0.1
        )
        return response.choices.message.content
    except Exception as e:
        return f"Yapay zeka yanıt verirken bir bulut hatası oluştu: {e}"

# 🗂️ Sol Taraf: Dosya Yükleme Paneli
with st.sidebar:
    st.header("📁 Doküman Yükleme")
    yuklenen_dosya = st.file_uploader("Bir PDF dosyası seçin", type=["pdf"])
    
    if yuklenen_dosya:
        st.success(f"✅ {yuklenen_dosya.name}")
        with st.spinner("Doküman okunuyor..."):
            dokuman_icerigi = pdf_metnini_oku(yuklenen_dosya)
            
        st.write("---")
        st.subheader("⚙️ Hızlı İşlemler")
        ozet_butonu = st.button("📄 Dokümanı Özetle")
        gorev_butonu = st.button("🧠 Görevleri/Kararları Çıkar")
        versiyon_butonu = st.button("⚠️ Versiyon Kontrolü Yap")

# 🖥️ Sağ Taraf: Ana Çalışma Alanı
if yuklenen_dosya and dokuman_icerigi:
    if ozet_butonu:
        st.header("📄 Doküman Özeti")
        with st.spinner("Özet çıkartılıyor..."):
            sonuc = yapay_zeka_talebi(dokuman_icerigi, "ozet")
        st.info(sonuc)
    elif gorev_butonu:
        st.header("🧠 Otomatik Ayıklanan Görevler")
        with st.spinner("Görevler analiz ediliyor..."):
            sonuc = yapay_zeka_talebi(dokuman_icerigi, "govev_cikarma")
        st.success(sonuc)
    elif versiyon_butonu:
        st.header("⚠️ Belge Versiyon Durumu")
        with st.spinner("Versiyon taranıyor..."):
            sonuc = yapay_zeka_talebi(dokuman_icerigi, "versiyon")
        st.warning(sonuc)
    else:
        st.header("🔎 Akıllı Doküman Arama Motoru")
        soru = st.text_input("Dokümanda merak ettiğiniz bilgiyi doğrudan sorun:", placeholder="Örn: Onay süreci nasıl işliyor?")
        if soru:
            with st.spinner("OfficeDoc AI arıyor..."):
                cevap = yapay_zeka_talebi(dokuman_icerigi, "arama", ek_soru=soru)
            st.markdown("### 🤖 Yanıt:")
            st.info(cevap)
else:
    st.info("💡 Başlamak için lütfen sol taraftaki panelden bir kurumsal PDF dokümanı yükleyin.")
