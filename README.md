# 🕵️ OSINT Arsenal

Herramienta modular de reconocimiento **OSINT** desarrollada en Python. Combina técnicas de **enumeración pasiva** (sin tocar al objetivo) y **enumeración activa** (escaneo directo), junto con análisis de cabeceras de seguridad y un servidor web para visualizar los resultados en tiempo real.

---

## 📂 Estructura del Proyecto

---

## 🧩 Módulos Principales

### 1. `enumeracion.py` — Reconocimiento Pasivo + Activo

Contiene dos funciones principales que devuelven un diccionario con toda la información recolectada:

#### 🔍 `pasiva_completa(dominio)` — Enumeración Pasiva

Consultas a fuentes públicas sin interactuar directamente con el objetivo:

| Fuente | Qué obtiene |
|--------|-------------|
| `socket.gethostbyname` | Dirección IP asociada al dominio |
| `dns.resolver` (dnspython) | Registros **NS**, **MX**, **TXT** y **CNAME** |
| `whois` (python-whois) | Registrador, fechas de creación/expiración, organización |
| `crt.sh` | Subdominios encontrados vía Certificate Transparency |

> ⚠️ **Nota**: Los dominios `.es` tienen restricciones de privacidad por parte de Red.es, por lo que la información WHOIS puede no estar disponible. `crt.sh` puede sufrir timeouts por saturación.

#### ⚔️ `activa(dominio)` — Enumeración Activa

Escaneo directo de puertos comunes en la IP del objetivo:

```python
puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]

# 1. Clonar el repositorio
git clone https://github.com/carti6654/osint-arsenal.git
cd osint-arsenal

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt


flask
requests
dnspython
python-whois

Panel web
python app.py

# Enumeración completa de un dominio
python enumeracion.py

# Análisis de cabeceras
python headers.py

# Servidor de captura de User-Agents
python servidor_http.py
