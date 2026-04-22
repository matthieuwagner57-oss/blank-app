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
        badge = f'<div style="color:red; font-weight:bold; font-size:11px;">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        color = "red" if is_stop else "#1a73e8"
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        # Structure de ligne forcée par tableau pour éviter que Maps ne saute en dessous
        cards_html += f"""
        <div id="row{i}" style="background:white; margin-bottom:6px; padding:10px; border-radius:8px; border-left:6px solid {color}; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="vertical-align:middle;">
                        <div style="font-size:14px; font-weight:800; color:#1a73e8;">{nom}</div>
                        <div style="font-size:12px; color:#444; font-weight:600;">{adr}</div>
                        {badge}
                    </td>
                    <td style="width:110px; text-align:right; white-space:nowrap; vertical-align:middle;">
                        <button onclick="var r=document.getElementById('row{i}'); if(r.style.opacity=='0.5'){{r.style.opacity='1'; r.style.background='white'; this.innerHTML='VALIDER'; this.style.background='#eee';}}else{{r.style.opacity='0.5'; r.style.background='#d1fae5'; this.innerHTML='✅ FAIT'; this.style.background='#22c55e';}}" 
                                style="background:#eee; border:1px solid #ccc; padding:10px 5px; border-radius:6px; font-size:10px; font-weight:bold; cursor:pointer; width:70px;">VALIDER</button>
                        <a href="{maps_url}" target="_blank" style="text-decoration:none; border:2px solid #1a73e8; color:#1a73e8; padding:8px; border-radius:6px; font-size:16px; background:white; display:inline-block; margin-left:5px;">📍</a>
                    </td>
                </tr>
            </table>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    </head>
    <body style="font-family:sans-serif; background:#f0f2f5; padding:10px; margin:0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; position:sticky; top:0; background:#f0f2f5; padding:10px 0; z-index:1000;">
            <b style="color:#1a73e8; font-size:18px;">🗞️ MA TOURNÉE</b>
            <div style="display:flex; gap:5px;">
                <button onclick="var s=document.getElementById('L').style; s.transformOrigin='top left'; if(s.transform=='scale(0.8)'){{s.transform='scale(1)';}}else{{s.transform='scale(0.8)';}}" style="background:#4b5563; color:white; border:none; padding:8px 10px; border-radius:6px; font-size:11px; font-weight:bold;">🔍 VUE</button>
                <button onclick="window.location.reload()" style="background:#ef4444; color:white; border:none; padding:8px 10px; border-radius:6px; font-size:11px; font-weight:bold;">🔄 RESET</button>
            </div>
        </div>
        <div id="L">{cards_html}</div>
    </body>
    </html>
    """

st.title("🗞️ Scanner RL - Final")
data = st.text_area("Colle ta liste NOM ; ADRESSE ; OPTION", height=300)

if st.button("🚀 GÉNÉRER L'APPLI"):
    if data:
        html = generate_final_html(data.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")