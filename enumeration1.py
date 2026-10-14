import socket
import requests
import os
import datetime

def crear_directorio_reportes():
    """Crea la carpeta de reportes si no existe."""
    if not os.path.exists("reportes"):
        os.makedirs("reportes")

def enumeracion_pasiva(dominio):
    """Realiza enumeración pasiva y guarda un reporte numerado."""
    print(f"[*] Iniciando enumeración PASIVA para {dominio}...")
    crear_directorio_reportes()
    
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = f"reportes/pasivo_{dominio}_{fecha}.txt"
    
    resultados = [f"=================================================="]
    resultados.append(f" REPORTE PASIVO - DOMINIO: {dominio}")
    resultados.append(f" Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    resultados.append(f"==================================================\n")
    
    try:
        # 1. Resolución DNS
        ip = socket.gethostbyname(dominio)
        resultados.append(f"--- [ INFORMACIÓN DNS ] ---")
        resultados.append(f" [+] Dirección IP resuelta: {ip}\n")
        
        # 2. Consulta a crt.sh (Certificate Transparency)
        url = f"https://crt.sh/?q=%25.{dominio}&output=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            datos = response.json()
            subdominios = sorted(set([item['name_value'] for item in datos]))
            resultados.append(f"--- [ SUBDOMINIOS ENCONTRADOS ({len(subdominios)}) ] ---")
            for i, sub in enumerate(subdominios, 1):
                resultados.append(f"  {i}. {sub}")
        else:
            resultados.append("[-] No se pudieron obtener subdominios de crt.sh")
    except Exception as e:
        resultados.append(f"[!] Error en enumeración pasiva: {e}")

    with open(archivo_salida, "w") as f:
        f.write("\n".join(resultados))
    print(f"[✓] Reporte pasivo guardado en: {archivo_salida}")

def enumeracion_activa(dominio):
    """Realiza enumeración activa y guarda un reporte numerado."""
    print(f"[*] Iniciando enumeración ACTIVA para {dominio}...")
    crear_directorio_reportes()
    
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = f"reportes/activo_{dominio}_{fecha}.txt"
    
    resultados = [f"=================================================="]
    resultados.append(f" REPORTE ACTIVO - DOMINIO: {dominio}")
    resultados.append(f" Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    resultados.append(f"==================================================\n")
    
    puertos_abiertos = []
    try:
        ip = socket.gethostbyname(dominio)
        puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]
        resultados.append(f"--- [ ESCANEO DE PUERTOS EN IP: {ip} ] ---")
        
        for puerto in puertos_comunes:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            resultado = sock.connect_ex((ip, puerto))
            if resultado == 0:
                puertos_abiertos.append(puerto)
            sock.close()
        
        if puertos_abiertos:
            for i, puerto in enumerate(puertos_abiertos, 1):
                resultados.append(f"  {i}. Puerto ABIERTO: {puerto}")
        else:
            resultados.append("  [-] No se encontraron puertos comunes abiertos.")
            
    except Exception as e:
        resultados.append(f"[!] Error en enumeración activa: {e}")

    with open(archivo_salida, "w") as f:
        f.write("\n".join(resultados))
    print(f"[✓] Reporte activo guardado en: {archivo_salida}")
# --- BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    print("=== PRUEBA DE ENUMERACIÓN ===")
    # Pedimos el dominio por pantalla para probar
    dominio = input("Ingresa un dominio para enumerar (ej. google.com): ")
    
    # Llamamos a las funciones
    enumeracion_pasiva(dominio)
    enumeracion_activa(dominio)
