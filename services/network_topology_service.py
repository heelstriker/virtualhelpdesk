"""
services/network_topology_service.py

Builds the {nodes, edges, drives} graph payload for the Dashboard's
Network Topology widget, reusing the existing catalog getters from
services/device_service.py instead of touching the DB directly.

Also owns the tiny `network_override` table used to persist the
widget's "simulate this device/link as down" toggles, kept separate
from the real inventory tables so double-clicking around the diagram
can never corrupt actual switch_catalog / network_topology rows.
"""
from services.device_service import (
    get_all_devices,
    get_server_catalog,
    get_printer_catalog,
    get_network_drive_catalog,
    get_switch_catalog,
    get_network_topology,
)
from services.db import get_db_connection

TYPE_MAP = {
    "MPLS Router": "router",
    "Core L3 Switch": "core_switch",
    "Access Switch": "access_switch",
    "MPLS CORE": "cloud",
}

# Hand-tuned layout for the hierarchical NOC-style diagram: NYC on the
# left, LAX on the right, MPLS cloud centered above both. If a device
# is ever added/removed, add/remove its coordinate here too.
POSITIONS = {
    "MPLS-CLOUD-01": (900, 70),
    "NYCRTR01": (560, 210), "LAXRTR01": (1240, 210),
    "NYCCORE-L3-01": (560, 330), "LAXCORE-L3-01": (1240, 330),
    "NYCACTSW01": (400, 460), "NYCSERVER01": (720, 460),
    "LAXHRSW01": (900, 460), "LAXITSSW01": (1080, 460),
    "LAXMKTSW01": (1260, 460), "LAXOPSSW01": (1440, 460),
    "LAXSERVER01": (1620, 460),
    "NYC-ACCOUNTING-PCS": (320, 600), "NYC-ACCOUNTING-PRINTERS": (480, 600),
    "LAX-HR-PCS": (860, 600), "LAX-HR-PRINTERS": (940, 600),
    "LAX-IT-PCS": (1040, 600), "LAX-IT-PRINTERS": (1120, 600),
    "LAX-MARKETING-PCS": (1220, 600), "LAX-MARKETING-PRINTERS": (1300, 600),
    "LAX-OPERATIONS-PCS": (1400, 600), "LAX-OPERATIONS-PRINTERS": (1480, 600),
}


def _norm(name):
    """switch_catalog.csv spells the core switches "...CORE-L3-01"
    (hyphenated) while network_topology.csv spells them
    "...COREL3-01" (no hyphen). Normalize to the hyphenated form so
    source_device/destination_device actually match switch_catalog
    device_id when building graph edges."""
    n = (name or "").strip().upper()
    n = n.replace("NYCCOREL3-01", "NYCCORE-L3-01")
    n = n.replace("LAXCOREL3-01", "LAXCORE-L3-01")
    return n


