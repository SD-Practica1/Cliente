import os
import socket
import platform
import psutil
from datetime import datetime

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

    # Obtener información del disco principal
    disco = psutil.disk_usage('/')
    total_disco = disco.total / (1024**3)  # Convertir a GB
    espacio_libre = disco.free / (1024**3)  # Convertir a GB
    espacio_usado = disco.used / (1024**3)  # Convertir a GB
    porcentaje_usado = disco.percent  # Porcentaje de espacio utilizado

    # Obtener información del disco físico
    discos = psutil.disk_partitions()
    nombre_disco = "Desconocido"
    tipo_disco = "Desconocido"
    if discos:
        nombre_disco = discos[0].device
        tipo_disco = discos[0].fstype

    # Obtener información del sistema
    nombre_dispositivo = platform.node()
    procesador = platform.processor()

    # Obtener información de la RAM
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024**3)  # Convertir a GB
    ram_disponible = ram.available / (1024**3)  # Convertir a GB
    ram_usada = ram.used / (1024**3)  # Convertir a GB
    porcentaje_ram_usada = ram.percent

    # Mostrar la información
    print(f"Hora y Fecha: {hora_actual}")
    print(f"IP de conexión física: {ip_fisica}")
    print(f"Dirección MAC: {direccion_mac}")
    print(f"Nombre del dispositivo: {nombre_dispositivo}")
    print(f"Procesador: {procesador}")
    print(f"Nombre del disco: {nombre_disco}")
    print(f"Tipo de disco: {tipo_disco}")
    print(f"Tamaño total del disco: {total_disco:.2f} GB")
    print(f"Espacio libre en el disco: {espacio_libre:.2f} GB")
    print(f"Espacio utilizado: {espacio_usado:.2f} GB")
    print(f"Porcentaje de espacio utilizado: {porcentaje_usado:.2f}%")
    print(f"RAM total: {ram_total:.2f} GB")
    print(f"RAM disponible: {ram_disponible:.2f} GB")
    print(f"RAM utilizada: {ram_usada:.2f} GB")
    print(f"Porcentaje de RAM utilizada: {porcentaje_ram_usada:.2f}%")

obtener_info_sistema()
