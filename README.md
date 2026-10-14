# 🕵️ OSINT Arsenal

Herramienta modular de reconocimiento OSINT desarrollada en Python.

## Módulos incluidos
- **Enumeración Pasiva:** DNS, subdominios vía crt.sh.
- **Enumeración Activa:** Escaneo de puertos comunes.
- **Headers de Seguridad:** Análisis de cabeceras HTTP y criticidad.
- **Servidor HTTP:** Captura de User-Agents de peticiones entrantes.

## Requisitos
- Python 3.10+
- Entorno virtual (recomendado)

## Instalación
```bash
git clone https://github.com/carti6654/osint-arsenal.git
cd osint-arsenal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

USO
python enumeracion1.py
python headers.py
python servidor_http.py


