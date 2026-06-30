from services.db import get_db_connection
import sqlite3

def get_dashboard_summary():

    conn = get_db_connection()
    cursor = conn.cursor()

    # total
    total_devices = cursor.execute("SELECT COUNT(*) FROM devices").fetchone()[0]


    # software missing count
    
    ct_alert_software_missing = cursor.execute("""
        SELECT COUNT(*)
        FROM software
        WHERE installed = 0
    """).fetchone()[0]

    # Missing Patch count

    ct_alert_patch_missing = cursor.execute("""
        SELECT COUNT(*)
        FROM patches
        WHERE installed = 0
    """).fetchone()[0]

    # offline devices count
    ct_alert_offline = cursor.execute("""
        SELECT COUNT(*)
        FROM devices
        WHERE status = 'Offline'
    """).fetchone()[0]


    # Windows10 PC count
    ct_alert_windows10 = cursor.execute("""
        SELECT COUNT(*)
        FROM hardware
        WHERE os = 'Windows 10'
    """).fetchone()[0]

    alert_count = (ct_alert_software_missing + ct_alert_patch_missing + ct_alert_offline + ct_alert_windows10)
    
    #Compliant Device (total device - union join remove duplicate hostname to count total unique risk devices as risk devices)
    
    cursor.execute("""
    DROP VIEW IF EXISTS device_risks
    """)              

    cursor.execute(""" 
    CREATE VIEW device_risks AS
        
        SELECT hostname, 'Missing Patch' AS reason
        FROM patches
        WHERE installed = 0           
   
        UNION           
        
        SELECT hostname, 'Missing Software' 
        FROM software
        WHERE installed = 0
                   
        UNION

        SELECT hostname, 'Windows 10'
        FROM hardware
        WHERE os LIKE '%Windows 10%'
                   
        UNION

        SELECT hostname, 'Offline'
        FROM devices
        WHERE status = 'Offline'
    """)


    #Get total risk devices

    risk_devices = cursor.execute("""
    SELECT COUNT (DISTINCT hostname)
    FROM device_risks
    """).fetchone()[0]
  
  
    #Get Risk Breakdown graph

    risk_breakdown = cursor.execute("""
    
        SELECT reason, COUNT(*)
        FROM device_risks
        GROUP BY reason
        ORDER BY COUNT(*) DESC
    """).fetchall()


    conn.close()

    compliant_devices = (total_devices - risk_devices)
    risk_labels = [row[0] for row in risk_breakdown]
    risk_counts = [row[1] for row in risk_breakdown]  
    compliance_percent = round(
        (compliant_devices / total_devices) * 100
    )
    risk_percent = 100 - compliance_percent

    return {
        "total_devices": total_devices,

        "alert_count": alert_count,
        
        "risk_devices": risk_devices,

        "compliant_devices": compliant_devices,

        "ct_alert_windows10": ct_alert_windows10,
        "ct_alert_software_missing":ct_alert_software_missing,
        "ct_alert_patch_missing":ct_alert_patch_missing,
        "ct_alert_offline":ct_alert_offline,
        

        "compliance_percent": compliance_percent,
        "risk_percent": risk_percent,
        
        "risk_labels" : risk_labels,
        "risk_counts" : risk_counts
        
    }

def get_risk_devices():

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT
            devices.hostname,
            devices.owner,
            devices.department,
            devices.status

        FROM devices 

        WHERE devices.hostname IN (

            SELECT hostname
            FROM software
            WHERE installed = 0

            UNION

            SELECT hostname
            FROM patches
            WHERE installed = 0

            UNION

            SELECT hostname
            FROM devices
            WHERE status = 'Offline'

        )

        ORDER BY devices.hostname

    """).fetchall()

    conn.close()

    return rows
    
def get_device_status_summary():

    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT
            status,
            COUNT(*) AS count
        FROM devices
        GROUP BY status
        ORDER BY count DESC
    """).fetchall()

    conn.close()

    return rows

