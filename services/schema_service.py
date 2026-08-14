"""Read-only schema metadata used by the ERD page."""

from collections import OrderedDict

from services.db import get_db_connection


TABLE_GROUPS = OrderedDict(
    [
        (
            "Inventory and activity",
            {
                "description": "Device records and per-device observations.",
                "tables": {
                    "devices",
                    "hardware",
                    "software",
                    "printers",
                    "network_drives",
                    "patches",
                },
            },
        ),
        (
            "Catalogs and infrastructure",
            {
                "description": "Reference data for software, patches, shared resources, and network equipment.",
                "tables": {
                    "server_catalog",
                    "patch_catalog",
                    "software_catalog",
                    "printer_catalog",
                    "network_drive_catalog",
                    "switch_catalog",
                    "network_topology",
                },
            },
        ),
        (
            "Runtime state",
            {
                "description": "Service-managed state created when network status controls are used.",
                "tables": {"network_override", "device_status_backup"},
            },
        ),
    ]
)


# These links are conventions used by the application and seed data. They are
# intentionally separate from SQLite foreign keys, because db_init.py does not
# currently declare FOREIGN KEY constraints.
LOGICAL_RELATIONSHIPS = (
    ("devices", "hostname", "hardware", "hostname", "1 : 0..1", "has profile"),
    ("devices", "hostname", "software", "hostname", "1 : N", "runs"),
    ("devices", "hostname", "patches", "hostname", "1 : N", "receives"),
    ("devices", "hostname", "printers", "hostname", "1 : N", "uses"),
    ("devices", "hostname", "network_drives", "hostname", "1 : N", "mounts"),
    ("software_catalog", "software_name", "software", "software_name", "1 : N", "describes"),
    ("patch_catalog", "patch", "patches", "patch", "1 : N", "describes"),
    ("network_drive_catalog", "drive_name", "network_drives", "drive_name", "1 : N", "describes"),
    ("switch_catalog", "device_id", "devices", "switch_id", "1 : N", "connects"),
    ("switch_catalog", "device_id", "server_catalog", "switch_id", "1 : N", "connects"),
    ("devices", "hostname", "device_status_backup", "hostname", "1 : 0..1", "backs up status"),
)


def _column_metadata(connection, table_name):
    escaped_name = table_name.replace('"', '""')
    rows = connection.execute(f'PRAGMA table_info("{escaped_name}")').fetchall()
    return [
        {
            "name": row[1],
            "type": row[2] or "ANY",
            "required": bool(row[3]),
            "primary_key": bool(row[5]),
        }
        for row in rows
    ]


def _foreign_key_metadata(connection, table_name):
    escaped_name = table_name.replace('"', '""')
    rows = connection.execute(f'PRAGMA foreign_key_list("{escaped_name}")').fetchall()
    return [
        {
            "from_column": row[3],
            "to_table": row[2],
            "to_column": row[4],
        }
        for row in rows
    ]


def get_schema_snapshot():
    """Return the live SQLite schema without reading application data rows."""
    connection = get_db_connection()
    try:
        table_names = [
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        ]

        tables = {}
        for table_name in table_names:
            tables[table_name] = {
                "name": table_name,
                "columns": _column_metadata(connection, table_name),
                "foreign_keys": _foreign_key_metadata(connection, table_name),
            }
    finally:
        connection.close()

    groups = []
    assigned_tables = set()
    for group_name, group_definition in TABLE_GROUPS.items():
        group_tables = [
            tables[name]
            for name in table_names
            if name in group_definition["tables"]
        ]
        if group_tables:
            groups.append(
                {
                    "name": group_name,
                    "description": group_definition["description"],
                    "tables": group_tables,
                }
            )
            assigned_tables.update(table["name"] for table in group_tables)

    uncategorized = [tables[name] for name in table_names if name not in assigned_tables]
    if uncategorized:
        groups.append(
            {
                "name": "Other tables",
                "description": "Tables discovered in the live database that are not yet categorized.",
                "tables": uncategorized,
            }
        )

    logical_relationships = [
        {
            "from_table": from_table,
            "from_column": from_column,
            "to_table": to_table,
            "to_column": to_column,
            "cardinality": cardinality,
            "label": label,
        }
        for (
            from_table,
            from_column,
            to_table,
            to_column,
            cardinality,
            label,
        ) in LOGICAL_RELATIONSHIPS
        if from_table in tables and to_table in tables
    ]

    enforced_foreign_keys = sum(
        len(table["foreign_keys"]) for table in tables.values()
    )
    return {
        "groups": groups,
        "relationships": logical_relationships,
        "table_count": len(table_names),
        "enforced_foreign_keys": enforced_foreign_keys,
    }
