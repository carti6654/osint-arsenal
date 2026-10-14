import socket
import requests
import dns.resolver
import whois
import datetime
import os

def pasiva_completa(dominio):
    """Enumeración pasiva completa. Devuelve un diccionario con los datos."""
    resultado = {
        "dominio": dominio,
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": None,
        "registros": {},
        "whois": {},
        "subdominios": [],
        "error_crtsh": None
    }

    # 1. IP
    try:
        resultado["ip"] = socket.gethostbyname(dominio)
    except Exception as e:
        resultado["ip"] = f"Error: {e}"

    # 2. Registros DNS
    tipos = {"NS": "Name Servers", "MX": "Servidores de Correo", "TXT": "Texto/SPF", "CNAME": "Alias"}
    for tipo, nombre in tipos.items():
        try:
            respuestas = dns.resolver.resolve(dominio, tipo)
            resultado["registros"][nombre] = [r.to_text() for r in respuestas]
        except Exception:
            resultado["registros"][nombre] = []

    # 3. WHOIS
    try:
        w = whois.whois(dominio)
        resultado["whois"] = {
            "Registrador": w.registrar or "No disponible",
            "Creación": str(w.creation_date) if w.creation_date else "No disponible",
            "Expiración": str(w.expiration_date) if w.expiration_date else "No disponible",
            "Servidores DNS": str(w.name_servers) if w.name_servers else "No disponible",
            "Organización": w.org or "No disponible"
        }
    except Exception as e:
        resultado["whois"] = {"Error": str(e)}

    # 4. Subdominios (crt.sh)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        url = f"https://crt.sh/?q=%25.{dominio}&output=json"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            datos = r.json()
            resultado["subdominios"] = sorted(set(item['name_value'] for item in datos))
        else:
            resultado["error_crtsh"] = f"crt.sh respondió con código {r.status_code}"
    except requests.exceptions.Timeout:
        resultado["error_crtsh"] = "crt.sh tardó demasiado (Timeout). Servicio saturado."
    except Exception as e:
        resultado["error_crtsh"] = f"Error de conexión: {e}"

    return resultado


def activa(dominio):
    """Enumeración activa. Devuelve un diccionario con los puertos abiertos."""
    resultado = {
        "dominio": dominio,
        "ip": None,
        "puertos": [],
        "error": None
    }
    puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]

    try:
        resultado["ip"] = socket.gethostbyname(dominio)
        for puerto in puertos_comunes:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((resultado["ip"], puerto)) == 0:
                resultado["puertos"].append(puerto)
            sock.close()
    except Exception as e:
        resultado["error"] = str(e)

    return resultado


# --- Bloque de prueba (opcional) ---
if __name__ == "__main__":
    d = input("Dominio a enumerar: ")
    print("\n=== PASIVA ===")
    print(pasiva_completa(d))
    print("\n=== ACTIVA ===")
    print(activa(d))
