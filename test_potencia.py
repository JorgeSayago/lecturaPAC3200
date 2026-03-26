from pymodbus.client.sync import ModbusTcpClient
import struct
import time

PLC_IP = "192.168.1.30"
UNIT = 1

def to_float(regs):
    try:
        raw = struct.pack('>HH', regs[0], regs[1])
        v = struct.unpack('>f', raw)[0]
        return v
    except:
        return None

client = ModbusTcpClient(PLC_IP, port=502, timeout=3)
if not client.connect():
    print("No se pudo conectar")
    exit()

print("Escaneando rango completo 1 - 65535...\n")

resultados = []
errores_bloque = 0
reg = 1
ultimo_valido = 0

with open("scan_completo.txt", "w") as f:
    f.write("REG | HEX | RAW | FLOAT\n")
    f.write("="*70 + "\n")

    while reg < 65535:
        resp = client.read_holding_registers(reg, 2, unit=UNIT)

        if not resp.isError():
            regs = resp.registers
            fval = to_float(regs)
            errores_bloque = 0
            ultimo_valido = reg

            linea = f"REG {reg:5d} (0x{reg:04X}) | RAW: {regs[0]:6d},{regs[1]:6d} | FLOAT: {fval:.4f}"
            print(linea)
            f.write(linea + "\n")
            resultados.append((reg, regs, fval))
            reg += 2

        else:
            errores_bloque += 1

            if errores_bloque < 20:
                # Seguimos de a 2
                reg += 2
            elif errores_bloque < 50:
                # Saltamos de a 10
                reg += 10
            else:
                # Zona muerta — saltamos 500 registros
                salto_a = ((reg // 500) + 1) * 500 + 1
                print(f"  >>> Zona sin datos, saltando de {reg} a {salto_a}...")
                f.write(f"  >>> Zona sin datos, saltando de {reg} a {salto_a}...\n")
                reg = salto_a
                errores_bloque = 0

print(f"\n{'='*60}")
print(f"TOTAL registros válidos: {len(resultados)}")
print(f"Resultados guardados en scan_completo.txt")

client.close()