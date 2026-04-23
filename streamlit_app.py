import streamlit as st
import re

st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

def generate_final_app(data_input):
    cards_html = ""
    lines = data_input.strip().split('\n')
    
    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        if not line_upper: continue
        
        # 1. FILTRE : On ignore ce qui n'est pas une adresse (titres, dates...)
        if not any(k in line_upper for k in ["RUE", "AVENUE", "AV ", "IMP", "PL ", "SQ", "BD", "ROUTE", "CHEMIN"]):
            continue

        # 2. EXTRACTION NOM / ADRESSE
        if ";" in line:
            parts = line.split(";")
            nom = parts[0].strip().upper()
            adr = parts[1].strip().upper()
            # On récupère le reste de la ligne s'il y a plus de 2 colonnes
            info_supp = " ".join(parts[2:]).strip().upper() if len(parts) > 2 else ""
        else:
            match = re.search(r'(\d+)', line)
            if match:
                nom = line[:match.start()].strip().upper()
                adr = line[match.start():].strip().upper()
                info_supp = ""
            else:
                nom = "CLIENT"
                adr = line.strip().upper()
                info_supp = ""

        # 3. DÉTECTION CONDITIONNELLE DES ARRÊTS
        # On ne met l'alerte QUE si on voit clairement un indicateur d'arrêt
        # On check dans le nom, l'adresse ET les infos supp
        full_line_check = f"{nom} {adr} {info_supp}"
        is_stop = any(x in full_line_check for x in ["PAS DE JOURNAL", "PAS ", "SANS J", "STOP", "VACANCES"])
        
        # Gestion de l'affichage
        if is_stop:
            color = "#ef4444" # Rouge pour alerte
            badge = '<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ PAS DE JOURNAL</div>'
            opacity = "0.7"
        else:
            color = "#1a73e8" # Bleu standard
            badge = ""
            opacity = "1"
        
        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}"
        
        cards_html += f"""
        <div style="background:white; margin-bottom:12px; padding:15px; border-radius:15px; border-left:10px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,0.1); opacity:{opacity};">
            <div style="flex:1;">
                <div style="color:#1a73e8; font-weight:bold; font-size:16px;">{nom}</div>
                <div style="font-size:13px; color:#444; margin-top:4px;">{adr}</div>
                {badge}
            </div>
            <a href="{maps_url}" target="_blank" style="text-decoration:none; background:#f0f7ff; padding:12px; border-radius:12px; border:1.5px solid #1a73e8; font-size:20px;">📍</a>
        </div>"""
    
    return f"<html><body style='font-family:sans-serif; background:#f8f9fa; padding:15px;'><h2 style='color:#1a73e8;'>🗞️ MA TOURNÉE</h2>{cards_html}</body></html>"

# --- INTERFACE ---
st.title("🗞️ Scanner RL")
st.caption("Version Adaptative - Matthieu Wagner")

tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

# On garde la même structure d'onglets pour la cohérence
with tab4:
    st.write("### 🚀 Création de l'Appli")
    st.info("Le système s'adapte : il détecte les 'PAS DE JOURNAL' si l'info est présente, sinon il crée une liste simple.")
    
    input_txt = st.text_area("Collez votre liste ici :", height=300, placeholder="NOM ; ADRESSE")
    
    if st.button("📱 GÉNÉRER MA TOURNÉE", use_container_width=True):
        if input_txt:
            app_html = generate_final_app(input_txt)
            st.success("✅ Application générée !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", app_html, "Tournee.html", "text/html")