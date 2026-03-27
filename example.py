import time
import struct
import psycopg2
from pymodbus.client.sync import ModbusTcpClient
from config import DB_PARAMS, TABLE_NAME, MULTIMETERS, REGISTERS

# -----------------------------------------
# DECODIFICAR FLOAT32 (SIEMENS)
# -----------------------------------------

def decode_float32(registers):
    raw = (registers[0] << 16) | registers[1]
    packed = struct.pack('>I', raw)
    return struct.unpack('!f', packed)[0]

# -----------------------------------------
# LEER FLOAT MODBUS
# -----------------------------------------

def read_float(client, address, unit=1):
    try:
        res = client.read_holding_registers(address, 2, unit=unit)
        if res.isError():
            return None
        return decode_float32(res.registers)
    except:
        return None

# -----------------------------------------
# INSERTAR EN POSTGRESQL
# -----------------------------------------

def insert_data(device, v1, v2, v3, c1, c2, c3, p_act, p_react, energia):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    sql = f"""
        INSERT INTO {TABLE_NAME}
        (device, voltage_l1, voltage_l2, voltage_l3,
         current_l1, current_l2, current_l3,
         power_active_kw, power_reactive_kvar,
         power_kw, energia_kwh)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cur.execute(sql, (
        device, v1, v2, v3,
        c1, c2, c3,
        p_act, p_react,
        p_act,        # power_kw (misma potencia)
        energia       # 🔥 energía acumulada
    ))

    conn.commit()
    cur.close()
    conn.close()

# -----------------------------------------
# LOOP PRINCIPAL
# -----------------------------------------

def main():
    m = MULTIMETERS[0]

    client = ModbusTcpClient(
        m["ip"],
        port=m["port"],
        timeout=m["timeout"]
    )

    print(f"Conectando a {m['ip']}...")

    if not client.connect():
        print("❌ No se pudo conectar al PAC3220")
        return

    print("✅ Conectado. Lectura cada 5 segundos...\n")

    intervalo_seg = 5
    intervalo_horas = intervalo_seg / 3600.0

    gasto_total_kwh = 0.0

    while True:
        # -------------------------
        # VOLTAJES
        # -------------------------
        v1 = read_float(client, REGISTERS["voltage_l1"]) or 0
        v2 = read_float(client, REGISTERS["voltage_l2"]) or 0
        v3 = read_float(client, REGISTERS["voltage_l3"]) or 0

        # -------------------------
        # CORRIENTES
        # -------------------------
        c1 = read_float(client, REGISTERS["current_l1"]) or 0
        c2 = read_float(client, REGISTERS["current_l2"]) or 0
        c3 = read_float(client, REGISTERS["current_l3"]) or 0

        # -------------------------
        # POTENCIAS (CORRECCIÓN CT)
        # -------------------------
        p_act_raw = read_float(client, REGISTERS["power_active_kw"])
        p_react_raw = read_float(client, REGISTERS["power_reactive_kvar"])

        p_act = abs(p_act_raw) if p_act_raw is not None else 0
        p_react = abs(p_react_raw) if p_react_raw is not None else 0

        # -------------------------
        # ENERGÍA ACUMULADA
        # -------------------------
        gasto_total_kwh += p_act * intervalo_horas

        # -------------------------
        # INSERTAR EN BD
        # -------------------------
        insert_data(
            m["device"],
            v1, v2, v3,
            c1, c2, c3,
            p_act, p_react,
            gasto_total_kwh   # 🔥 guardamos energía
        )

        # -------------------------
        # LOG CONSOLA
        # -------------------------
        print("======================================")
        print(f"Voltajes: {v1:.2f} | {v2:.2f} | {v3:.2f} V")
        print(f"Corrientes: {c1:.2f} | {c2:.2f} | {c3:.2f} A")
        print(f"Potencia activa: {p_act:.2f} kW")
        print(f"Potencia reactiva: {p_react:.2f} kVAR")
        print(f"Energía acumulada: {gasto_total_kwh:.6f} kWh")
        print("======================================\n")

        time.sleep(intervalo_seg)


if __name__ == "__main__":
    main()