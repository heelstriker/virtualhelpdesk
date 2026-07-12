"""
services/network_topology_service.py

Builds the {nodes, edges, drives} graph payload for the Dashboard's
Network Topology widget.

NOTE: This queries the DB directly via get_db_connection() + raw SQL
(SELECT * FROM <table>), the same pattern already used in app.py's
/api/printers and /all_tables routes. We deliberately do NOT call
services/device_service.py's get_switch_catalog() / get_all_devices()
/ etc., since several of those turned out to be single-record lookups
(e.g. get_switch_catalog(device_id)) rather than "get all rows"
getters, and guessing signatures kept breaking. Raw SQL against the
known table/column names (same ones used to build all_tables.html)
is more robust.

Also owns the tiny `network_override` table used to persist the
widget's "simulate this device/link as down" toggles, kept separate
from the real inventory tables so double-clicking around the diagram
can never corrupt actual switch_catalog / network_topology rows.
"""
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


def _rows(conn, sql):
    return [dict(r) for r in conn.execute(sql).fetchall()]


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


def _get_overrides(conn):
    _ensure_override_table(conn)
    node_overrides, edge_overrides = {}, {}
    for r in _rows(conn, "SELECT entity_type, entity_id, status FROM network_override"):
        if r["entity_type"] == "node":
            node_overrides[r["entity_id"]] = r["status"]
        else:
            edge_overrides[r["entity_id"]] = r["status"]
    return node_overrides, edge_overrides


