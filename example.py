import time
import struct
import math
import psycopg2
from pymodbus.client.sync import ModbusTcpClient
from config import DB_PARAMS, TABLE_NAME, MULTIMETERS, REGISTERS


def decode_float32(registers):
    raw = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">f", raw)[0]


def read_float(client, address, unit=1):
    try:
        if address is None:
            return 0

        res = client.read_holding_registers(address, 2, unit=unit)

        if res.isError():
            return 0

        value = decode_float32(res.registers)

        if math.isnan(value) or math.isinf(value):
            return 0

        return value

    except Exception:
        return 0


def fmt(value, decimals=2):
    return f"{value:.{decimals}f}"


def insert_data(device, data):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    sql = f"""
        INSERT INTO {TABLE_NAME}
        (
            device,

            voltage_l1,
            voltage_l2,
            voltage_l3,

            voltage_l12,
            voltage_l23,
            voltage_l31,

            current_l1,
            current_l2,
            current_l3,

            power_kw,
            power_active_kw,
            power_reactive_kvar,
            power_apparent,

            power_factor,
            cos_phi,

            frequency,

            voltage_unbalance,
            current_unbalance,

            thd_voltage_l1,
            thd_voltage_l2,
            thd_voltage_l3,

            thd_voltage_l12,
            thd_voltage_l23,
            thd_voltage_l31,

            thd_current_l1,
            thd_current_l2,
            thd_current_l3,

            energy_apparent,
            energia_kwh,
            energy_reactive
        )
        VALUES (
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s,
            %s,

            %s,
            %s,

            %s,

            %s,
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s,

            %s,
            %s,
            %s
        )
    """

    cur.execute(sql, (
        device,

        data["voltage_l1"],
        data["voltage_l2"],
        data["voltage_l3"],

        data["voltage_l12"],
        data["voltage_l23"],
        data["voltage_l31"],

        data["current_l1"],
        data["current_l2"],
        data["current_l3"],

        data["power_kw"],
        data["power_active_kw"],
        data["power_reactive_kvar"],
        data["power_apparent"],

        data["power_factor"],
        data["cos_phi"],

        data["frequency"],

        data["voltage_unbalance"],
        data["current_unbalance"],


        data["thd_voltage_l1"],
        data["thd_voltage_l2"],
        data["thd_voltage_l3"],

        data["thd_voltage_l12"],
        data["thd_voltage_l23"],
        data["thd_voltage_l31"],

        data["thd_current_l1"],
        data["thd_current_l2"],
        data["thd_current_l3"],

        data["energy_apparent"],
        data["energia_kwh"],
        data["energy_reactive"]
    ))

    conn.commit()
    cur.close()
    conn.close()


def main():
    m = MULTIMETERS[0]

    client = ModbusTcpClient(
        m["ip"],
        port=m["port"],
        timeout=m["timeout"]
    )

    print(f"Conectando a {m['ip']}...")

    if not client.connect():
        print("No se pudo conectar al PAC")
        return

    print("Conectado. Lectura cada 5 segundos...\n")

    while True:
        data = {}

        for key, reg in REGISTERS.items():
            data[key] = read_float(client, reg)

        insert_data(m["device"], data)

        print("======================================")
        print("LECTURA SENTRON PAC")
        print("======================================")

        print(
            f"Tension UL-N: "
            f"{fmt(data['voltage_l1'])} | "
            f"{fmt(data['voltage_l2'])} | "
            f"{fmt(data['voltage_l3'])} V"
        )

        print(
            f"Tension UL-L: "
            f"{fmt(data['voltage_l12'])} | "
            f"{fmt(data['voltage_l23'])} | "
            f"{fmt(data['voltage_l31'])} V"
        )

        print(
            f"Corrientes: "
            f"{fmt(data['current_l1'])} | "
            f"{fmt(data['current_l2'])} | "
            f"{fmt(data['current_l3'])} A"
        )

        print(f"Potencia total:    {fmt(data['power_kw'])}")
        print(f"Potencia activa:   {fmt(data['power_active_kw'])}")
        print(f"Potencia reactiva: {fmt(data['power_reactive_kvar'])}")
        print(f"Potencia aparente: {fmt(data['power_apparent'])}")

        print(f"Factor potencia: {fmt(data['power_factor'], 3)}")
        print(f"Cos phi:         {fmt(data['cos_phi'], 3)}")

        print(f"Frecuencia: {fmt(data['frequency'])} Hz")

        print(f"Desbalance U%: {fmt(data['voltage_unbalance'])}")
        print(f"Desbalance I%: {fmt(data['current_unbalance'])}")


        print(
            f"THD voltaje L1/L2/L3: "
            f"{fmt(data['thd_voltage_l1'])} | "
            f"{fmt(data['thd_voltage_l2'])} | "
            f"{fmt(data['thd_voltage_l3'])} %"
        )

        print(
            f"THD voltaje L12/L23/L31: "
            f"{fmt(data['thd_voltage_l12'])} | "
            f"{fmt(data['thd_voltage_l23'])} | "
            f"{fmt(data['thd_voltage_l31'])} %"
        )

        print(
            f"THD corriente L1/L2/L3: "
            f"{fmt(data['thd_current_l1'])} | "
            f"{fmt(data['thd_current_l2'])} | "
            f"{fmt(data['thd_current_l3'])} %"
        )

        print(f"Energia aparente: {fmt(data['energy_apparent']/1000)}")
        print(f"Energia activa:   {fmt(data['energia_kwh']/1000)}")
        print(f"Energia reactiva: {fmt(data['energy_reactive']/1000)}")

        print("======================================\n")

        time.sleep(5)


if __name__ == "__main__":
    main()