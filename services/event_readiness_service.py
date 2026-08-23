from services.db import get_db_connection


READINESS_ORDER = {"Blocked": 0, "Needs Attention": 1, "Ready": 2}


def get_event_readiness():
    """Build an Intune-inspired readiness view from the existing endpoint data."""

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                d.hostname,
                d.owner,
                d.department,
                d.location,
                d.status AS device_status,
                d.last_seen,
                h.os,
                COALESCE(s.required_total, 0) AS required_total,
                COALESCE(s.required_missing, 0) AS required_missing,
                COALESCE(p.patch_total, 0) AS patch_total,
                COALESCE(p.patch_missing, 0) AS patch_missing
            FROM devices d
            LEFT JOIN hardware h ON h.hostname = d.hostname
            LEFT JOIN (
                SELECT
                    hostname,
                    SUM(CASE WHEN required = 'YES' THEN 1 ELSE 0 END) AS required_total,
                    SUM(CASE WHEN required = 'YES' AND installed = 0 THEN 1 ELSE 0 END) AS required_missing
                FROM software
                GROUP BY hostname
            ) s ON s.hostname = d.hostname
            LEFT JOIN (
                SELECT
                    hostname,
                    SUM(CASE WHEN applicable = 'YES' THEN 1 ELSE 0 END) AS patch_total,
                    SUM(CASE WHEN applicable = 'YES' AND installed = 0 THEN 1 ELSE 0 END) AS patch_missing
                FROM patches
                GROUP BY hostname
            ) p ON p.hostname = d.hostname
            ORDER BY d.hostname
            """
        ).fetchall()
    finally:
        conn.close()

    devices = []
    counts = {"Ready": 0, "Needs Attention": 0, "Blocked": 0}

    for row in rows:
        record = dict(row)
        reasons = []
        blocked = False

        if (record.get("device_status") or "").lower() != "online":
            reasons.append("Endpoint offline")
            blocked = True
        if record["required_missing"]:
            reasons.append(f'{record["required_missing"]} required app(s) missing')
            blocked = True
        if record["patch_missing"]:
            reasons.append(f'{record["patch_missing"]} applicable patch(es) pending')
        if "windows 10" in (record.get("os") or "").lower():
            reasons.append("Windows 10 lifecycle review")

        if blocked:
            readiness = "Blocked"
        elif reasons:
            readiness = "Needs Attention"
        else:
            readiness = "Ready"
            reasons.append("Required app and patch checks passed")

        record["readiness"] = readiness
        record["reasons"] = reasons
        record["search_text"] = " ".join(
            str(record.get(key) or "")
            for key in ("hostname", "owner", "department", "location", "os")
        ).lower()
        counts[readiness] += 1
        devices.append(record)

    devices.sort(key=lambda device: (READINESS_ORDER[device["readiness"]], device["hostname"]))

    return {
        "devices": devices,
        "total": len(devices),
        "ready": counts["Ready"],
        "attention": counts["Needs Attention"],
        "blocked": counts["Blocked"],
    }
