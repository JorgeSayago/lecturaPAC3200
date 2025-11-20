import time
import struct
import psycopg2
from pymodbus.client.sync import ModbusTcpClient
from config import DB_PARAMS, TABLE_NAME, MULTIMETERS

# -----------------------------------------
# DECODIFICAR FLOAT32 (formato Siemens)
# -----------------------------------------

def decode_float32(registers):
    raw = (registers[0] << 16) | registers[1]
    packed = struct.pack('>I', raw)
    return struct.unpack('!f', packed)[0]

# -----------------------------------------
# LEER UN REGISTRO DEL PAC (FLOAT32)
# -----------------------------------------

def read_float(client, address, unit=1):
    res = client.read_holding_registers(address, 2, unit=unit)
    if res.isError():
        return None
    return decode_float32(res.registers)

# -----------------------------------------
# INSERTAR DATOS EN POSTGRESQL
# -----------------------------------------

def insert_data(device, v1, v2, v3, p_kw):
    conn = psycopg2.connect(
        host=DB_PARAMS["host"],
        database=DB_PARAMS["database"],
        user=DB_PARAMS["user"],
        password=DB_PARAMS["password"]
    )
    cur = conn.cursor()

    sql = f"""
        INSERT INTO {TABLE_NAME} 
        (device, voltage_l1, voltage_l2, voltage_l3, power_kw)
        VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(sql, (device, v1, v2, v3, p_kw))

    conn.commit()
    cur.close()
    conn.close()

# -----------------------------------------
# LOOP PRINCIPAL
# -----------------------------------------

def main():
    m = MULTIMETERS[0]       # Primer multímetro (PAC3220)

    client = ModbusTcpClient(m["ip"], port=m["port"], timeout=m["timeout"])

    print(f"Conectando a {m['ip']}...")
    if not client.connect():
        print("❌ No se pudo conectar al PAC3220")
        return

    print("🔥 Logging activo a PostgreSQL (cada 5 s)")
    print("⚡ Mostrando solo gasto total eléctrico (kWh) en pantalla\n")

    # Direcciones Modbus PAC3200/3220
    REG_VA = 1
    REG_VB = 3
    REG_VC = 5
    REG_PTOT = 15

    intervalo_seg = 5
    intervalo_horas = intervalo_seg / 3600.0

    gasto_total_kwh = 0.0

    while True:
        v1 = read_float(client, REG_VA)
        v2 = read_float(client, REG_VB)
        v3 = read_float(client, REG_VC)
        pkw = read_float(client, REG_PTOT)

        # Guardar en BD
        insert_data(m["device"], v1, v2, v3, pkw)

        # Calcular gasto eléctrico
        if pkw is not None:
            incremento = pkw * intervalo_horas
            gasto_total_kwh += incremento

        # Mostrar SOLO gasto eléctrico
        print(f"Gasto total acumulado: {gasto_total_kwh:.6f} kWh")

        time.sleep(intervalo_seg)


if __name__ == "__main__":
    main()
