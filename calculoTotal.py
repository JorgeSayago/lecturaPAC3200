
import psycopg2
import time

# CONFIGURACIÓN
DB_PARAMS = {
    "host": "localhost",
    "database": "sentron_db",
    "user": "postgres",
    "password": "admin"
}

TABLE = "pac_measurements"
INTERVALO_SEG = 5              # intervalo de muestreo usado al registrar
FACTOR_POTENCIA = 0.90         # PF asumido para cálculo de kW


def calcular_kwh_desde_bd():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # Obtener todos los registros ordenados por fecha
    sql = f"""
        SELECT voltage_l1, current_l1, timestamp
        FROM {TABLE}
        ORDER BY timestamp ASC
    """
    cur.execute(sql)
    registros = cur.fetchall()

    cur.close()
    conn.close()

    if not registros:
        print("No hay registros en la base de datos.")
        return

    gasto_total_kwh = 0.0

    for row in registros:
        v = row[0] or 0
        a = row[1] or 0

        # Calcular potencia activa aproximada
        kw = (v * a * FACTOR_POTENCIA) / 1000

        # Convertimos el intervalo a horas
        gasto_total_kwh += kw * (INTERVALO_SEG / 3600)

    print("\n=====================================")
    print(f"Gasto total eléctrico aproximado: {gasto_total_kwh:.6f} kWh")
    print("=====================================\n")


if __name__ == "__main__":
    calcular_kwh_desde_bd()
