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
        
        activas = []
        faltantes_criticas = []
        
        # Clasificamos las cabeceras
        for header, criticidad in cabeceras_criticas.items():
            valor = response.headers.get(header)
            if valor:
                activas.append((header, valor, criticidad))
            else:
                if criticidad == "ALTA":
                    faltantes_criticas.append(header)
        
        # --- MOSTRAR CABECERAS ACTIVAS ---
        print("=" * 70)
        print(" ✅ CABECERAS DE SEGURIDAD ACTIVAS (Configuradas correctamente)")
        print("=" * 70)
        
        if activas:
            for header, valor, criticidad in activas:
                # Cortamos el valor si es muy largo para que no rompa la línea
                valor_mostrar = valor if len(valor) < 50 else valor[:47] + "..."
                print(f" [{criticidad:<5}] {header:<28} -> {valor_mostrar}")
        else:
            print(" [!] No se encontró ninguna cabecera de seguridad activa.")
        
        print("=" * 70)
        
        # --- RESUMEN DE FALTANTES (Solo críticas para no saturar) ---
        if faltantes_criticas:
            print(f"\n [!] AVISO: Faltan {len(faltantes_criticas)} cabeceras críticas:")
            for falta in faltantes_criticas:
                print(f"     - {falta}")
            print("     (Revisar recomendaciones de seguridad para este sitio)")
        else:
            print("\n [✓] ¡Excelente! Todas las cabeceras críticas están presentes.")
        
        return response.headers
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Error al conectar con {url}: {e}")
        return {}

# --- BLOQUE DE EJECUCIÓN POR COMANDOS ---
if __name__ == "__main__":
    # Si el usuario pasa una URL como argumento, la usamos
    if len(sys.argv) > 1:
        # Permite pasar múltiples URLs separadas por espacio
        for url in sys.argv[1:]:
            obtener_cabeceras_seguridad(url)
    else:
        # Si no pasa nada, mostramos ayuda
        print("Uso: python headers.py <URL1> <URL2> ...")
        print("Ejemplo: python headers.py https://tajamar.es https://google.com")
