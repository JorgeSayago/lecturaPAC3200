from pymodbus.client.sync import ModbusTcpClient
import struct
import math

PLC_IP = "192.168.1.37"
PORT = 502
UNIT = 1

REGISTERS = {
    "Tension UL-N L1": 30517,
    "Tension UL-N L2": 30519,
    "Tension UL-N L3": 30521,

    "Tension UL-L L12": 30523,
    "Tension UL-L L23": 30525,
    "Tension UL-L L31": 30527,

    "Potencia Aparente": 31059,
    "Potencia Activa": 31061,
    "Potencia Reactiva": 31063,

    "Factor Potencia": 31073,
    "Frecuencia": 31075,

    "Desbalance U%": 31101,
    "Desbalance I%": 31103,
    "THD Voltaje": 31105
}


def decode_float32(registers):
    raw = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">f", raw)[0]


def read_float(client, reg):
    try:
        resp = client.read_holding_registers(reg, 2, unit=UNIT)

        if resp.isError():
            return None

        value = decode_float32(resp.registers)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    except:
        return None


client = ModbusTcpClient(PLC_IP, port=PORT, timeout=3)

if not client.connect():
    print("No se pudo conectar")
    exit()

print("\n======================================")
print("LECTURA SENTRON PAC")
print("======================================")

for nombre, reg in REGISTERS.items():

    valor = read_float(client, reg)

    if valor is not None:
        print(f"{nombre}: {valor:.2f}")
    else:
        print(f"{nombre}: ERROR")

print("======================================\n")

client.close()