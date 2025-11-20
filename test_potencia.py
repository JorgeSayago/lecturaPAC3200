from pymodbus.client.sync import ModbusTcpClient

PLC_IP = "192.168.1.30"

client = ModbusTcpClient(PLC_IP, port=502, timeout=3)

print("Escaneando registros FLOAT válidos...")

if client.connect():
    for reg in range(0, 200, 2):   # prueba 0,2,4,...,200
        resp = client.read_holding_registers(reg, 2, unit=1)

        if not resp.isError():
            print(f"Registro {reg}: OK → {resp.registers}")
        else:
            pass  # ignoramos errores
else:
    print("No se pudo conectar")

client.close()
