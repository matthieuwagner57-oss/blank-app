import streamlit as st

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip() or ";" not in line: continue
        
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        consigne = parts[2].strip().upper() if len(parts) > 2 else ""
        
        is_stop = "PAS" in consigne
        color = "red" if is_stop else "#1a73e8"
        badge = f'<div class="badge-stop">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        
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
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 10px; margin: 0; display: flex; flex-direction: column; min-height: 100vh; }}
            
            /* INTERRUPTEURS INVISIBLES */
            .toggle-done, #toggle-compact {{ display: none; }}
            
            /* HEADER */
            .header {{ background: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #1a73e8; position: sticky; top: 0; z-index: 100; }}
            .controls {{ display: flex; gap: 8px; }}
            
            /* BOUTONS DU HAUT */
            .btn-top {{ background: #4b5563; color: white; padding: 8px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; border: none; }}
            .btn-reset {{ background: #ef4444; text-decoration: none; display: inline-block; }}

            /* LISTE ET CARTES */
            #liste {{ flex: 1; }}
            .card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2); cursor: pointer; }}
            .nom {{ font-size: 14px; font-weight: bold; color: #1a73e8; }}
            .adr {{ font-size: 12px; color: #444; font-weight: 600; }}
            .badge-stop {{ color: red; font-weight: bold; font-size: 11px; margin-top: 4px; }}
            
            .actions {{ display: flex; align-items: center; gap: 10px; }}
            .btn-v {{ background: #f3f4f6; border: 1px solid #ccc; padding: 10px 8px; border-radius: 8px; font-size: 10px; font-weight: bold; min-width: 70px; text-align: center; }}
            .btn-m {{ text-decoration: none; border: 2.5px solid #1a73e8; padding: 8px 12px; border-radius: 8px; font-size: 18px; background: white; }}
            
            /* LOGIQUE INTERACTIVE (SANS JS) */
            .toggle-done:checked + .card {{ background: #d1fae5; opacity: 0.6; }}
            .toggle-done:checked + .card .btn-v {{ background: #22c55e; color: white; border: none; font-size: 0; }}
            .toggle-done:checked + .card .btn-v::after {{ content: "✅ FAIT"; font-size: 10px; }}

            /* MODE COMPACT */
            #toggle-compact:checked ~ #liste .card {{ padding: 6px 12px; margin-bottom: 4px; }}
            #toggle-compact:checked ~ #liste .nom {{ font-size: 12px; }}
            #toggle-compact:checked ~ #liste .adr {{ font-size: 10px; }}
            #toggle-compact:checked ~ .header label[for="toggle-compact"] {{ background: #1a73e8; }}

            /* FOOTER / SIGNATURE */
            .footer {{ text-align: center; padding: 20px 10px; color: #9ca3af; font-size: 12px; font-style: italic; }}
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

        <div id="liste">
            {cards_html}
        </div>

        <div class="footer">
            Créé par Matthieu Wagner
        </div>
    </body>
    </html>
    """

st.title("🗞️ Scanner RL - Final")
data = st.text_area("Colle la liste (NOM ; ADRESSE ; OPTION) :", height=300)

if st.button("🚀 GÉNÉRER L'APPLI"):
    if data:
        html = generate_final_html(data.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee_RL.html", "text/html")