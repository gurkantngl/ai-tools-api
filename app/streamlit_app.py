import streamlit as st
import requests
import json
import time

# Tema ayarları
st.set_page_config(
    page_title="AI Tool API Arayüzü",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/gurkantngl',
        'Report a bug': "https://github.com/gurkantngl/issues",
        'About': "# AI Tool API Arayüzü\nYapay zeka tabanlı araçlar sunan bir REST servisi."
    }
)

# Tema seçimi için session state kontrolü
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

# Tema seçimi
theme = st.sidebar.selectbox(
    "Tema Seçin",
    ["Light", "Dark"],
    index=1 if st.session_state.theme == "Dark" else 0
)

# Tema değişikliğini kontrol et
if theme != st.session_state.theme:
    st.session_state.theme = theme
    st.rerun()

# CSS stilleri
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .document-content {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
    }
    .stTextArea textarea {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stSelectbox > div > div {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stTextInput input {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    div[data-baseweb="select"] {
        background-color: #2D2D2D;
    }
    div[data-baseweb="select"] > div {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    div[role="listbox"] {
        background-color: #2D2D2D;
    }
    div[role="option"] {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stMarkdown {
        color: #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
    }
    .document-content {
        background-color: #f0f2f6 !important;
        color: #1f1f1f !important;
    }
    .stTextArea textarea {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stTextInput input {
        background-color: #FFFFFF;
        color: #000000;
    }
    div[data-baseweb="select"] {
        background-color: #FFFFFF;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        color: #000000;
    }
    div[role="listbox"] {
        background-color: #FFFFFF;
    }
    div[role="option"] {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stMarkdown {
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# Sayfa başlığı ve açıklaması
st.title("🤖 AI Tool API Arayüzü")
st.markdown("""
Bu uygulama, AI Tool API'sinin özelliklerini kullanmanızı sağlar:
- 📝 Döküman Yükleme ve Vektör Arama
- 🔢 Matematik İşlemleri
- 🔑 Anahtar Kelime Çıkarma
""")

# API endpoint'i
API_URL = "http://localhost:8000"

# Sidebar ile işlem seçimi
islem = st.sidebar.selectbox(
    "İşlem Seçin",
    ["Döküman İşlemleri", "Matematik İşlemleri", "Anahtar Kelime Çıkarma"]
)

# Döküman İşlemleri
if islem == "Döküman İşlemleri":
    st.header("📝 Döküman İşlemleri")
    
    # Döküman yükleme
    st.subheader("Döküman Yükleme")
    uploaded_file = st.file_uploader("Bir metin dosyası seçin", type=['txt', 'pdf', 'md', 'rst'])
    if uploaded_file:
        with st.spinner('Döküman yükleniyor...'):
            files = {"file": uploaded_file}
            try:
                response = requests.post(f"{API_URL}/documents/upload", files=files)
                if response.status_code in [200, 201]:
                    st.success(response.json()["message"])
                else:
                    st.error(f"Hata: {response.json().get('detail', 'Bilinmeyen bir hata oluştu.')}")
            except Exception as e:
                st.error(f"Bağlantı hatası: {str(e)}")
    
    # Vektör arama
    st.subheader("Vektör Arama")
    search_query = st.text_input("Arama sorgusu girin:")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Gösterilecek sonuç sayısını seçin:**")
        st.markdown("*Not: Daha fazla sonuç, benzerlik oranı daha düşük olan dökümanları da getirecektir.*")
    with col2:
        top_k = st.number_input("", min_value=1, max_value=20, value=5, key="top_k_input")
    
    if st.button("Ara", type="primary"):
        if search_query:
            with st.spinner('Arama yapılıyor...'):
                try:
                    response = requests.post(
                        f"{API_URL}/vector/search",
                        json={"query": search_query, "top_k": top_k}
                    )
                    if response.status_code == 200:
                        results = response.json()["results"]
                        
                        # Cache durumunu kontrol et
                        is_cached = response.headers.get("X-Cache") == "HIT"
                        cache_status = "🔄 Cache'den geldi" if is_cached else "🆕 Yeni sorgu"
                        
                        st.markdown(f"### 🔍 Arama Sonuçları ({cache_status})")
                        
                        if not results:
                            st.warning("Aramanızla eşleşen sonuç bulunamadı.")
                        else:
                            for idx, result in enumerate(results):
                                st.markdown("---")
                                st.markdown(f"#### 📄 Döküman {idx + 1}")
                                
                                # Benzerlik skoru - ChromaDB'den gelen değeri normalize et
                                similarity = result.get("similarity", 0)
                                normalized_similarity = 1 - min(max(similarity, 0), 1)  # Değeri 0-1 arasına normalize et
                                
                                st.markdown("**Benzerlik Oranı:**")
                                st.progress(normalized_similarity)
                                st.markdown(f"**{normalized_similarity * 100:.1f}%**")
                                
                                # İçerik
                                st.markdown("**İçerik:**")
                                document_text = result.get("content", "")
                                if document_text:
                                    st.markdown(f"""
                                    <div style="background-color: {'#2D2D2D' if theme == 'Dark' else '#f0f2f6'}; 
                                         color: {'#E0E0E0' if theme == 'Dark' else '#1f1f1f'}; 
                                         padding: 10px; 
                                         border-radius: 5px;">
                                        {document_text}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.info("Bu döküman için içerik bulunamadı.")
                    else:
                        st.error(f"Hata: {response.json().get('detail', 'Bilinmeyen bir hata oluştu.')}")
                except Exception as e:
                    st.error(f"Bağlantı hatası: {str(e)}")
        else:
            st.warning("Lütfen bir arama sorgusu girin.")

# Matematik İşlemleri
elif islem == "Matematik İşlemleri":
    st.header("🔢 Matematik İşlemleri")
    st.subheader("Matematik İşlemi Çözme")
    
    # Kullanım örnekleri
    st.markdown("""
    **Örnek İşlemler:**
    - Basit işlemler: `3 * 4 + 2`
    - Karekök: `sqrt(16) + 5`
    - Parantezli işlemler: `(15 + 3) * 2`
    - Trigonometri: `sin(30) + cos(60)`
    - Logaritma: `log(100) + 5`
    """)
    
    # İşlem girişi
    operation = st.text_input("Matematik işlemini girin:", placeholder="Örnek: 3 * 4 + 2")
    
    if st.button("Çöz"):
        if operation:
            with st.spinner('İşlem çözülüyor...'):
                try:
                    response = requests.post(
                        f"{API_URL}/math/solve",
                        json={"operation": operation}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.balloons()
                        
                        # Sonucu göster
                        st.markdown(f"""
                        <div style="background-color: {'#2D2D2D' if theme == 'Dark' else '#f0f2f6'}; 
                             color: {'#E0E0E0' if theme == 'Dark' else '#1f1f1f'}; 
                             padding: 20px; 
                             margin: 10px 0; 
                             border-radius: 5px; 
                             text-align: center;">
                            <h2 style="margin: 0;">Sonuç: {result['result']}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # İşlem detayları
                        with st.expander("İşlem Detayları"):
                            st.markdown(f"""
                            - **Girilen İşlem:** `{operation}`
                            - **Sayısal Sonuç:** `{result['result']}`
                            """)
                    else:
                        st.error(f"Hata: {response.json().get('detail', 'Bilinmeyen bir hata oluştu.')}")
                except Exception as e:
                    st.error(f"Bağlantı hatası: {str(e)}")
        else:
            st.warning("Lütfen bir matematik işlemi girin.")

# Anahtar Kelime Çıkarma
else:
    st.header("🔑 Anahtar Kelime Çıkarma")
    
    text_input = st.text_area("Metni girin:", height=200)
    num_keywords = st.slider("Anahtar kelime sayısı", min_value=1, max_value=10, value=5)
    
    if st.button("Anahtar Kelimeleri Çıkar"):
        if text_input:
            with st.spinner('Anahtar kelimeler çıkarılıyor...'):
                try:
                    response = requests.post(
                        f"{API_URL}/keywords",
                        json={"text": text_input, "num_keywords": num_keywords}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Cache durumunu kontrol et
                        is_cached = response.headers.get("X-Cache") == "HIT"
                        cache_status = "🔄 Cache'den geldi" if is_cached else "🆕 Yeni sorgu"
                        
                        st.markdown(f"### Anahtar Kelimeler ({cache_status})")
                        
                        # Anahtar kelimeleri kartlar halinde göster
                        for i, keyword in enumerate(result["keywords"]):
                            st.markdown(f"""
                            <div style="background-color: {'#2D2D2D' if theme == 'Dark' else '#f0f2f6'}; 
                                 color: {'#E0E0E0' if theme == 'Dark' else '#1f1f1f'}; 
                                 padding: 15px; 
                                 margin: 10px 0; 
                                 border-radius: 5px; 
                                 text-align: center;">
                                <h3 style="margin: 0;">{keyword}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.info(f"Toplam {result['total_keywords']} anahtar kelime bulundu.")
                    else:
                        st.error(f"Hata: {response.json().get('detail', 'Bilinmeyen bir hata oluştu.')}")
                except Exception as e:
                    st.error(f"Bağlantı hatası: {str(e)}")
        else:
            st.warning("Lütfen bir metin girin.") 