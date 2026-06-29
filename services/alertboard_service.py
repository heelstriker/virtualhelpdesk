def generate_alertboard(summary):

    messages = []


    if summary["ct_alert_patch_missing"] > 0:
        messages.append(
            f"{summary['ct_alert_patch_missing']} critical patches missing. Schedule remediation before month-end."
        )

    if summary["ct_alert_offline"] > 0:
        messages.append(
            f"{summary['ct_alert_offline']} devices currently offline for more than 7 days. Verify asset status."
        )

    if summary["ct_alert_software_missing"] > 0:
        messages.append(
            f"{summary['ct_alert_software_missing']} devices missing required software."
        )

    if summary["ct_alert_windows10"] > 0:
        messages.append(
            f"{summary['ct_alert_windows10']} Windows 10 devices remaining. Recommend replacement planning during next user interaction"
        )


    return messages