import os
from flask import Flask, render_template, redirect
import sqlite3

from services.inventory_import import initialize_database
from services.device_service import get_all_devices, get_device_by_hostname, get_device_software,get_device_hardware,get_device_printers, get_network_drives, get_patches
from services.db_init import create_database, DB_PATH
from services.dashboard_service import get_dashboard_summary, get_risk_devices
from services.compliance_service import calculate_compliance_score, generate_alerts
from services.inventory_service import get_inventory
from services.alertboard_service import generate_alertboard
from services.patch_service import get_patch_progress,get_wave_progress, get_department_progress


app = Flask(__name__)


# ============================================
# All Tables: DBの全テーブルをそのまま表示する機能で使用
# ============================================

# db_init.py の create_database() で作成しているテーブル名と一致させること
ALL_TABLE_NAMES = [
    "devices",
    "software",
    "hardware",
    "printers",
    "network_drives",
    "patches",
]

# 画面表示用のラベル
TABLE_LABELS = {
    "devices": "Devices",
    "software": "Software",
    "hardware": "Hardware",
    "printers": "Printers",
    "network_drives": "Network Drives",
    "patches": "Patches",
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/admin/import")
def import_inventory():

    initialize_database()

    return "Database Refreshed"


@app.route("/")
def home():
    return "Virtual Help Desk Running"


@app.route("/dashboard")
def dashboard():

    summary = get_dashboard_summary()

    alertboard = generate_alertboard(summary)

    risks = get_risk_devices()

    inventory = get_inventory()

    patch_progress = get_patch_progress()
    wave_progress = get_wave_progress()
    dept_progress = get_department_progress()


    return render_template(
        "dashboard.html",
        active_page="dashboard",
        summary=summary,
        risks=risks,
        inventory=inventory,
        alertboard=alertboard,
        patch_progress=patch_progress,
        wave_progress=wave_progress,
        dept_progress=dept_progress

    )


@app.route("/readme")
def show_readme():

    return render_template(
        "readme.html",
        active_page="readme",
    )


@app.route("/devices")
def show_devices():

    devices = get_all_devices()

    return render_template(
        "devices.html",
        devices=devices
    )


@app.route("/devices/<hostname>")
def device_detail(hostname):

    device = get_device_by_hostname(hostname)
    if device is None:
        return "Device not found", 404

    software = get_device_software(hostname)
    if software is None:
        return "Software not found", 404

    hardware = get_device_hardware(hostname)
    if hardware is None:
        return "hardware not found", 404

    printer = get_device_printers(hostname)
    if printer is None:
        return "Printer not found", 404

    network_drive = get_network_drives(hostname)
    if network_drive is None:
        return "Network Drive not found", 404

    patch = get_patches(hostname)
    if patch is None:
        return "Patch updates not found", 404

    score = calculate_compliance_score(
        software,
        patch,
        printer,
        network_drive
    )

    alerts = generate_alerts(
        hardware,
        software,
        patch,
        network_drive
    )

    print("test_device_detail")
    print(device_detail)

    return render_template(
        "device_detail.html",
        device=device,
        software=software,
        hardware=hardware,
        printer = printer,
        network_drive = network_drive,
        patch = patch,

        compliance_score = score,
        alerts= alerts
    )


@app.route("/all_tables")
def all_tables():

    conn = get_db_connection()
    tables = {}

    for table_name in ALL_TABLE_NAMES:
        cursor = conn.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]

        tables[table_name] = {
            "label": TABLE_LABELS.get(table_name, table_name),
            "rows": rows,
        }

    conn.close()

    return render_template(
        "all_tables.html",
        active_page="all_tables",
        tables=tables,
    )



@app.errorhandler(500)
def error(e):
    return "Internal Server Error", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


#@app.errorhandler(500)
#def error(e):
#    import traceback
#    traceback.print_exc()
#    return "DEBUG 500 ERROR - check terminal", 500



#if __name__ == "__main__":

#   create_database()        #Create DB
#   initialize_database()    #Insert CSV to DB

#  app.run(
#        host="0.0.0.0",
#        port=5055
#   )
