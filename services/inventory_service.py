from services.db import get_db_connection

def get_inventory():

    conn = get_db_connection()

    rows = conn.execute("""

    SELECT

        devices.hostname,
        devices.owner,
        devices.department,
        devices.status,
        devices.last_seen,
        devices.serial_number,
        devices.asset_tag,
        devices.purchase_date,
        devices.warranty_expiration,
        devices.retirement_date,
        devices.location,
        devices.cost_center,

        hardware.os,
        hardware.memory_gb,
        hardware.disk_gb

    FROM devices

    LEFT JOIN hardware
    ON devices.hostname = hardware.hostname

    ORDER BY devices.hostname

    """).fetchall()

    conn.close()

    return rows
