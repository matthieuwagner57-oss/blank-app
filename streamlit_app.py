import streamlit as st
from google import genai
from PIL import Image
import PyPDF2
import time

st.set_page_config(page_title="Générateur de Tournée", page_icon="🚚", layout="centered")

# --- PARAMÈTRES ---
st.title("🚚 Générateur d'Application de Tournée")
st.markdown("Créez l'application mobile pour les livreurs en 1 clic !")

# Connexion avec le NOUVEAU système Google
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except:
    st.error("Erreur : La clé API n'est pas configurée dans les paramètres secrets.")
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

# --- FONCTION AVEC PATIENCE AUTOMATIQUE ---
def ask_ai(content_data):
    # L'ordinateur va essayer 3 fois maximum
    for tentative in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[system_prompt, content_data]
            )
            return response.text, None
            
        except Exception as e:
            erreur = str(e)
            
            # Si le serveur mondial a un pic de trafic (503)
            if "503" in erreur or "high demand" in erreur:
                if tentative < 2: # S'il reste des essais
                    time.sleep(5) # On patiente 5 secondes
                    continue      # Et on relance la boucle
                else:
                    return None, "Les serveurs mondiaux de Google sont surchargés. Réessayez dans quelques minutes !"
                    
            # Si on clique trop vite
            elif "429" in erreur or "Quota" in erreur:
                return None, "Vitesse limite atteinte. Patientez un peu avant de re-cliquer."
                
            # Autre erreur inconnue
            else:
                return None, erreur

# --- LES 3 ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📸 Photo", "📄 Fichier (PDF/Texte)", "✍️ Manuel"])

# --- ONGLET 1 : PHOTO ---
with tab1:
    uploaded_image = st.file_uploader("Prenez en photo la feuille de tournée :", type=["jpg", "jpeg", "png"])
    if st.button("🚀 Générer depuis la photo") and uploaded_image:
        with st.spinner("L'IA lit la photo... (cela peut prendre quelques secondes si le serveur est occupé)"):
            img = Image.open(uploaded_image)
            html_result, error = ask_ai(img)
            
            if html_result:
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

# --- ONGLET 2 : FICHIER ---
with tab2:
    uploaded_file = st.file_uploader("Uploadez un PDF ou fichier texte :", type=["pdf", "txt"])
    if st.button("🚀 Générer depuis le fichier") and uploaded_file:
        with st.spinner("L'IA lit le fichier..."):
            file_text = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    file_text += page.extract_text() + "\n"
            else:
                file_text = str(uploaded_file.read(), "utf-8")
                
            html_result, error = ask_ai(file_text)
            
            if html_result:
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

# --- ONGLET 3 : MANUEL ---
with tab3:
    manual_text = st.text_area("Collez la liste des adresses ici :", height=200)
    if st.button("🚀 Générer depuis le texte") and manual_text:
        with st.spinner("L'IA analyse le texte..."):
            html_result, error = ask_ai(manual_text)
            
            if html_result:
                st.success("✅ Application générée avec succès !")
                st.download_button(label="📥 Télécharger l'App (Tournee.html)", data=html_result, file_name="Tournee.html", mime="text/html")
            else:
                st.error(f"❌ {error}")

# --- SIGNATURE DU CRÉATEUR ---
st.divider()
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>✨ Créé sur mesure par <b>Matthieu WAGNER</b> pour l'équipe de livraison 🗞️</p>", unsafe_allow_html=True)