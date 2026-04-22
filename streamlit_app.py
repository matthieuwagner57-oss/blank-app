import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2

st.set_page_config(page_title="Générateur de Tournée", page_icon="🚚", layout="centered")

# --- PARAMÈTRES ---
st.title("🚚 Générateur d'Application de Tournée")
st.markdown("Créez l'application mobile pour les livreurs en 1 clic !")

# On va chercher la clé API cachée dans les secrets de Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Correction ici : utilisation de la version "latest" pour éviter l'erreur
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    st.error("Erreur : La clé API n'est pas configurée dans les paramètres (Secrets) du site.")
    st.stop()

# --- LE PROMPT SECRET ---
system_prompt = """
Tu es un expert développeur. Ton but est de lire les données fournies (photo, texte ou PDF) et de générer un fichier HTML unique pour une tournée de livraison.
REGLES OBLIGATOIRES :
1. AUCUN JAVASCRIPT pour cocher les cases. Utilise un <input type="checkbox" class="hidden-checkbox"> et du CSS pour griser/barrer la carte quand elle est cochée.
2. Ajoute un bouton "<input type='reset' value='🔄 TOUT DÉCOCHER'>" dans la balise <form>.
3. Ajoute une case "🔍 Vue Compacte" qui réduit la taille des cartes en CSS.
4. Les adresses doivent être des liens Google Maps : https://www.google.com/maps/search/?api=1&query={adresse}.
5. Si des consignes spéciales sont détectées (ex: 'Pas le lundi'), mets-les en rouge vif sur la carte.
6. Range les adresses dans un ordre géographique logique si elles sont en vrac, sinon respecte l'ordre fourni.
7. Ne renvoie QUE le code HTML complet, rien d'autre, sans les balises ```html au début ou à la fin.
"""

# --- LES 3 ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📸 Photo", "📄 Fichier (PDF/Texte)", "✍️ Manuel"])

# --- ONGLET 1 : PHOTO ---
with tab1:
    uploaded_image = st.file_uploader("Prenez en photo la feuille de tournée :", type=["jpg", "jpeg", "png"])
    if st.button("🚀 Générer depuis la photo") and uploaded_image:
        with st.spinner("L'IA lit la photo et crée l'application..."):
            img = Image.open(uploaded_image)
            response = model.generate_content([system_prompt, img])
            html_result = response.text
            
            st.success("✅ Application générée avec succès !")
            st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")

# --- ONGLET 2 : FICHIER ---
with tab2:
    uploaded_file = st.file_uploader("Uploadez un PDF ou fichier texte :", type=["pdf", "txt"])
    if st.button("🚀 Générer depuis le fichier") and uploaded_file:
        with st.spinner("L'IA lit le fichier et crée l'application..."):
            file_text = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    file_text += page.extract_text() + "\n"
            else:
                file_text = str(uploaded_file.read(), "utf-8")
                
            response = model.generate_content([system_prompt, file_text])
            html_result = response.text
            
            st.success("✅ Application générée avec succès !")
            st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")

# --- ONGLET 3 : MANUEL ---
with tab3:
    manual_text = st.text_area("Collez la liste des adresses ici :", height=200)
    if st.button("🚀 Générer depuis le texte") and manual_text:
        with st.spinner("L'IA analyse le texte et crée l'application..."):
            response = model.generate_content([system_prompt, manual_text])
            html_result = response.text
            
            st.success("✅ Application générée avec succès !")
            st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")

# --- SIGNATURE DU CRÉATEUR ---
st.divider()
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>✨ Créé sur mesure par <b>Matthieu WAGNER</b> pour l'équipe de livraison 🗞️</p>", unsafe_allow_html=True)