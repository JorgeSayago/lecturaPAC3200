from libs.sentron_pac3200 import PAC3200_MEASUREMENTS

DB_PARAMS = { 
    "host": "localhost",
    "database": "sentron_db",
    "user": "postgres",
    "password": "admin"
}

TABLE_NAME = "pac_measurements"

# Registros Modbus PAC3220 / PAC3200
REGISTERS = {
    "voltage_l1": 1,
    "voltage_l2": 3,
    "voltage_l3": 5,
    "current_l1": 7,
    "current_l2": 9,
    "current_l3": 11,
    "power_active_kw": 15,
    "power_reactive_kvar": 17
}

MULTIMETERS = [
    {
        "device": "device_1",
        "ip": "192.168.1.30",
        "port": 502,
        "timeout": 3
    }
]
