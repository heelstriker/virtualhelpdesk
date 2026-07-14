from flask import Flask, render_template, redirect, jsonify, request
from services.inventory_import import initialize_database
from services.device_service import get_all_devices, get_device_by_hostname, get_device_software,get_device_hardware,get_device_printers, get_network_drives, get_patches, get_server_catalog, get_patch_catalog, get_software_catalog, get_printer_catalog,get_network_drive_catalog,get_switch_catalog,get_network_topology
from services.db_init import create_database
from services.db import get_db_connection
from services.dashboard_service import get_dashboard_summary, get_risk_devices, get_device_status_summary
from services.compliance_service import calculate_compliance_score, generate_alerts
from services.inventory_service import get_inventory
from services.alertboard_service import generate_alertboard
from services.patch_service import get_patch_progress,get_wave_progress, get_department_progress
from services.network_topology_service import (
    get_network_topology_graph,
    set_device_override,
    set_link_override,
    reset_overrides,
)



app = Flask(__name__)

# ============================================
# DB初期化
# 重要: gunicorn等(if __name__ == "__main__" を通らない起動方法)でも
# 必ず実行されるよう、モジュールのトップレベルで呼び出す。
# Renderのディスクは再デプロイのたびにリセットされるため、
# 起動のたびにスキーマ作成 + CSVからの再投入を行う。
# ============================================
create_database()
initialize_database()


# ============================================
# All Tables: DBの全テーブルをそのまま表示する機能で使用
# ============================================

# db_init.py の create_database() で作成しているテーブル名と一致させること
ALL_TABLE_NAMES = [
    "devices",
    "hardware",
    "server_catalog",
    "patch_catalog",
    "software_catalog",
    "printer_catalog",
    "network_drive_catalog",
    "switch_catalog",
    "network_topology",
    "printers",
    "network_drives",
    "patches",
    "software",
    
    
]

# 画面表示用のラベル
TABLE_LABELS = {
    "devices": "Devices Catalog",
    "hardware": "Hardware Catalog",
    "server_catalog": "Server Catalog",
    "patch_catalog": "Patch Catalog",
    "software_catalog":"Software Catalog",
    "printer_catalog":"Printer Catalog",
    "network_drive_catalog":"Network Drive Catalog",
    "switch_catalog": "Switch and Router Catalog",
    "network_topology":"Network Topology",
    "printers": "Printers (Transaction)",
    "network_drives": "Network Drives (Transaction)",  
    "patches": "Patches (Transaction)",
    "software": "Software (Transaction)",
    
}


@app.route("/admin/import")
def import_inventory():

    initialize_database()

    return "Database Refreshed"


@app.route("/")
def home():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():

    summary = get_dashboard_summary()

    alertboard = generate_alertboard(summary)

    risks = get_risk_devices()

    inventory = get_inventory()

    patch_progress = get_patch_progress()
    wave_progress = get_wave_progress()
    dept_progress = get_department_progress()

    device_status_rows = get_device_status_summary()
    device_status_labels = [row["status"] for row in device_status_rows]
    device_status_counts = [row["count"] for row in device_status_rows]

  
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        summary=summary,
        risks=risks,
        inventory=inventory,
        alertboard=alertboard,
        patch_progress=patch_progress,
        wave_progress=wave_progress,
        dept_progress=dept_progress,
        device_status_labels=device_status_labels,
        device_status_counts=device_status_counts,
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
        printer,
        network_drive
    )

   
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
@app.route("/powershell")
def powershell():
    return render_template("powershell.html", active_page="powershell")

@app.route("/erd")
def erd():
    return render_template("erd.html", active_page="erd")

@app.route("/field_notes")
def field_notes():
    return render_template("field_notes.html", active_page="field_notes")

@app.route("/case_studies")
def case_studies():
    return render_template("case_studies.html", active_page="case_studies")

@app.route("/api/printers")
def api_printers():

    conn=get_db_connection()

    printers=conn.execute("""

    SELECT printer_name,status,driver

    FROM printers

    """).fetchall()

    return jsonify([dict(x) for x in printers])

@app.route("/api/network/topology")
def api_network_topology():
    return jsonify(get_network_topology_graph())


@app.route("/api/network/device/<device_id>/status", methods=["POST"])
def api_network_device_status(device_id):
    status = (request.get_json(silent=True) or {}).get("status", "Online")
    set_device_override(device_id, status)
    return jsonify({"ok": True, "device_id": device_id, "status": status})


@app.route("/api/network/link/<path:link_id>/status", methods=["POST"])
def api_network_link_status(link_id):
    status = (request.get_json(silent=True) or {}).get("status", "up")
    set_link_override(link_id, status)
    return jsonify({"ok": True, "link_id": link_id, "status": status})


@app.route("/api/network/reset", methods=["POST"])
def api_network_reset():
    reset_overrides()
    return jsonify({"ok": True})


@app.route("/api/dashboard/summary")
def api_dashboard_summary():
    """Same data the /dashboard route renders server-side on page load,
    exposed as JSON so the Network Topology widget can trigger a live
    refresh of Active Alerts / Risk Devices / Device Status right after
    a toggle — no page reload needed."""
    summary = get_dashboard_summary()
    alertboard = generate_alertboard(summary)
    risks = get_risk_devices()
    device_status_rows = get_device_status_summary()
    return jsonify({
        "summary": summary,
        "alertboard": alertboard,
        "risks": [dict(r) for r in risks],
        "device_status_labels": [row["status"] for row in device_status_rows],
        "device_status_counts": [row["count"] for row in device_status_rows],
    })


@app.route("/cmd_reference")
def cmd_reference():
    return render_template(
        "cmd_reference.html",
        active_page="cmd_reference",
    )


@app.errorhandler(500)
def error(e):
    import traceback
    traceback.print_exc()
    return "DEBUG 500 ERROR - check terminal", 500




if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5055
    )