def _ensure_override_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS network_override (
            entity_type TEXT NOT NULL,   -- 'node' | 'edge'
            entity_id   TEXT NOT NULL,
            status      TEXT NOT NULL,   -- 'Offline' | 'severed'
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (entity_type, entity_id)
        )
    """)
    conn.commit()


def _get_overrides():
    conn = get_db_connection()
    _ensure_override_table(conn)
    node_overrides, edge_overrides = {}, {}
    for r in conn.execute("SELECT entity_type, entity_id, status FROM network_override"):
        r = dict(r)
        if r["entity_type"] == "node":
            node_overrides[r["entity_id"]] = r["status"]
        else:
            edge_overrides[r["entity_id"]] = r["status"]
    conn.close()
    return node_overrides, edge_overrides


def set_device_override(device_id, status):
    conn = get_db_connection()
    _ensure_override_table(conn)
    device_id = _norm(device_id)
    if status == "Online":
        conn.execute("DELETE FROM network_override WHERE entity_type='node' AND entity_id=?", (device_id,))
    else:
        conn.execute(
            "INSERT INTO network_override (entity_type, entity_id, status) VALUES ('node', ?, ?) "
            "ON CONFLICT(entity_type, entity_id) DO UPDATE SET status=excluded.status",
            (device_id, status),
        )
    conn.commit()
    conn.close()


def set_link_override(link_id, status):
    conn = get_db_connection()
    _ensure_override_table(conn)
    if status == "up":
        conn.execute("DELETE FROM network_override WHERE entity_type='edge' AND entity_id=?", (link_id,))
    else:
        conn.execute(
            "INSERT INTO network_override (entity_type, entity_id, status) VALUES ('edge', ?, ?) "
            "ON CONFLICT(entity_type, entity_id) DO UPDATE SET status=excluded.status",
            (link_id, status),
        )
    conn.commit()
    conn.close()


def reset_overrides():
    conn = get_db_connection()
    _ensure_override_table(conn)
    conn.execute("DELETE FROM network_override")
    conn.commit()
    conn.close()


def get_network_topology_graph():
    node_overrides, edge_overrides = _get_overrides()
    nodes = {}
    edges = []

    # --- infra devices (routers, core/access switches, MPLS cloud) ---
    for row in get_switch_catalog():
        r = dict(row)
        nid = _norm(r["device_id"])
        nodes[nid] = {
            "id": nid,
            "type": TYPE_MAP.get(r["device_type"], "device"),
            "label": nid,
            "model": r.get("model"),
            "vendor": r.get("vendor"),
            "mgmt_ip": r.get("management_ip"),
            "lan_ip": r.get("lan_ip"),
            "location": r.get("location"),
            "rack": r.get("rack"),
            "status": node_overrides.get(nid, r.get("status", "Online")),
            "firmware": r.get("firmware"),
            "serial": r.get("serial_number"),
        }

    # --- file servers (+ uplink edge into their switch) ---
    for row in get_server_catalog():
        r = dict(row)
        nid = _norm(r["hostname"])
        site = "NYC" if r.get("site") == "New York" else "LAX"
        nodes[nid] = {
            "id": nid, "type": "file_server", "label": nid, "role": r.get("role"),
            "ip": r.get("ip_address"), "os": r.get("operating_system"),
            "status": node_overrides.get(nid, r.get("status", "Online")), "site": site,
            "cpu": r.get("cpu"), "memory_gb": r.get("memory_gb"), "storage_tb": r.get("storage_tb"),
            "description": r.get("description"),
        }
        sw = _norm(r.get("switch_id"))
        if sw:
            eid = f"{sw}__{nid}"
            edges.append({
                "id": eid, "source": sw, "target": nid, "type": "LAN",
                "status": edge_overrides.get(eid, "Up"), "bandwidth": "10Gbps",
                "label": r.get("switch_port"),
            })

    # --- PC groups, aggregated per (department, location) ---
    dept_switch, dept_site, dept_status_lists = {}, {}, {}
    for row in get_all_devices():
        r = dict(row)
        key = (r["department"], r["location"])
        dept_switch[key] = _norm(r.get("switch_id"))
        dept_site[r["department"]] = r["location"]
        dept_status_lists.setdefault(key, []).append(r.get("status", "Online"))

    for (dept, loc), statuses in dept_status_lists.items():
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{dept.upper()}-PCS"
        online = sum(1 for s in statuses if s == "Online")
        default_status = "Online" if online == len(statuses) else ("Offline" if online == 0 else "Degraded")
        nodes[gid] = {
            "id": gid, "type": "pc_group", "label": f"{dept} PCs", "department": dept,
            "site": site, "count": len(statuses), "online_count": online,
            "status": node_overrides.get(gid, default_status),
        }
        sw = dept_switch.get((dept, loc))
        if sw:
            eid = f"{sw}__{gid}"
            edges.append({
                "id": eid, "source": sw, "target": gid, "type": "Access",
                "status": edge_overrides.get(eid, "Up"), "bandwidth": "1Gbps",
                "label": f"{len(statuses)}x ports",
            })

    # --- printer groups, aggregated per department ---
    pr_status_lists = {}
    for row in get_printer_catalog():
        r = dict(row)
        pr_status_lists.setdefault(r["department"], []).append(r.get("status", "Online"))

    for dept, statuses in pr_status_lists.items():
        loc = dept_site.get(dept)
        if not loc:
            continue
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{dept.upper()}-PRINTERS"
        online = sum(1 for s in statuses if s == "Online")
        default_status = "Online" if online == len(statuses) else ("Offline" if online == 0 else "Degraded")
        nodes[gid] = {
            "id": gid, "type": "printer_group", "label": f"{dept} Printers", "department": dept,
            "site": site, "count": len(statuses), "online_count": online,
            "status": node_overrides.get(gid, default_status),
        }
        sw = dept_switch.get((dept, loc))
        if sw:
            eid = f"{sw}__{gid}"
            edges.append({
                "id": eid, "source": sw, "target": gid, "type": "Access",
                "status": edge_overrides.get(eid, "Up"), "bandwidth": "1Gbps",
                "label": "print queue",
            })

    # --- backbone / MPLS links straight from network_topology table ---
    for row in get_network_topology():
        r = dict(row)
        src, dst = _norm(r["source_device"]), _norm(r["destination_device"])
        eid = f"{src}__{dst}"
        edges.append({
            "id": eid, "source": src, "target": dst, "type": r.get("link_type"),
            "status": edge_overrides.get(eid, r.get("status", "Up")),
            "bandwidth": r.get("bandwidth"), "latency_ms": r.get("latency_ms"),
            "utilization_pct": r.get("utilization_pct"), "packet_loss_pct": r.get("packet_loss_pct"),
            "alarm": r.get("alarm"), "label": r.get("notes"),
        })

    for nid, n in nodes.items():
        x, y = POSITIONS.get(nid, (900, 700))
        n["x"], n["y"] = x, y

    drives = [dict(r) for r in get_network_drive_catalog()]

    return {"nodes": list(nodes.values()), "edges": edges, "drives": drives}
