import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- JOUR ACTUEL ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
nom_j = jours[datetime.now().weekday()]

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        # Format attendu : NOM ; ADRESSE ; CONSIGNE (optionnel)
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper() if len(parts) > 1 else ""
        consigne = parts[2].strip().upper() if len(parts) > 2 else ""
        
        # On vérifie si c'est un arrêt
        is_stop = "PAS" in consigne
        badge_html = f'<div style="color:#ef4444; font-weight:bold; font-size:12px; margin-top:5px;">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div style="margin-bottom:12px; background:white; border-left:8px solid {'#ef4444' if is_stop else '#1a73e8'}; padding:15px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
            <div style="flex-grow:1;">
                <div style="font-size:16px; font-weight:900; color:#1a73e8;">{nom}</div>
                <div style="font-size:13px; font-weight:600; color:#4b5563;">{adr}</div>
                {badge_html}
                <div onclick="this.innerHTML='✅ LIVRÉ'; this.style.background='#22c55e';" style="margin-top:10px; display:inline-block; padding:6px 12px; background:#1a73e8; color:white; border-radius:15px; font-size:11px; font-weight:bold; cursor:pointer;">VALIDER</div>
            </div>
            <a href="{maps_url}" target="_blank" style="margin-left:10px; background:white; border:2px solid #1a73e8; color:#1a73e8; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:12px;">📍 MAPS</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    </head>
    <body style="font-family: -apple-system, sans-serif; background: #f4f7f9; padding: 10px; margin: 0;">
        <h2 style="color: #1a73e8; text-align: center;">🗞️ TOURNÉE DU {nom_j.upper()}</h2>
        {cards_html}
    </body>
    </html>
    """

st.title("🗞️ Ma Tournée RL")

st.subheader("📝 Liste des clients")
st.info("Colle la liste (NOM ; ADRESSE ; PAS)")
data_input = st.text_area("Données :", height=300)

if st.button("🚀 GÉNÉRER L'APPLI"):
    if data_input:
        lines = data_input.split("\n")
        res_html = generate_final_html(lines)
        st.success("✅ Application prête !")
        st.download_button("📥 TÉLÉCHARGER LE FICHIER", res_html, "MaTournee.html", "text/html")