import streamlit as st

st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        # On essaie de séparer si l'utilisateur met un ";"
        if ";" in line:
            parts = line.split(";")
            nom = parts[0].strip().upper()
            adr = parts[1].strip().upper()
            consigne = parts[2].strip().upper() if len(parts) > 2 else ""
        else:
            # Si l'utilisateur a juste scanné en vrac, on essaie de séparer
            # Tout ce qui est avant "RUE", "IMP", "SQUARE" est le NOM
            text = line.upper()
            trigger_words = ["RUE", "IMP", "SQU", "AVENUE", "ALLÉE", "PLACE", "RUELLE"]
            nom = text
            adr = ""
            for word in trigger_words:
                if word in text:
                    parts = text.split(word, 1)
                    nom = parts[0].strip()
                    adr = word + parts[1].strip()
                    break
            consigne = ""

        # Détection des arrêts (le "N" du bordereau)
        is_stop = "PAS" in consigne or " NO " in line.upper()
        color = "red" if is_stop else "#1a73e8"
        badge = f'<div style="color:red; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="check{i}" class="toggle-done">
            <label for="check{i}" class="card" style="border-left: 6px solid {color};">
                <div class="info">
                    <div class="nom">{nom}</div>
                    <div class="adr">{adr}</div>
                    {badge}
                </div>
                <div class="actions">
                    <span class="btn-v">VALIDER</span>
                    <a href="{maps_url}" target="_blank" class="btn-m" onclick="event.stopPropagation();">📍</a>
                </div>
            </label>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 10px; margin: 0; }}
            .header {{ background: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #1a73e8; position: sticky; top: 0; z-index: 100; }}
            .btn-top {{ background: #4b5563; color: white; padding: 8px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; border: none; }}
            .btn-reset {{ background: #ef4444; text-decoration: none; display: inline-block; }}
            .card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2); cursor: pointer; }}
            .nom {{ font-size: 14px; font-weight: bold; color: #1a73e8; }}
            .adr {{ font-size: 12px; color: #444; font-weight: 600; }}
            .btn-v {{ background: #f3f4f6; border: 1px solid #ccc; padding: 10px 8px; border-radius: 8px; font-size: 10px; font-weight: bold; min-width: 70px; text-align: center; }}
            .btn-m {{ text-decoration: none; border: 2.5px solid #1a73e8; padding: 8px 12px; border-radius: 8px; font-size: 18px; background: white; }}
            .toggle-done {{ display: none; }}
            .toggle-done:checked + .card {{ background: #d1fae5; opacity: 0.6; }}
            .toggle-done:checked + .card .btn-v {{ background: #22c55e; color: white; border: none; font-size: 0; }}
            .toggle-done:checked + .card .btn-v::after {{ content: "✅ FAIT"; font-size: 10px; }}
            .footer {{ text-align: center; padding: 30px 10px; color: #6b7280; font-size: 13px; font-weight: bold; }}
            #toggle-compact {{ display: none; }}
            #toggle-compact:checked ~ #liste .card {{ padding: 6px 12px; }}
        </style>
    </head>
    <body>
        <input type="checkbox" id="toggle-compact">
        <div class="header">
            <strong style="color:#1a73e8;">🗞️ MA TOURNÉE</strong>
            <div class="controls">
                <label for="toggle-compact" class="btn-top">🔍 VUE</label>
                <a href="" class="btn-top btn-reset">🔄 RESET</a>
            </div>
        </div>
        <div id="liste">{cards_html}</div>
        <div class="footer">🛠️ Créé par Matthieu Wagner</div>
    </body>
    </html>
    """

st.title("🗞️ Système de Tournée - Matthieu Wagner")

st.info("💡 Astuce : Sur iPhone, appuyez deux fois dans la zone ci-dessous et choisissez 'Scanner du texte' pour importer le bordereau en direct.")

data_input = st.text_area("Importez ou collez la liste ici :", height=250)

if st.button("🚀 GÉNÉRER L'APPLICATION"):
    if data_input:
        html = generate_final_html(data_input.split("\n"))
        st.success("✅ Application générée !")
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee_Matthieu.html", "text/html")