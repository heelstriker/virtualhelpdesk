import os
import csv
import sqlite3
from services.db import get_db_connection

def import_csv(filepath):

    with open(
        filepath,
        newline="",
        encoding="utf-8-sig"
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        return list(reader)



def initialize_database():

    print("Importing Devices...")
    device_count = import_devices()   
    print(f"Imported {device_count} devices")  


    print("Importing Hardware...")
    hardware_count = import_hardware()
    print(f"Imported {hardware_count} devices")  


    print("Importing Software...")
    software_count = import_software()
    print(f"Imported {software_count} software")


    print("Importing Printers...")
    printer_count = import_printer()
    print(f"Imported {printer_count} printer")
    
    print("Importing Network Drives...")
    network_drive_count = import_network_drives()
    print(f"Imported {network_drive_count} network drives")
    

    print("Importing Patches...")
    patches_count = import_patches()
    print(f"Imported {patches_count} Patches")
    

    print("Importing Server Catalogs...")
    server_catalog_count = import_server_catalog()
    print(f"Imported {server_catalog_count} Server Catalogs")
    

    print("Importing Patch Catalogs...")
    patch_catalog_count = import_patch_catalog()
    print(f"Imported {patch_catalog_count} Patch Catalogs")
    


    print("Import Complete")



# DB insert process

def import_devices():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(
        BASE_DIR,
        "..",
        "seed_data",
        "devices.csv"
    )

    rows = import_csv(CSV_PATH)

    print("=== DEBUG ===")
    print(type(rows))
    print(len(rows))

    if len(rows) > 0:
        print(rows[0])
        print(rows[0].keys())

    cursor.execute("DELETE FROM devices")


    for row in rows:
      
        cursor.execute("""
        INSERT INTO devices
        (hostname, owner, department, ip_address, subnet, gateway, status, last_seen, location, cost_center, asset_tag, monthly_cost, serial_number, purchase_date, warranty_expiration, retirement_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["hostname"],
            row["owner"],
            row["department"],
            
            row["ip_address"],
            row["subnet"],
            row["gateway"],
            
            row["status"],
            row["last_seen"],
            
            row["location"],
            row["cost_center"],
            row["asset_tag"],
            row["monthly_cost"],

            row["serial_number"],
            
            row["purchase_date"],
            row["warranty_expiration"],
            row["retirement_date"]
                        
            ))

    conn.commit()
 
    cursor.execute("SELECT COUNT(*) FROM devices")
    print(cursor.fetchone())

    conn.close()

    return len(rows)


# Software Table


def import_software():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "software.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM software")

    for row in rows:

        cursor.execute("""
        INSERT INTO software
        (hostname, software_name, installed, required)
        VALUES (?, ?, ?, ?)
        """, (
            row["hostname"],
            row["software_name"],
            row["installed"],
	    row["required"]
        ))

    conn.commit()
    conn.close()

    return len(rows)

# Hardware Catalog Spec Table

def import_hardware():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "hardware.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM hardware")

    for row in rows:

        cursor.execute("""
        INSERT INTO hardware
        (hostname,os, manufacturer, model, device_type, memory_gb, disk_gb, cpu, serial_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["hostname"],
            row["os"],
            row["manufacturer"],
            row["model"],
            row["device_type"],

            row["memory_gb"],
            row["disk_gb"],

            row["cpu"],
            row["serial_number"]
            
            ))

    conn.commit()
    conn.close()

    return len(rows)



def import_printer():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "printers.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM printers")

    for row in rows:

        cursor.execute("""
        INSERT INTO printers
        (hostname, printer_name, installed, driver_name)
        VALUES (?, ?, ?, ?)
        """, (
            row["hostname"],
            row["printer_name"],
            row["installed"],
            row["driver_name"]
        ))

    conn.commit()
    conn.close()

    return len(rows)

def import_network_drives():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "network_drives.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM network_drives")

    for row in rows:

        cursor.execute("""
        INSERT INTO network_drives
        (hostname, network_drive, connected, drive_name, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            row["hostname"],
            row["network_drive"],
            row["connected"],
            row["drive_name"],
            row["status"]
            
        ))

    conn.commit()
    conn.close()

    return len(rows)



def import_patches():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "patches.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM patches")

    for row in rows:

        cursor.execute("""
        INSERT INTO patches
        (hostname, patch, description, installed, install_date, release_month, deployment_date, applicable, downloaded, deployment_window)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["hostname"],
            row["patch"],
            row["description"],
            row["installed"],
            row["install_date"],
            row["release_month"],
            row["deployment_date"],
            row["applicable"],
            row["downloaded"],
            row["deployment_window"]
        ))

    conn.commit()
    conn.close()

    return len(rows)

def import_server_catalog():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "server_catalog.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM server_catalog")

    for row in rows:

        cursor.execute("""
        INSERT INTO server_catalog
        (hostname, role, site, ip_address, operating_system, environment, status, cpu, memory_gb, storage_tb, uptime_days, patch_status, backup_status, monitoring, last_checkin, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["hostname"],
            row["role"],
            row["site"],
            row["ip_address"],
            row["operating_system"],
            row["environment"],
            row["status"],
            row["cpu"],
            row["memory_gb"],
            row["storage_tb"],
	    row["uptime_days"],
            row["patch_status"],
	    row["backup_status"],
            row["monitoring"],
            row["last_checkin"],
            row["description"]

        ))

    conn.commit()
    conn.close()

    return len(rows)


def import_patch_catalog():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "patch_catalog.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM patch_catalog")

    for row in rows:

        cursor.execute("""
        INSERT INTO patch_catalog
        (patch, description, target_os, required_software, release_month, severity)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["patch"],
            row["description"],
            row["target_os"],
            row["required_software"],
            row["release_month"],
            row["severity"]
        ))

    conn.commit()
    conn.close()

    return len(rows)

def import_software_catalog():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "software_catalog.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM software_catalog")

    for row in rows:

        cursor.execute("""
        INSERT INTO software_catalog
        (software_name, vendor, category, description, required_device, required, current_version, monthly_cost, license_type, install_risk, support_status, auto_update)
        VALUES (?, ?, ?, ?, ?, ?, ? ,? ,? ,? ,? ,?)
        """, (
            row["software_name"],
            row["vendor"],
            row["category"],
            row["description"],
            row["required_device"],
            row["required"],
	    row["current_version"],
	    row["monthly_cost"],
	    row["license_type"],
	    row["license_risk"],
	    row["support_status"],
	    row["auto_update"]
        ))

    conn.commit()
    conn.close()

def import_printer_catalog():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conn = get_db_connection()
    cursor = conn.cursor()

    CSV_PATH = os.path.join(BASE_DIR, "..", "seed_data", "printer_catalog.csv")

    rows = import_csv(CSV_PATH)

    cursor.execute("DELETE FROM printer_catalog")

    for row in rows:

        cursor.execute("""
        INSERT INTO printer_catalog
        (printer_id, hostname, department, manufacturer, model, printer_type, ip_address, status, location, cost_center)
        VALUES (?, ?, ?, ?, ?, ?, ? ,? ,? ,?)
        """, (
            row["printer_id"],
            row["hostname"],
            row["department"],
            row["manufacturer"],
            row["model"],
            row["printer_type"],
	    row["ip_address"],
	    row["status"],
	    row["location"],
	    row["cost_center"]
        ))

    conn.commit()
    conn.close()



    return len(rows)