import sqlite3
import os
from services.db import get_db_connection



def get_all_devices():

    conn = get_db_connection()

    devices = conn.execute(
        """
        SELECT *
        FROM devices
        """
    ).fetchall()

    conn.close()

    return devices


def get_device_by_hostname(hostname):

    conn = get_db_connection()

    device = conn.execute("""
        SELECT * FROM devices
        WHERE hostname = ?
    """, (hostname,)).fetchone()

    conn.close()

    return device


def get_device_software(hostname):

    conn = get_db_connection()

    software = conn.execute("""
        SELECT * FROM software
        WHERE hostname = ?
    """, (hostname,)).fetchall()

    conn.close()

    return software



def get_device_hardware(hostname):

    conn = get_db_connection()

    hardware = conn.execute("""
        SELECT * FROM hardware
        WHERE hostname = ?
    """, (hostname,)).fetchone()

    conn.close()

    return hardware

def get_device_printers(hostname):

    conn = get_db_connection()

    printers = conn.execute("""
        SELECT * FROM printers
        WHERE hostname = ?
    """, (hostname,)).fetchall()

    conn.close()

    return printers


def get_network_drives(hostname):

    conn = get_db_connection()

    network_drives = conn.execute("""
        SELECT * FROM network_drives
        WHERE hostname = ?
    """, (hostname,)).fetchall()

    conn.close()

    return network_drives


def get_patches(hostname):

    conn = get_db_connection()

    patches = conn.execute("""
        SELECT * FROM patches
        WHERE hostname = ?
    """, (hostname,)).fetchall()

    conn.close()

    return patches