import requests
import sys

def obtener_cabeceras_seguridad(url):
    """Realiza una petición HTTP y extrae las cabeceras de seguridad con formato de tabla."""
    # Si la URL no empieza por http, se lo añadimos
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n[*] Analizando cabeceras de seguridad para: {url}")
    
    cabeceras_criticas = {
        "Strict-Transport-Security": "ALTA",
        "Content-Security-Policy": "ALTA",
        "X-Frame-Options": "MEDIA",
        "X-Content-Type-Options": "MEDIA",
        "Referrer-Policy": "BAJA",
        "Permissions-Policy": "BAJA"
    }
    
    try:
        response = requests.get(url, timeout=10)
        print(f"[+] Código de estado: {response.status_code}")
        print(f"[+] Servidor: {response.headers.get('Server', 'No revelado')}\n")
        
        print("=" * 60)
        print(f"{'CABECERA':<30} | {'ESTADO':<10} | {'CRITICIDAD'}")
        print("=" * 60)
        
        encontradas = 0
        faltantes_criticas = []
        
        for header, criticidad in cabeceras_criticas.items():
            valor = response.headers.get(header)
            if valor:
                print(f"{header:<30} | {'[✓] OK':<10} | {criticidad}")
                encontradas += 1
            else:
                print(f"{header:<30} | {'[X] FALTA':<10} | {criticidad}")
                if criticidad == "ALTA":
                    faltantes_criticas.append(header)
        
        print("=" * 60)
        print(f"\n[+] Resumen: {encontradas}/{len(cabeceras_criticas)} cabeceras presentes.")
        
        if faltantes_criticas:
            print("\n[!] RECOMENDACIONES CRÍTICAS:")
            for falta in faltantes_criticas:
                print(f"  - Implementar: {falta}")
        else:
            print("\n[✓] ¡Excelente! Todas las cabeceras críticas están presentes.")
            
        return response.headers
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Error al conectar con {url}: {e}")
        return {}

# --- BLOQUE DE EJECUCIÓN POR COMANDOS ---
if __name__ == "__main__":
    # Si el usuario pasa una URL como argumento, la usamos
    if len(sys.argv) > 1:
        url_objetivo = sys.argv[1]
        obtener_cabeceras_seguridad(url_objetivo)
    else:
        # Si no pasa nada, mostramos ayuda
        print("Uso: python headers.py <URL>")
        print("Ejemplo: python headers.py https://tajamar.es")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for url in sys.argv[1:]:
            obtener_cabeceras_seguridad(url)
    else:
        print("Uso: python headers.py <URL1> <URL2> ...")
