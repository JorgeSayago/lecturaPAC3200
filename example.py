import time
import struct
import psycopg2
from pymodbus.client.sync import ModbusTcpClient
from config import DB_PARAMS, TABLE_NAME, MULTIMETERS, REGISTERS

# -----------------------------------------
# DECODIFICAR FLOAT32 (formato Siemens)
# -----------------------------------------

def decode_float32(registers):
    raw = (registers[0] << 16) | registers[1]
    packed = struct.pack('>I', raw)
    return struct.unpack('!f', packed)[0]

# -----------------------------------------
# LEER REGISTRO FLOAT32
# -----------------------------------------

def read_float(client, address, unit=1):
    res = client.read_holding_registers(address, 2, unit=unit)
    if res.isError():
        return None
    return decode_float32(res.registers)

# -----------------------------------------
# INSERTAR EN POSTGRESQL
# -----------------------------------------

def insert_data(device, v1, v2, v3, c1, c2, c3, p_act, p_react):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    sql = f"""
        INSERT INTO {TABLE_NAME}
        (device, voltage_l1, voltage_l2, voltage_l3,
         current_l1, current_l2, current_l3,
         power_active_kw, power_reactive_kvar)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cur.execute(sql, (device, v1, v2, v3, c1, c2, c3, p_act, p_react))

    conn.commit()
    cur.close()
    conn.close()

# -----------------------------------------
# LOOP PRINCIPAL
# -----------------------------------------

def main():
    m = MULTIMETERS[0]
    client = ModbusTcpClient(m["ip"], port=m["port"], timeout=m["timeout"])

    print(f"Conectando a {m['ip']}...")
    if not client.connect():
        print("NO se pudo conectar al PAC3220")
        return

    print("Lectura activa cada 5 segundos...\n")

    intervalo_seg = 5
    intervalo_horas = intervalo_seg / 3600.0

    gasto_total_kwh = 0.0

    while True:
        # ========== VOLTAJES ==========
        v1 = read_float(client, REGISTERS["voltage_l1"])
        if v1 is None:
            v1 = 0

        # duplicar porque solo L1 está conectado
        v2 = v1
        v3 = v1

        # ========== CORRIENTES ==========
        c1 = read_float(client, REGISTERS["current_l1"])
        if c1 is None:
            c1 = 0

        c2 = c1
        c3 = c1

        # ========== POTENCIAS ==========
        p_act = read_float(client, REGISTERS["power_active_kw"])
        if p_act is None:
            p_act = 0

        p_react = read_float(client, REGISTERS["power_reactive_kvar"])
        if p_react is None:
            p_react = 0

        # Insertar en base de datos
        insert_data(
            m["device"], v1, v2, v3,
            c1, c2, c3,
            p_act, p_react
        )

        # Acumulación gasto eléctrico
        gasto_total_kwh += p_act * intervalo_horas

        # Mostrar valores
        print(f"Gasto total acumulado: {gasto_total_kwh:.6f} kWh")
        print(f"V1={v1:.2f}  A1={c1:.2f}  kW={p_act:.2f}  kVAR={p_react:.2f}\n")

        time.sleep(intervalo_seg)


if __name__ == "__main__":
    main()
