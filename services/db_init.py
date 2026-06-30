from services.db import get_db_connection
conn = get_db_connection()

def create_database():

    conn = sqlite3.connect(DB_PATH)
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        software_name TEXT,
        installed INTEGER
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

    # for development purpose use drop for delete table: 
    # cursor.execute("DROP TABLE IF EXISTS hardware")
    # use ALTER TABLE for table configuration chagne after production

    conn.commit()
    conn.close()

    print("Database schema created")