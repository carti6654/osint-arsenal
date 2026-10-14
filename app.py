#!/usr/bin/env python3
from flask import Flask, request
import datetime
import enumeracion  # <-- CAMBIO CLAVE: ya no usa "modulos."

app = Flask(__name__)

CSS_COMUN = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
       min-height: 100vh; color: #e0e0e0; padding: 30px 20px; }
.nav { max-width: 1200px; margin: 0 auto 20px; background: rgba(0,0,0,0.4); border-radius: 10px;
       padding: 15px 25px; display: flex; gap: 20px; align-items: center; border: 1px solid rgba(255,255,255,0.1); }
.nav a { color: #4fc3f7; text-decoration: none; font-weight: 600; padding: 8px 15px; border-radius: 6px; }
.nav a:hover, .nav a.active { background: rgba(79, 195, 247, 0.2); color: #fff; }
.nav .logo { font-size: 18px; color: #fff; font-weight: 700; margin-right: auto; }
.container { max-width: 1200px; margin: 0 auto; background: rgba(20, 30, 45, 0.85); border-radius: 12px;
             padding: 30px; border: 1px solid rgba(255,255,255,0.1); }
h1 { color: #4fc3f7; margin-bottom: 20px; }
h2 { color: #81d4fa; margin: 25px 0 15px; border-bottom: 1px solid rgba(79,195,247,0.3); padding-bottom: 8px; }
form { display: flex; gap: 10px; margin-bottom: 25px; }
input[type=text] { flex: 1; padding: 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(79,195,247,0.4);
                   border-radius: 8px; color: #fff; font-size: 15px; }
button { padding: 12px 24px; background: linear-gradient(135deg, #4fc3f7, #0288d1); color: #fff;
         border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; background: rgba(0,0,0,0.2); border-radius: 8px; }
th { background: rgba(79,195,247,0.15); padding: 12px; text-align: left; color: #4fc3f7; font-size: 13px; text-transform: uppercase; }
td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px; }
.badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px;
         font-weight: 600; background: rgba(79,195,247,0.2); color: #4fc3f7; margin: 2px; }
.badge.port { background: rgba(76,175,80,0.2); color: #4caf50; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }
.stat { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; border-left: 4px solid #4fc3f7; }
.stat .label { font-size: 12px; color: #90a4ae; text-transform: uppercase; }
.stat .value { font-size: 24px; color: #fff; font-weight: 700; margin-top: 5px; }
.list-box { background: rgba(0,0,0,0.2); border-radius: 8px; padding: 15px; max-height: 300px; overflow-y: auto; }
.list-box ul { list-style: none; }
.list-box li { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: monospace; font-size: 13px; }
.error { background: rgba(239,83,80,0.2); border-left: 4px solid #ef5350; padding: 15px; border-radius: 8px; color: #ef5350; margin: 15px 0; }
</style>
"""

def nav(activo=""):
    def cls(name): return 'class="active"' if activo == name else ''
    return f"""<div class="nav">
        <span class="logo">🕵️ OSINT Arsenal</span>
        <a href="/" {cls('home')}>Inicio</a>
        <a href="/enum" {cls('enum')}>Enumeración</a>
    </div>"""

@app.route("/")
def home():
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>OSINT</title>{CSS_COMUN}</head><body>
    {nav('home')}
    <div class="container">
        <h1>🕵️ Panel de Control OSINT</h1>
        <p>Selecciona una herramienta para comenzar:</p>
        <div style="margin-top:30px;">
            <a href="/enum" style="display:inline-block; padding:15px 30px; background:rgba(79,195,247,0.1); border:1px solid #4fc3f7; border-radius:8px; color:#4fc3f7; text-decoration:none; font-weight:600;">🌐 Ir a Enumeración de Dominios</a>
        </div>
    </div></body></html>"""

@app.route("/enum", methods=["GET", "POST"])
def enum_view():
    datos_pasivos = None
    datos_activos = None
    target = ""
    error = None

    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if target:
            try:
                datos_pasivos = enumeracion.pasiva_completa(target)
                datos_activos = enumeracion.activa(target)
            except Exception as e:
                error = f"Error al ejecutar la enumeración: {e}"

    resultados_html = ""
    if datos_pasivos and datos_activos:
        stats = f"""
        <div class="stats">
            <div class="stat"><div class="label">IP Resuelta</div><div class="value">{datos_pasivos['ip']}</div></div>
            <div class="stat"><div class="label">Subdominios</div><div class="value">{len(datos_pasivos['subdominios'])}</div></div>
            <div class="stat"><div class="label">Puertos Abiertos</div><div class="value">{len(datos_activos['puertos'])}</div></div>
        </div>
        """

        dns_html = "<table><thead><tr><th>Tipo</th><th>Valores</th></tr></thead><tbody>"
        for tipo, valores in datos_pasivos["registros"].items():
            if valores:
                dns_html += f"<tr><td><b>{tipo}</b></td><td>{'<br>'.join(valores)}</td></tr>"
            else:
                dns_html += f"<tr><td><b>{tipo}</b></td><td style='color:#ef5350;'>No encontrado</td></tr>"
        dns_html += "</tbody></table>"

        whois_html = "<table><thead><tr><th>Campo</th><th>Valor</th></tr></thead><tbody>"
        for campo, valor in datos_pasivos["whois"].items():
            whois_html += f"<tr><td><b>{campo}</b></td><td>{valor}</td></tr>"
        whois_html += "</tbody></table>"

        if datos_pasivos["subdominios"]:
            subs_lista = "".join(f"<li>{sub}</li>" for sub in datos_pasivos["subdominios"])
            subdominios_html = f"<div class='list-box'><ul>{subs_lista}</ul></div>"
        else:
            subdominios_html = f"<div class='error'>⚠️ {datos_pasivos.get('error_crtsh', 'No se encontraron subdominios.')}</div>"

        if datos_activos["puertos"]:
            puertos_html = "".join(f"<span class='badge port'>Puerto {p}</span>" for p in datos_activos["puertos"])
        else:
            puertos_html = "<p style='color:#ffb74d;'>No se encontraron puertos comunes abiertos.</p>"

        resultados_html = f"""
        <h2>📊 Resultados para: <code>{target}</code></h2>
        {stats}
        <h2>🌐 1. Información DNS y WHOIS (Pasivo)</h2>
        <h3 style="color:#81d4fa;margin:15px 0 10px;">Registros DNS</h3>
        {dns_html}
        <h3 style="color:#81d4fa;margin:15px 0 10px;">Información WHOIS</h3>
        {whois_html}
        <h2>🔍 2. Subdominios Encontrados</h2>
        {subdominios_html}
        <h2>⚔️ 3. Escaneo de Puertos (Activo)</h2>
        <p><b>IP Escaneada:</b> {datos_activos['ip']}</p>
        <div style="margin-top:15px;">{puertos_html}</div>
        """

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Enumeración</title>{CSS_COMUN}</head><body>
    {nav('enum')}
    <div class="container">
        <h1>🌐 Enumeración de Dominios</h1>
        <form method="POST">
            <input type="text" name="target" placeholder="ej. bankia.es" value="{target}" required>
            <button type="submit">🔍 Enumerar</button>
        </form>
        {f'<div class="error">{error}</div>' if error else ''}
        {resultados_html if resultados_html else '<p style="color:#90a4ae;text-align:center;padding:40px;">Introduce un dominio para comenzar el análisis.</p>'}
    </div></body></html>"""

if __name__ == "__main__":
    print("🕵️ Servidor web OSINT iniciado en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
