import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import base64
import io
import re

st.set_page_config(page_title="Générateur de Tournée", page_icon="🚚", layout="centered")

# --- PARAMÈTRES ---
st.title("🚚 Générateur d'Application de Tournée")
st.markdown("Créez l'application mobile pour les livreurs en 1 clic !")

# Connexion chez OpenAI
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : La clé OPENAI_API_KEY n'est pas configurée.")
    st.stop()

# --- LE PROMPT (AMÉLIORÉ POUR LE DESIGN) ---
system_prompt = """
Tu es un expert développeur web. Tu dois générer un fichier HTML unique, moderne et élégant pour une tournée de livraison.
DESIGN REQUIS :
1. Utilise un fond gris très clair (#f4f4f9) et des cartes blanches avec des coins arrondis et une ombre légère.
2. Chaque carte doit contenir : L'adresse en gras, un bouton bleu "📍 Google Maps", et les consignes en rouge.
3. INTERACTION : Quand on coche la case d'une carte, toute la carte doit devenir grise à 50% et le texte doit être barré.
4. Ajoute un bandeau fixe en haut avec le titre "Ma Tournée".
5. Ne mets AUCUN texte avant ou après le code <html>.
"""

# --- FONCTION DE NETTOYAGE ---
def clean_html(raw_html):
    # Cette fonction enlève les ```html et autres textes inutiles que l'IA peut rajouter
    cleaned = re.sub(r'```html', '', raw_html)
    cleaned = re.sub(r'```', '', cleaned)
    return cleaned.strip()

def ask_ai_text(text_data):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_data}
            ]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e:
        return None, str(e)

def ask_ai_image(img):
    try:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Génère l'app de tournée pour cette photo :"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                ]}
            ]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e:
        return None, str(e)

# --- INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📸 Photo", "📄 Fichier", "✍️ Manuel"])

with tab1:
    uploaded_image = st.file_uploader("Photo :", type=["jpg", "jpeg", "png"])
    if st.button("🚀 Générer (Photo)") and uploaded_image:
        with st.spinner("Analyse..."):
            html_result, error = ask_ai_image(Image.open(uploaded_image))
            if html_result:
                st.success("Prêt !")
                st.download_button("📥 Télécharger l'App", html_result, "Tournee.html", "text/html")

with tab2:
    uploaded_file = st.file_uploader("PDF/Texte :", type=["pdf", "txt"])
    if st.button("🚀 Générer (Fichier)") and uploaded_file:
        with st.spinner("Analyse..."):
            text = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                for p in reader.pages: text += p.extract_text()
            else:
                text = uploaded_file.read().decode()
            html_result, error = ask_ai_text(text)
            if html_result:
                st.download_button("📥 Télécharger l'App", html_result, "Tournee.html", "text/html")

with tab3:
    manual_text = st.text_area("Adresses :")
    if st.button("🚀 Générer (Manuel)") and manual_text:
        html_result, error = ask_ai_text(manual_text)
        if html_result:
            st.download_button("📥 Télécharger l'App", html_result, "Tournee.html", "text/html")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>✨ Par Matthieu WAGNER</p>", unsafe_allow_html=True)