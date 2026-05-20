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
# REGISTROS MODBUS PAC3220
# -----------------------------------------

REGISTERS = {

    "voltage_l1": 1,
    "voltage_l2": 3,
    "voltage_l3": 5,

    "voltage_l12": 7,
    "voltage_l23": 9,
    "voltage_l31": 11,

    "current_l1": 13,
    "current_l2": 15,
    "current_l3": 17,

    "power_kw": 65,
    "power_active_kw": 65,
    "power_reactive_kvar": 67,
    "power_apparent": 63,

    "power_factor": 69,
    "cos_phi": 247,

    "frequency": 55,

    "voltage_unbalance": 71,
    "current_unbalance": 73,

    "energy_apparent": 2817,
    "energia_kwh": 2801,
    "energy_reactive": 2809,

    "thd_voltage_l1": 43,
    "thd_voltage_l2": 45,
    "thd_voltage_l3": 47,

    "thd_current_l1": 49,
    "thd_current_l2": 51,
    "thd_current_l3": 53,

    "thd_voltage_l12": 271,
    "thd_voltage_l23": 273,
    "thd_voltage_l31": 275,
}

# -----------------------------------------
# DISPOSITIVOS
# -----------------------------------------

MULTIMETERS = [
    {
        "device": "device_1",
        "ip": "192.168.1.37",
        "port": 502,
        "timeout": 3
    }
]