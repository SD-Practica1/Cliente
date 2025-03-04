import os
import socket
import platform
import psutil
import json
import requests
import time
from datetime import datetime

# Obtener la IP local automáticamente
def obtener_ip_local():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return addr.address  # Retorna la primera IP de red detectada
    return "127.0.0.1"  # Si no se encuentra ninguna, usa localhost como fallback

# URL del servidor con la IP local detectada
SERVER_IP = obtener_ip_local()
SERVER_URL = f"http://{SERVER_IP}:8080/items"

def obtener_info_sistema():
    # Obtener la hora y fecha actual
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener información de todas las interfaces de red
    interfaces_info = []
    for interface, addrs in psutil.net_if_addrs().items():
        ip_address = None
        mac_address = None
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ip_address = addr.address
            elif addr.family == psutil.AF_LINK:  # Dirección MAC
                mac_address = addr.address
        if ip_address or mac_address:  # Guardamos solo si tiene alguna dirección
            interfaces_info.append({
                "interface": interface,
                "ip": ip_address,
                "mac": mac_address
            })

    
    # Obtener información de todos los discos
    discos_info = []
    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            discos_info.append({
                "nombre": particion.device,
                "tipo": particion.fstype,
                "montaje": particion.mountpoint,
                "total": f"{uso.total / (1024**3):.2f} GB",
                "libre": f"{uso.free / (1024**3):.2f} GB",
                "usado": f"{uso.used / (1024**3):.2f} GB",
                "porcentaje_usado": f"{uso.percent}%",
            })
        except Exception as e:
            print(f"⚠️ No se pudo obtener información del disco {particion.device}: {e}")

    # Obtener información del sistema
    nombre_dispositivo = platform.node()
    procesador = platform.processor()

    # Obtener información de la RAM
    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024**3), 2)  # Convertir a GB
    ram_disponible = round(ram.available / (1024**3), 2)  # Convertir a GB
    ram_usada = round(ram.used / (1024**3), 2)  # Convertir a GB
    porcentaje_ram_usada = ram.percent

    # Crear diccionario con la información
    datos_sistema = {
        "hora_fecha": hora_actual,
        "interfaces": interfaces_info,  # Lista con todas las interfaces de red
        "nombre_dispositivo": nombre_dispositivo,
        "procesador": procesador,
        "discos": discos_info,  # Lista con todos los discos
        "ram": {
            "total": f"{ram_total} GB",
            "disponible": f"{ram_disponible} GB",
            "usada": f"{ram_usada} GB",
            "porcentaje_usada": f"{porcentaje_ram_usada}%",
        }
    }

    # Guardar los datos en un archivo JSON
    with open("info_sistema.json", "w") as archivo_json:
        json.dump(datos_sistema, archivo_json, indent=4)

    print("✅ Datos del sistema guardados en 'info_sistema.json'.")

    # Enviar los datos al servidor
    enviar_datos_al_servidor(datos_sistema)

def enviar_datos_al_servidor(datos):
    try:
        respuesta = requests.post(SERVER_URL, json=datos)
        if respuesta.status_code == 200:
            print("✅ Datos enviados exitosamente al servidor.")
        else:
            print(f"⚠️ Error al enviar datos: {respuesta.status_code} - {respuesta.text}")
    except Exception as e:
        print(f"❌ No se pudo enviar los datos al servidor: {e}")

# Enviar los datos continuamente 
while True:
    obtener_info_sistema()
    print("🔄 Esperando 30 segundos para la próxima actualización...\n")
    time.sleep(30)
