

def calculate_compliance_score(
    software,
    patches,
    printers,
    network_drive
):

    score = 100

    for app in software:

        if app["installed"] == 0:
            score -= 10

    for patch in patches:

        if patch["installed"] == 0:
            score -= 20

    for printer in printers:

        if printer["installed"] == 99:
            score -= 5

    for drive in network_drive:

        if drive["connected"] == 0:
            score -= 5

    if score < 0:
        score = 0

    return score


def generate_alerts(
    hardware,
    software,
    patches,
    printers,
    network_drive
):
    
    print("=== HARDWARE DEBUG ===")
    print(hardware)
    print(type(hardware))


    alerts = []

    if hardware["os"] == "Windows 10":

        alerts.append(
            "⚠ Windows 10 support ended. Upgrade recommended."
        )

    if int(hardware["memory_gb"]) < 8:
        alerts.append(
            "⚠ RAM less than 8GB. The system may run slow."
        )
    if int(hardware["disk_gb"]) < 256:
        alerts.append(
            "⚠ SSD is 256GB or less. Consider upgarding."
        )

    for app in software:

        if app["installed"] == 0:

            alerts.append(
                f"⚠ {app['software_name']} is missing."
            )

    for patch in patches:

        if patch["installed"] == 0:

            alerts.append(
                f"⚠ {patch['patch']} is missing."
            )

    for printer in printers:
        if printer["installed"]==99:
            
            alerts.append(
                f"⚠ Security Alert! Your department does not allow connection to  {printers['printer_name']} printer."
            )
            
    for drive in network_drive:
        if drive["drive_name"]=="System Drive" and drive["connected"]==0:
            alerts.append(
                f"⚠ {drive['network_drive']} is missing. Please re-connect."
            )

    

    return alerts

