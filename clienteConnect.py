import os
import socket
import platform
import psutil
import json
import requests
import time
from datetime import datetime

# URL del servidor 
SERVER_URL = "http://192.168.190.104:8080/items"

def obtener_info_sistema():
    # Obtener la hora y fecha actual
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener la IP de conexión física y la dirección MAC
    ip_fisica = None
    direccion_mac = None
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ip_fisica = addr.address
            elif addr.family == psutil.AF_LINK:  # Dirección MAC
                direccion_mac = addr.address
        if ip_fisica and direccion_mac:
            break

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
        "ip_fisica": ip_fisica,
        "direccion_mac": direccion_mac,
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
    print("🔄 Esperando 2 segundos para la próxima actualización...\n")
    time.sleep(2)
