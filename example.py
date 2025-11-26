import time
import struct
import psycopg2
from pymodbus.client.sync import ModbusTcpClient
from config import DB_PARAMS, TABLE_NAME, MULTIMETERS


# -----------------------------------------
# DECODIFICAR FLOAT32 LITTLE-ENDIAN SIEMENS
# -----------------------------------------

def decode_float32(registers):
    raw = (registers[0] << 16) | registers[1]
    packed = struct.pack('>I', raw)
    return struct.unpack('!f', packed)[0]


# -----------------------------------------
# LEER FLOAT32 DESDE MODBUS
# -----------------------------------------

def read_float(client, address, unit=1):
    res = client.read_holding_registers(address, 2, unit=unit)
    if res.isError():
        return None
    return decode_float32(res.registers)


# -----------------------------------------
# INSERTAR EN LA TABLA PRINCIPAL pac_measurements
# AHORA TAMBIÉN INSERTA CORRIENTE
# -----------------------------------------

def insert_data(device, v1, v2, v3, c1, c2, c3, p_kw):
    conn = psycopg2.connect(
        host=DB_PARAMS["host"],
        database=DB_PARAMS["database"],
        user=DB_PARAMS["user"],
        password=DB_PARAMS["password"]
    )
    cur = conn.cursor()

    sql = f"""
        INSERT INTO {TABLE_NAME}
        (device, voltage_l1, voltage_l2, voltage_l3,
         current_l1, current_l2, current_l3, power_kw)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(sql, (device, v1, v2, v3, c1, c2, c3, p_kw))

    conn.commit()
    cur.close()
    conn.close()


# -----------------------------------------
# LOOP PRINCIPAL
# -----------------------------------------

def main():
    m = MULTIMETERS[0]  # PRIMER PAC

    client = ModbusTcpClient(m["ip"], port=m["port"], timeout=m["timeout"])

    print(f"Conectando a {m['ip']}...")
    if not client.connect():
        print("No se pudo conectar al PAC3220")
        return

    print("Logging activo cada 5 s\n")

    # Direcciones Modbus PAC3200/3220
    REG_VA = 1     # Voltage L1
    REG_VB = 3     # Voltage L2
    REG_VC = 5     # Voltage L3
    REG_PTOT = 15  # Potencia total

    REG_I1 = 7     # Corriente L1
    REG_I2 = 9     # Corriente L2
    REG_I3 = 11    # Corriente L3

    intervalo_seg = 5
    intervalo_horas = intervalo_seg / 3600.0
    gasto_total_kwh = 0.0

    while True:
        # Voltajes
        v1 = read_float(client, REG_VA)
        v2 = read_float(client, REG_VB)
        v3 = read_float(client, REG_VC)

        # Corrientes
        c1 = read_float(client, REG_I1)
        c2 = read_float(client, REG_I2)
        c3 = read_float(client, REG_I3)

        # Potencia
        pkw = read_float(client, REG_PTOT)

        # Guardar en BD
        insert_data(m["device"], v1, v2, v3, c1, c2, c3, pkw)

        # Actualizar gasto eléctrico
        if pkw is not None:
            gasto_total_kwh += pkw * intervalo_horas

        print(f"Gasto total acumulado: {gasto_total_kwh:.6f} kWh")

        time.sleep(intervalo_seg)


if __name__ == "__main__":
    main()
