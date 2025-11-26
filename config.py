from libs.sentron_pac3200 import PAC3200_MEASUREMENTS

DB_PARAMS = { 
    "host": "localhost",
    "database": "sentron_db",    
    "user": "postgres",
    "password": "admin"
}

# Tabla principal donde guardarás todo (voltajes + potencia + corriente)
TABLE_NAME = "pac_measurements"

MULTIMETERS = [
    {
        "device": "device_1",
        "ip": "192.168.1.30",
        "port": 502,
        "timeout": 3,
        "measurements": [
            PAC3200_MEASUREMENTS['Voltage Va-n'],
            PAC3200_MEASUREMENTS['Voltage Vb-n'],
            PAC3200_MEASUREMENTS['Voltage Vc-n'],
        ]
    },
    {
        "device": "device_2",
        "ip": "192.168.1.30",
        "port": 502,
        "timeout": 3,
        "measurements": [
            PAC3200_MEASUREMENTS['Voltage Va-n'],
            PAC3200_MEASUREMENTS['Voltage Vb-n'],
            PAC3200_MEASUREMENTS['Voltage Vc-n'],
        ]
    }
]
