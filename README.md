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
        badge = f'<div style="color:red; font-weight:bold; font-size:11px;">⚠️ PAS DE JOURNAL</div>' if is_stop else ""
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div class="card" id="card{i}" style="border-left: 8px solid {'red' if is_stop else '#1a73e8'};">
            <div style="flex: 1;">
                <div class="nom">{nom}</div>
                <div class="adr">{adr}</div>
                {badge}
            </div>
            <div class="btns">
                <button onclick="valider({i})" id="btn{i}">VALIDER</button>
                <a href="{maps_url}" target="_blank">📍</a>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: sans-serif; background: #eee; padding: 10px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-bottom: 3px solid #1a73e8; }}
            
            .card {{ background: white; margin-bottom: 10px; padding: 12px; border-radius: 10px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
            .nom {{ font-size: 14px; font-weight: bold; color: #1a73e8; }}
            .adr {{ font-size: 12px; color: #444; }}
            
            .btns {{ display: flex; align-items: center; gap: 5px; margin-left: 10px; }}
            
            button {{ background: #f3f4f6; border: 1px solid #aaa; padding: 12px 8px; border-radius: 8px; font-weight: bold; font-size: 10px; cursor: pointer; min-width: 70px; }}
            a {{ text-decoration: none; background: white; border: 2px solid #1a73e8; padding: 8px 10px; border-radius: 8px; font-size: 18px; display: inline-block; }}
            
            /* Mode Validé */
            .fait {{ background: #d1fae5 !important; opacity: 0.7; }}
            .fait button {{ background: #22c55e !important; color: white; border: none; }}
            
            /* Mode Compact */
            .compact .card {{ padding: 5px 10px; margin-bottom: 4px; }}
            .compact .nom {{ font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <strong>🗞️ MA TOURNÉE</strong>
            <div>
                <button onclick="document.body.classList.toggle('compact')" style="background:#4b5563; color:white;">🔍 VUE</button>
                <button onclick="window.location.reload()" style="background:red; color:white;">🔄 RESET</button>
            </div>
        </div>
        
        <div id="liste">{cards_html}</div>

        <script>
            function valider(id) {{
                var card = document.getElementById('card' + id);
                var btn = document.getElementById('btn' + id);
                if (card.classList.contains('fait')) {{
                    card.classList.remove('fait');
                    btn.innerText = 'VALIDER';
                }} else {{
                    card.classList.add('fait');
                    btn.innerText = '✅ FAIT';
                }}
            }}
        </script>
    </body>
    </html>
    """

st.title("🗞️ Configurateur (Dernier essai)")
data = st.text_area("Liste des clients (NOM ; ADRESSE ; OPTION) :", height=300)

if st.button("🚀 GÉNÉRER"):
    if data:
        html = generate_final_html(data.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")