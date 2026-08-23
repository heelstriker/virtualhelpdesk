from services.db import get_db_connection


TABLE_GROUPS = (
    {
        "id": "endpoint-core",
        "label": "Endpoint Core",
        "description": "Primary device identity and its recorded hardware profile.",
        "tables": ("devices", "hardware"),
    },
    {
        "id": "operational-state",
        "label": "Operational State",
        "description": "Per-endpoint software, patch, printer, and network-drive state.",
        "tables": ("software", "patches", "printers", "network_drives"),
    },
    {
        "id": "reference-catalogs",
        "label": "Reference Catalogs",
        "description": "Reusable definitions for infrastructure, software, patches, printers, and shared drives.",
        "tables": (
            "server_catalog",
            "software_catalog",
            "patch_catalog",
            "printer_catalog",
            "network_drive_catalog",
            "switch_catalog",
        ),
    },
    {
        "id": "infrastructure-map",
        "label": "Infrastructure Map",
        "description": "Recorded links between managed network and infrastructure assets.",
        "tables": ("network_topology",),
    },
)


TABLE_LABELS = {
    "devices": "Devices",
    "hardware": "Hardware",
    "software": "Software State",
    "patches": "Patch State",
    "printers": "Printer State",
    "network_drives": "Network Drive State",
    "server_catalog": "Server Catalog",
    "software_catalog": "Software Catalog",
    "patch_catalog": "Patch Catalog",
    "printer_catalog": "Printer Catalog",
    "network_drive_catalog": "Network Drive Catalog",
    "switch_catalog": "Switch & Router Catalog",
    "network_topology": "Network Topology",
}


ALL_TABLE_NAMES = [
    table_name
    for group in TABLE_GROUPS
    for table_name in group["tables"]
]


RELATIONSHIPS = (
    ("devices", "hostname", "hardware", "hostname", "One device identity to one recorded hardware profile"),
    ("devices", "hostname", "software", "hostname", "One device to many software-state records"),
    ("devices", "hostname", "patches", "hostname", "One device to many patch-state records"),
    ("devices", "hostname", "printers", "hostname", "One device to many assigned-printer records"),
    ("devices", "hostname", "network_drives", "hostname", "One device to many mapped-drive records"),
    ("software_catalog", "software_name", "software", "software_name", "Software definition to endpoint installation state"),
    ("patch_catalog", "patch", "patches", "patch", "Patch definition to endpoint deployment state"),
    ("network_drive_catalog", "drive_name", "network_drives", "drive_name", "Shared-drive definition to endpoint connection state"),
    ("server_catalog", "hostname", "network_drive_catalog", "server", "Server identity to hosted shared-drive definitions"),
    ("switch_catalog", "device_id", "devices", "switch_id", "Network device to connected endpoint switch assignment"),
    ("switch_catalog", "device_id", "server_catalog", "switch_id", "Network device to connected server switch assignment"),
)


def get_schema_overview():
    """Return a live, presentation-ready view of the configured SQLite schema."""

    conn = get_db_connection()
    try:
        existing_tables = {
            row["name"]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                """
            ).fetchall()
        }

        groups = []
        total_columns = 0
        total_rows = 0

        for group in TABLE_GROUPS:
            tables = []
            for table_name in group["tables"]:
                if table_name not in existing_tables:
                    continue

                columns = [
                    {
                        "name": row["name"],
                        "type": row["type"] or "UNSPECIFIED",
                        "required": bool(row["notnull"]),
                        "primary_key": bool(row["pk"]),
                    }
                    for row in conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
                ]
                row_count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
                total_columns += len(columns)
                total_rows += row_count
                tables.append(
                    {
                        "name": table_name,
                        "label": TABLE_LABELS.get(table_name, table_name.replace("_", " ").title()),
                        "columns": columns,
                        "row_count": row_count,
                    }
                )

            if tables:
                groups.append(
                    {
                        "id": group["id"],
                        "label": group["label"],
                        "description": group["description"],
                        "tables": tables,
                    }
                )

        relationships = [
            {
                "source_table": source_table,
                "source_column": source_column,
                "target_table": target_table,
                "target_column": target_column,
                "description": description,
            }
            for source_table, source_column, target_table, target_column, description in RELATIONSHIPS
            if source_table in existing_tables and target_table in existing_tables
        ]

        return {
            "groups": groups,
            "relationships": relationships,
            "table_count": sum(len(group["tables"]) for group in groups),
            "column_count": total_columns,
            "row_count": total_rows,
            "relationship_count": len(relationships),
        }
    finally:
        conn.close()
