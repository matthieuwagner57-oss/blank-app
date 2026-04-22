import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import base64
import io

st.set_page_config(page_title="Générateur de Tournée", page_icon="🚚", layout="centered")

# --- PARAMÈTRES ---
st.title("🚚 Générateur d'Application de Tournée")
st.markdown("Créez l'application mobile pour les livreurs en 1 clic !")

# Connexion chez OpenAI (ChatGPT)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : La clé OPENAI_API_KEY n'est pas configurée dans les paramètres secrets.")
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

# --- FONCTIONS OPENAI ---
def ask_ai_text(text_data):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_data}
            ]
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def ask_ai_image(img):
    try:
        # On transforme l'image en texte lisible par l'API
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Voici la feuille de tournée en photo :"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                ]}
            ]
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# --- LES 3 ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📸 Photo", "📄 Fichier (PDF/Texte)", "✍️ Manuel"])

with tab1:
    uploaded_image = st.file_uploader("Prenez en photo la feuille de tournée :", type=["jpg", "jpeg", "png"])
    if st.button("🚀 Générer depuis la photo") and uploaded_image:
        with st.spinner("ChatGPT lit la photo..."):
            img = Image.open(uploaded_image)
            html_result, error = ask_ai_image(img)
            
            if html_result:
                # Nettoyage au cas où ChatGPT rajoute des balises
                html_result = html_result.replace("```html", "").replace("```", "")
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

with tab2:
    uploaded_file = st.file_uploader("Uploadez un PDF ou fichier texte :", type=["pdf", "txt"])
    if st.button("🚀 Générer depuis le fichier") and uploaded_file:
        with st.spinner("ChatGPT lit le fichier..."):
            file_text = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    file_text += page.extract_text() + "\n"
            else:
                file_text = str(uploaded_file.read(), "utf-8")
                
            html_result, error = ask_ai_text(file_text)
            
            if html_result:
                html_result = html_result.replace("```html", "").replace("```", "")
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

with tab3:
    manual_text = st.text_area("Collez la liste des adresses ici :", height=200)
    if st.button("🚀 Générer depuis le texte") and manual_text:
        with st.spinner("ChatGPT analyse le texte..."):
            html_result, error = ask_ai_text(manual_text)
            
            if html_result:
                html_result = html_result.replace("```html", "").replace("```", "")
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

st.divider()
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>✨ Créé sur mesure par <b>Matthieu WAGNER</b> pour l'équipe de livraison 🗞️</p>", unsafe_allow_html=True)