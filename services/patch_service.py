import sqlite3
from services.db import get_db_connection
from datetime import datetime

# KB5062553 Patch installation trend overall company

def get_patch_progress():

    conn = get_db_connection()
    cursor = conn.cursor()
   
    patch_trend = cursor.execute("""
    SELECT
        install_date,
        COUNT(*)
    FROM patches
    WHERE patch='KB5062553'
    AND installed=1
    AND applicable = "YES"
    GROUP BY install_date
    ORDER BY install_date
    """).fetchall()

    
    trend_dates = [row[0] for row in patch_trend]
    trend_counts = [row[1] for row in patch_trend]

    #obtain total devicves drom device table
    total_devices = cursor.execute("""
    SELECT COUNT(*)
    FROM devices
    """).fetchone()[0]

    conn.close()


    #calculate accumulating percentage for company-wide project progress

    running = 0

    trend_percent = []

    for row in patch_trend:

        running += row[1]

        percent = round(
            running / total_devices * 100,
            1
        )

        trend_percent.append(percent)

    #Format date display for the chart 

    trend_dates = [

    datetime.strptime(
        row[0],
        "%Y-%m-%d"
    ).strftime("%b %d")

    for row in patch_trend

    ]

    return{
        "trend_dates": trend_dates,
        "trend_counts": trend_counts,
        "trend_percent": trend_percent,
       
    }

# Installation progress by wave

def get_wave_progress():

    conn = get_db_connection()
    cursor = conn.cursor()
   
    wave_data = cursor.execute("""
     SELECT
        deployment_window,
        COUNT(DISTINCT hostname) AS total,
        SUM(CASE WHEN installed = 1 THEN 1 ELSE 0 END) AS installed
    FROM patches
    WHERE patch = 'KB5062553'
    AND applicable = 'YES'
    GROUP BY deployment_window
    ORDER BY
    CASE deployment_window
        WHEN 'Wave 1' THEN 1
        WHEN 'Wave 2' THEN 2
        WHEN 'Wave 3' THEN 3
        WHEN 'Wave 4' THEN 4
    END
    """).fetchall()

      
    conn.close()



   #Calculate accumulte installation results by each wave
   
    trend_wave = []
    wave_percent = []

    for wave, total, installed in wave_data:
        trend_wave.append(wave)

        percent = round((installed / total) * 100, 1) if total else 0
        wave_percent.append(percent)


    return {
        "percent":percent,
        "trend_wave": trend_wave,
        "wave_percent": wave_percent,
    }




def get_department_progress():

    conn = get_db_connection()
    cursor = conn.cursor()
   
    dept_data = cursor.execute("""
    SELECT
        d.department,
        COUNT(DISTINCT d.hostname) AS total,
        SUM(CASE WHEN p.installed = 1 THEN 1 ELSE 0 END) AS installed
    FROM devices d
    LEFT JOIN patches p
        ON d.hostname = p.hostname
        AND p.patch = 'KB5062553'
        AND p.applicable = 'YES'
        GROUP BY d.department
        ORDER BY installed DESC
    """).fetchall()
    
    
    conn.close()


   #Calculate accumulte installation results by each department
   
    trend_dept = []
    dept_percent = []
    dept_counts = []

    for dept, total, installed in dept_data:
        trend_dept.append(dept)
        dept_counts.append(installed)

        percent = round((installed / total) * 100, 1) if total else 0
        dept_percent.append(percent)


    print("DEPT TREND DATA TEST")
    print(trend_dept)
    print(dept_percent)
    print(dept_counts)
    print("END TESTS")

    return {
        "trend_dept": trend_dept,
        "dept_counts": dept_counts,
        "dept_percent": dept_percent
    }