def _ensure_backup_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS device_status_backup (
            hostname        TEXT PRIMARY KEY,
            original_status TEXT NOT NULL,
            backed_up_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def _bfs_reachable(edges, node_overrides, edge_overrides, root="MPLS-CLOUD-01"):
    """Same reachability rule the frontend uses: walk edges that aren't
    severed, skip nodes that are manually offline. Anything not visited
    is 'cut off' from the backbone."""
    adj = {}
    for e in edges:
        if edge_overrides.get(e["id"]) == "severed":
            continue
        adj.setdefault(e["source"], []).append(e["target"])
        adj.setdefault(e["target"], []).append(e["source"])
    visited = set()
    queue = [root]
    while queue:
        cur = queue.pop(0)
        if cur in visited or node_overrides.get(cur) == "Offline":
            continue
        visited.add(cur)
        for nb in adj.get(cur, []):
            if nb not in visited and node_overrides.get(nb) != "Offline":
                queue.append(nb)
    return visited


def _sync_devices_with_topology(conn):
    """Cascades the diagram's simulated online/offline & severed state
    down onto the real `devices` table, so the Dashboard's Active Alerts /
    Risk Devices / Device Status panels (which query `devices.status`
    directly in dashboard_service.py) reflect whatever the Network
    Topology widget is currently showing. No changes needed in
    dashboard_service.py / alertboard_service.py — they just re-query
    `devices` on every request and will see whatever this wrote.

    A device's original status is backed up before being forced
    Offline, and restored once it's reachable again, so this never
    permanently loses real data.
    """
    _ensure_backup_table(conn)
    node_overrides, edge_overrides = _get_overrides(conn)

    edges = []
    for r in _rows(conn, "SELECT source_device, destination_device FROM network_topology"):
        src, dst = _norm(r.get("source_device")), _norm(r.get("destination_device"))
        edges.append({"id": f"{src}__{dst}", "source": src, "target": dst})

    dept_switch = {}
    group_members = {}
    for r in _rows(conn, "SELECT hostname, department, location, switch_id FROM devices"):
        dept, loc, hostname = r.get("department"), r.get("location"), r.get("hostname")
        key = (dept, loc)
        dept_switch[key] = _norm(r.get("switch_id"))
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{(dept or '').upper()}-PCS"
        group_members.setdefault(gid, []).append(hostname)

    for (dept, loc), sw in dept_switch.items():
        if not sw:
            continue
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{(dept or '').upper()}-PCS"
        edges.append({"id": f"{sw}__{gid}", "source": sw, "target": gid})

    visited = _bfs_reachable(edges, node_overrides, edge_overrides)

    should_be_offline = set()
    for gid, hostnames in group_members.items():
        if gid not in visited:
            should_be_offline.update(hostnames)

    backed_up = {
        r["hostname"]: r["original_status"]
        for r in _rows(conn, "SELECT hostname, original_status FROM device_status_backup")
    }

    for hostname in should_be_offline:
        if hostname in backed_up:
            continue
        cur = conn.execute("SELECT status FROM devices WHERE hostname=?", (hostname,)).fetchone()
        if cur is None:
            continue
        conn.execute(
            "INSERT INTO device_status_backup (hostname, original_status) VALUES (?, ?)",
            (hostname, cur["status"]),
        )
        conn.execute("UPDATE devices SET status='Offline' WHERE hostname=?", (hostname,))

    for hostname, original_status in backed_up.items():
        if hostname in should_be_offline:
            continue
        conn.execute("UPDATE devices SET status=? WHERE hostname=?", (original_status, hostname))
        conn.execute("DELETE FROM device_status_backup WHERE hostname=?", (hostname,))

    conn.commit()


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
    _sync_devices_with_topology(conn)
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
    _sync_devices_with_topology(conn)
    conn.close()


def reset_overrides():
    conn = get_db_connection()
    _ensure_override_table(conn)
    conn.execute("DELETE FROM network_override")
    conn.commit()
    _sync_devices_with_topology(conn)  # restores every backed-up device
    conn.close()


def get_network_topology_graph():
    conn = get_db_connection()
    node_overrides, edge_overrides = _get_overrides(conn)
    nodes = {}
    edges = []

    # --- infra devices (routers, core/access switches, MPLS cloud) ---
    for r in _rows(conn, "SELECT * FROM switch_catalog"):
        nid = _norm(r.get("device_id"))
        nodes[nid] = {
            "id": nid,
            "type": TYPE_MAP.get(r.get("device_type"), "device"),
            "label": nid,
            "model": r.get("model"),
            "vendor": r.get("vendor"),
            "mgmt_ip": r.get("management_ip"),
            "lan_ip": r.get("lan_ip"),
            "location": r.get("location"),
            "rack": r.get("rack"),
            "status": node_overrides.get(nid, r.get("status") or "Online"),
            "firmware": r.get("firmware"),
            "serial": r.get("serial_number"),
        }

    # --- file servers (+ uplink edge into their switch) ---
    for r in _rows(conn, "SELECT * FROM server_catalog"):
        nid = _norm(r.get("hostname"))
        site = "NYC" if r.get("site") == "New York" else "LAX"
        nodes[nid] = {
            "id": nid, "type": "file_server", "label": nid, "role": r.get("role"),
            "ip": r.get("ip_address"), "os": r.get("operating_system"),
            "status": node_overrides.get(nid, r.get("status") or "Online"), "site": site,
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
    for r in _rows(conn, "SELECT * FROM devices"):
        key = (r.get("department"), r.get("location"))
        dept_switch[key] = _norm(r.get("switch_id"))
        dept_site[r.get("department")] = r.get("location")
        dept_status_lists.setdefault(key, []).append(r.get("status") or "Online")

    for (dept, loc), statuses in dept_status_lists.items():
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{(dept or '').upper()}-PCS"
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
    for r in _rows(conn, "SELECT * FROM printer_catalog"):
        pr_status_lists.setdefault(r.get("department"), []).append(r.get("status") or "Online")

    for dept, statuses in pr_status_lists.items():
        loc = dept_site.get(dept)
        if not loc:
            continue
        site = "NYC" if loc == "New York" else "LAX"
        gid = f"{site}-{(dept or '').upper()}-PRINTERS"
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
    for r in _rows(conn, "SELECT * FROM network_topology"):
        src, dst = _norm(r.get("source_device")), _norm(r.get("destination_device"))
        eid = f"{src}__{dst}"
        edges.append({
            "id": eid, "source": src, "target": dst, "type": r.get("link_type"),
            "status": edge_overrides.get(eid, r.get("status") or "Up"),
            "bandwidth": r.get("bandwidth"), "latency_ms": r.get("latency_ms"),
            "utilization_pct": r.get("utilization_pct"), "packet_loss_pct": r.get("packet_loss_pct"),
            "alarm": r.get("alarm"), "label": r.get("notes"),
        })

    drives = _rows(conn, "SELECT * FROM network_drive_catalog")
    conn.close()

    for nid, n in nodes.items():
        x, y = POSITIONS.get(nid, (900, 700))
        n["x"], n["y"] = x, y

    return {"nodes": list(nodes.values()), "edges": edges, "drives": drives}
