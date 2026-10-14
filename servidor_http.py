from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import datetime
import json
import sys

# Lista global para almacenar los registros (en memoria)
REGISTROS = []

# HTML de la plantilla del dashboard
# Usamos %VARIABLE% en lugar de {VARIABLE} para evitar conflictos con el CSS
PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel de User-Agents Capturados</title>
    <meta http-equiv="refresh" content="10">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #1e3c72;
            color: white;
            padding: 30px 40px;
        }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header p { opacity: 0.8; font-size: 14px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2a5298;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .stat-card .label {
            font-size: 12px;
            text-transform: uppercase;
            color: #777;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: 700;
            color: #1e3c72;
        }
        .content { padding: 30px 40px; }
        .content h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #1e3c72;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        th {
            background: #1e3c72;
            color: white;
            padding: 14px;
            text-align: left;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        td {
            padding: 12px 14px;
            border-bottom: 1px solid #eee;
            font-size: 14px;
            vertical-align: top;
        }
        tr:hover { background: #f8f9fa; }
        .ua-text {
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: #2a5298;
            word-break: break-all;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            background: #e8f0fe;
            color: #1e3c72;
        }
        .empty {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        .empty-icon { font-size: 48px; margin-bottom: 15px; }
        .footer {
            padding: 20px 40px;
            background: #f8f9fa;
            font-size: 12px;
            color: #777;
            text-align: center;
            border-top: 1px solid #e0e0e0;
        }
        .refresh-note {
            display: inline-block;
            background: #fff3cd;
            color: #856404;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ Panel de Captura de User-Agents</h1>
            <p>Servidor HTTP OSINT · Se actualiza automáticamente cada 10 segundos</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Peticiones</div>
                <div class="value">%TOTAL%</div>
            </div>
            <div class="stat-card">
                <div class="label">IPs Únicas</div>
                <div class="value">%IPS_UNICAS%</div>
            </div>
            <div class="stat-card">
                <div class="label">Última Captura</div>
                <div class="value" style="font-size: 14px;">%ULTIMA%</div>
            </div>
        </div>
        
        <div class="content">
            <h2>📋 Historial de User-Agents</h2>
            <div class="refresh-note">🔄 Página con auto-refresco cada 10 segundos</div>
            %TABLA%
        </div>
        
        <div class="footer">
            OSINT Arsenal · Servidor activo en el puerto %PUERTO%
        </div>
    </div>
</body>
</html>
"""


class ManejadorUserAgent(BaseHTTPRequestHandler):
    """Manejador HTTP que captura el User-Agent y muestra el panel."""

    PUERTO = 8080  # Se sobreescribe desde iniciar_servidor

    def do_GET(self):
        # --- CAPTURA DEL USER-AGENT ---
        user_agent = self.headers.get('User-Agent', 'Desconocido')
        ip_cliente = self.client_address[0]
        hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ruta = urlparse(self.path).path

        # Guardar en memoria
        REGISTROS.append({
            "hora": hora,
            "ip": ip_cliente,
            "user_agent": user_agent,
            "ruta": ruta
        })

        # Guardar en archivo log
        with open("user_agents.log", "a") as f:
            f.write(f"[{hora}] IP: {ip_cliente} | Ruta: {ruta} | User-Agent: {user_agent}\n")

        print(f"[{hora}] Petición desde {ip_cliente} en {ruta} - User-Agent: {user_agent}")

        # --- RUTAS ---
        if ruta == "/json":
            self._responder_json()
        else:
            self._responder_html(mostrar_todo=(ruta == "/logs"))

    def _responder_json(self):
        """Devuelve los registros en JSON."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(REGISTROS, indent=2, ensure_ascii=False).encode('utf-8'))

    def _responder_html(self, mostrar_todo=False):
        """Genera y sirve el panel HTML."""
        total = len(REGISTROS)
        ips_unicas = len(set(r["ip"] for r in REGISTROS))
        ultima = REGISTROS[-1]["hora"] if REGISTROS else "Sin registros"

        # Filtrar: si no es "mostrar_todo", solo mostramos los últimos 20
        datos_tabla = REGISTROS if mostrar_todo else REGISTROS[-20:]
        datos_tabla = list(reversed(datos_tabla))  # Los más recientes primero

        if datos_tabla:
            filas = ""
            for i, r in enumerate(datos_tabla, 1):
                filas += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{r['hora']}</td>
                        <td><span class="badge">{r['ip']}</span></td>
                        <td><code>{r['ruta']}</code></td>
                        <td class="ua-text">{r['user_agent']}</td>
                    </tr>
                """
            tabla = f"""
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Fecha y Hora</th>
                            <th>IP Origen</th>
                            <th>Ruta</th>
                            <th>User-Agent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            """
        else:
            tabla = """
                <div class="empty">
                    <div class="empty-icon">📭</div>
                    <p>Aún no se han capturado peticiones.</p>
                    <p style="font-size:13px;margin-top:10px;">Abre otra terminal y ejecuta:</p>
                    <code style="display:inline-block;margin-top:10px;padding:8px 14px;background:#f0f0f0;border-radius:6px;font-size:13px;">
                        curl -A "MiNavegador/1.0" http://localhost:8080
                    </code>
                </div>
            """

        # Usamos .replace() para evitar el error con las llaves del CSS
        html = PLANTILLA_HTML.replace("%TOTAL%", str(total)) \
                             .replace("%IPS_UNICAS%", str(ips_unicas)) \
                             .replace("%ULTIMA%", ultima) \
                             .replace("%TABLA%", tabla) \
                             .replace("%PUERTO%", str(self.PUERTO))

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        """Silencia el log por defecto para no duplicar salida."""
        pass


def iniciar_servidor(puerto=8080):
    """Inicia el servidor HTTP en el puerto especificado."""
    ManejadorUserAgent.PUERTO = puerto
    servidor = HTTPServer(('0.0.0.0', puerto), ManejadorUserAgent)

    print(f"\n{'='*60}")
    print(f" 🕵️  SERVIDOR HTTP OSINT ACTIVO")
    print(f"{'='*60}")
    print(f" [+] URL del panel:     http://localhost:{puerto}/")
    print(f" [+] Ver todos los logs: http://localhost:{puerto}/logs")
    print(f" [+] Datos en JSON:      http://localhost:{puerto}/json")
    print(f" [+] Archivo de log:     user_agents.log")
    print(f"{'='*60}")
    print(f" [*] Presiona Ctrl+C para detenerlo.\n")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor detenido.")
        servidor.server_close()


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
    iniciar_servidor(puerto)
