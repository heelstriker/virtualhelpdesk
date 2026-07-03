import sqlite3
from services.db import get_db_connection


def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS devices")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        owner TEXT,
        department TEXT,

        ip_address TEXT,
        subnet TEXT,
        gateway TEXT,

        status TEXT,
        last_seen TEXT,

        location TEXT,
        cost_center TEXT,
        asset_tag TEXT,
        monthly_cost TEXT,

        serial_number TEXT,

        purchase_date TEXT,
        warranty_expiration TEXT,
        retirement_date TEXT
                   
    )
    """)
    
    cursor.execute("DROP TABLE IF EXISTS software")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        software_name TEXT,
        installed INTEGER,
	required TEXT
    )
    """)

    cursor.execute("DROP TABLE IF EXISTS hardware")
    cursor.execute("""
    Create TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        os TEXT,
        manufacturer TEXT,
        model TEXT,
        device_type TEXT,
        memory_gb INTEGER,
        disk_gb INTEGER,           
        cpu TEXT,
        serial_number TEXT
                      
    )
    """)
    cursor.execute("DROP TABLE IF EXISTS printers")
    cursor.execute("""
    Create TABLE IF NOT EXISTS printers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        printer_name TEXT,
        installed INTEGER,
        driver_name TEXT
    )
    """)

    cursor.execute("DROP TABLE IF EXISTS network_drives")
    cursor.execute("""
    Create TABLE IF NOT EXISTS network_drives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        network_drive TEXT,
        connected INTEGER,
        drive_name TEXT,
        status TEXT
    )
    """)
    cursor.execute("DROP TABLE IF EXISTS patches")
    cursor.execute("""
    Create TABLE IF NOT EXISTS patches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        patch TEXT,
        description TEXT,
        installed INTEGER,
        install_date TEXT,
        release_month TEXT,
        deployment_date TEXT,
        applicable TEXT,
        downloaded TEXT,
        deployment_window TEXT
    )
    """)

    cursor.execute("DROP TABLE IF EXISTS server_catalog")
    cursor.execute("""
    Create TABLE IF NOT EXISTS server_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        role TEXT,
        site TEXT,
	ip_address TEXT,
	operating_system TEXT,
	environment TEXT,
	status TEXT,
	cpu TEXT,
	memory_gb INTEGER,
	storage_tb TEXT,
	uptime_days INTEGER,
	patch_status TEXT,
	backup_status TEXT,
	monitoring TEXT,
	last_checkin TEXT,
        description TEXT
    )
    """)


    cursor.execute("DROP TABLE IF EXISTS patch_catalog")
    cursor.execute("""
    Create TABLE IF NOT EXISTS patch_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patch TEXT,
        description TEXT,
        target_os TEXT,
	required_software TEXT,
	release_month TEXT,
	severity TEXT
    )
    """)


    cursor.execute("DROP TABLE IF EXISTS software_catalog")
    cursor.execute("""
    Create TABLE IF NOT EXISTS software_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        software_name TEXT,
        vendor TEXT,
        category TEXT,
	description TEXT,
	required_device_type TEXT,
	required TEXT,
	current_version TEXT,
	monthly_cost TEXT,
	license_type TEXT,
	install_risk TEXT,
	support_status TEXT,
	auto_update TEXT
    )
    """)

    cursor.execute("DROP TABLE IF EXISTS printer_catalog")
    cursor.execute("""
    Create TABLE IF NOT EXISTS printer_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        printer_id TEXT,
        hostname TEXT,
        department TEXT,
	manufacturer TEXT,
	model TEXT,
	printer_type TEXT,
	ip_address TEXT,
	status TEXT,
	location TEXT,
	cost_center TEXT
    )
    """)

    cursor.execute("DROP TABLE IF EXISTS network_drive_catalog")
    cursor.execute("""
    Create TABLE IF NOT EXISTS network_drive_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_letter TEXT,
        drive_name TEXT,
        unc_path TEXT,
	    server TEXT,
	    department TEXT,
	    permission TEXT,
	    criticality TEXT,
	    capacity_gb TEXT,
	    used_gb TEXT,
	    backup TEXT,
	    status TEXT
    )
    """)



    # for development purpose use drop for delete table: 
    # cursor.execute("DROP TABLE IF EXISTS hardware")
    # use ALTER TABLE for table configuration chagne after production


    conn.commit()
    conn.close()


    print("Database schema created")