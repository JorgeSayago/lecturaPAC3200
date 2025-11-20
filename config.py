from libs.sentron_pac3200 import PAC3200_MEASUREMENTS

DB_PARAMS = { 
    "host": "localhost",
    "database": "sentron_db",    # ← tu nueva base
    "user": "postgres",
    "password": "admin"
}

TABLE_NAME = "pac_measurements"
MULTIMETERS = [
    {
        "device": "device_1",
        "ip": "192.168.1.30",     # ← AQUÍ LA IP REAL DEL PAC3220
        "port": 502,
        "timeout": 3,
        "measurements": [
            PAC3200_MEASUREMENTS['Voltage Va-n'],
            PAC3200_MEASUREMENTS['Voltage Vb-n'],
            PAC3200_MEASUREMENTS['Voltage Vc-n']
        ]
    },
    {
        "device": "device_2",
        "ip": "192.168.1.30",     # ← Si vas a usar dos lecturas del mismo equipo
        "port": 502,
        "timeout": 3,
        "measurements": [
            PAC3200_MEASUREMENTS['Voltage Va-n'],
            PAC3200_MEASUREMENTS['Voltage Vb-n'],
            PAC3200_MEASUREMENTS['Voltage Vc-n']
        ]
    }
]
