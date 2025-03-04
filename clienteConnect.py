import os
import socket
import platform
import psutil
import json
import requests
import time
from datetime import datetime

# Obtener la IP local automáticamente
def obtener_ip_wifi():
    for interface, addrs in psutil.net_if_addrs().items():
        if "Wi-Fi" in interface or "Wireless" in interface or "wlan" in interface.lower():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    return addr.address  # Retorna la IP del Wi-Fi si la encuentra
    return "No se encontró la IP del Wi-Fi"

SERVER_IP = obtener_ip_wifi()
SERVER_URL = f"http://{SERVER_IP}:8080/items"

def convertir_a_unidad_adecuada(valor_bytes):
    """Convierte el valor en bytes a la unidad más adecuada (MB, GB, o TB)"""
    valor_mb = valor_bytes / (1024 ** 2)  # Convertir a MB
    if valor_mb >= 1024 ** 2:  # Si es mayor o igual a 1 TB
        return f"{valor_mb / (1024**2):.2f} TB"
    elif valor_mb >= 1024:  # Si es mayor o igual a 1 GB
        return f"{valor_mb / 1024:.2f} GB"
    else:  # Si es menor a 1 GB
        return f"{valor_mb:.2f} MB"

def obtener_info_sistema():
    # Obtener la hora y fecha actual
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener información de todas las interfaces de red
    interfaces_info = []
    direccion_mac = None
    for interface, addrs in psutil.net_if_addrs().items():
        ip_address = None
        mac_address = None
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ip_address = addr.address
            elif addr.family == psutil.AF_LINK:  # Dirección MAC
                mac_address = addr.address
                if direccion_mac == None:
                    direccion_mac = addr.address
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
                "total": convertir_a_unidad_adecuada(uso.total),  # Usar valor en bytes
                "libre": convertir_a_unidad_adecuada(uso.free),  # Usar valor en bytes
                "usado": convertir_a_unidad_adecuada(uso.used),  # Usar valor en bytes
                "porcentaje_usado": f"{uso.percent}%",
            })
        except Exception as e:
            print(f"⚠️ No se pudo obtener información del disco {particion.device}: {e}")

    # Obtener información del sistema
    nombre_dispositivo = platform.node()
    procesador = platform.processor()

    # Obtener información de la RAM
    ram = psutil.virtual_memory()
    ram_total = convertir_a_unidad_adecuada(ram.total)  # Usar valor en bytes
    ram_disponible = convertir_a_unidad_adecuada(ram.available)  # Usar valor en bytes
    ram_usada = convertir_a_unidad_adecuada(ram.used)  # Usar valor en bytes
    porcentaje_ram_usada = ram.percent

    # Crear diccionario con la información
    datos_sistema = {
        "hora_fecha": hora_actual,
        "interfaces": interfaces_info,
        "direccion_mac": direccion_mac,
        "nombre_dispositivo": nombre_dispositivo,
        "procesador": procesador,
        "discos": discos_info,  # Lista con todos los discos
        "ram": {
            "total": ram_total,
            "disponible": ram_disponible,
            "usada": ram_usada,
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
        if respuesta.status_code in [200, 201]:
            print("✅ Datos enviados exitosamente al servidor.")
        else:
            print(f"⚠️ Error al enviar datos: {respuesta.status_code} - {respuesta.text}")
    except Exception as e:
        print(f"❌ No se pudo enviar los datos al servidor: {e}")

# Enviar los datos continuamente 
while True:
    obtener_info_sistema()
    print("🔄 Esperando 10 segundos para la próxima actualización...\n")
    time.sleep(10)