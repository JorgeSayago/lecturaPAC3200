# -----------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------

DB_PARAMS = { 
    "host": "localhost",
    "database": "sentron_db",
    "user": "postgres",
    "password": "admin"
}

TABLE_NAME = "pac_measurements"

# -----------------------------------------
# REGISTROS MODBUS (PAC3220)
# -----------------------------------------

REGISTERS = {
    # Voltajes
    "voltage_l1": 1,
    "voltage_l2": 3,
    "voltage_l3": 5,

    # Corrientes
    "current_l1": 7,
    "current_l2": 9,
    "current_l3": 11,

    # 🔥 POTENCIA REAL (NEGATIVA POR CT INVERTIDO)
    "power_active_kw": 169,       # 0x00A9
    "power_reactive_kvar": 175    # 0x00AF
}

# -----------------------------------------
# DISPOSITIVOS
# -----------------------------------------

MULTIMETERS = [
    {
        "device": "device_1",
        "ip": "192.168.1.30",
        "port": 502,
        "timeout": 3
    }
]