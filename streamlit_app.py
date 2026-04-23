import streamlit as st
import pdfplumber
import re

st.set_page_config(page_title="Système RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f5;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 15px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #1a73e8 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION D'EXTRACTION PDF ---
def extraire_pdf(file):
    lignes = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for l in text.split('\n'):
                    if any(k in l.upper() for k in ["RUE", "AV", "IMP", "PL", "BD"]):
                        lignes.append(l.strip())
    return lignes

# --- INTERFACE ---
st.title("🗞️ Scanner RL - Multi-Outils")
st.caption("Développement : Matthieu Wagner")

tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA (CONSEILLÉ)", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

# --- ONGLET 1 : IA EXTERNE ---
with tab1:
    st.write("### 🧠 Extraction par IA Haute Précision")
    st.info("La meilleure méthode pour éviter les décalages de colonnes.")
    st.markdown("**Copiez ce prompt anti-erreur :**")
    st.code("Analyse ce tableau. Extrait : NOM ; ADRESSE. Garde bien l'alignement horizontal de chaque ligne. Ignore les codes abonnés.")
    col1, col2 = st.columns(2)
    with col1: st.link_button("Ouvrir Claude", "https://claude.ai")
    with col2: st.link_button("Ouvrir Gemini", "https://gemini.google.com")

# --- ONGLET 2 : PHOTO ---
with tab2:
    st.write("### 📸 Scan Photo Direct")
    photo = st.file_uploader("Prendre une photo du bordereau", type=["jpg", "jpeg", "png"])
    if photo:
        st.image(photo, caption="Aperçu du bordereau", use_container_width=True)
        st.warning("⚠️ L'analyse photo directe est limitée sur mobile. Utilisez le 'Texte en direct' de votre iPhone/Android pour copier le texte vers l'onglet GÉNÉRATEUR.")

# --- ONGLET 3 : PDF ---
with tab3:
    st.write("### 📄 Extraction PDF Directe")
    file_pdf = st.file_uploader("Choisir le fichier PDF officiel", type="pdf")
    if file_pdf:
        if st.button("🔍 Analyser le PDF"):
            res = extraire_pdf(file_pdf)
            if res:
                st.success(f"{len(res)} lignes détectées")
                st.text_area("Texte extrait (Ajoutez les ';' entre nom et adresse) :", value="\n".join(res), height=200)

# --- ONGLET 4 : GÉNÉRATEUR ---
with tab4:
    st.write("### 🚀 Création de l'Appli Mobile")
    saisie = st.text_area("Collez votre liste finale (NOM ; ADRESSE) :", height=300, placeholder="Ex: BOUR BERNADETTE ; 38 RUE SAINT ANTOINE")
    
    if st.button("📱 GÉNÉRER MA TOURNÉE", use_container_width=True):
        if ";" in saisie:
            # Création du HTML (Simplifiée pour l'exemple)
            cards = ""
            for line in saisie.split('\n'):
                if ";" in line:
                    n, a = line.split(";", 1)
                    cards += f"<div style='border-left:8px solid #1a73e8; background:white; padding:10px; margin-bottom:10px; border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;'><div><b>{n.strip().upper()}</b><br>{a.strip().upper()}</div><a href='https://www.google.com/maps/search/?api=1&query={a.replace(' ','+')}' style='text-decoration:none; font-size:20px;'>📍</a></div>"
            
            full_html = f"<html><body style='font-family:sans-serif; background:#f0f2f5; padding:10px;'>{cards}</body></html>"
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", full_html, "Tournee.html", "text/html")
        else:
            st.error("Format requis : NOM ; ADRESSE")