# Virtual Help Desk

A realistic enterprise IT Support simulator built with Flask.

## Features

- Incident Management
- CMDB
- Asset Management
- Device Inventory
- Compliance Dashboard
- Software Installation Tracking

## Technologies

- Python
- Flask
- SQLite
- HTML/CSS
- JavaScript

## Getting Started

```bash
pip install -r requirements.txt
python app.py


# VirtualHelpDesk

## Project Overview

VirtualHelpDesk is a web-based endpoint management and IT support platform designed to simulate real-world enterprise desktop support operations.

The purpose of this project is not only to learn Python programming, but also to understand how modern IT infrastructure is built using a multi-layer architecture consisting of:

* Frontend (HTML/CSS)
* Backend (Python Flask)
* Database (SQLite)
* Automation Layer (PowerShell / Shell Scripts)
* Inventory & Configuration Management

The system is inspired by enterprise endpoint management solutions such as Microsoft Intune, SCCM, ServiceNow CMDB, and internal IT support tools.

---

## Business Objective

The primary objective is to provide a centralized interface for Help Desk and Desktop Support Engineers to:

* View endpoint inventory information
* Track hardware specifications
* Monitor software compliance
* Review patch deployment status
* Execute remote administrative actions
* Identify unsupported or non-compliant devices

The platform acts as a lightweight Configuration Management Database (CMDB) and Endpoint Management System.

---

## Configuration Management Concept

Every managed device stores inventory information including:

* Hostname
* Department
* Owner
* IP Address
* Hardware Specifications
* Installed Software
* Patch Status
* Last Check-in Time

The server maintains a centralized inventory database containing information from all managed endpoints.

This allows administrators to answer questions such as:

* Which computers are still running Windows 10?
* Which devices are missing required software?
* Which devices have not checked in recently?
* Which department owns a particular workstation?
* Which systems require hardware replacement?

---

## Naming Convention and Department Mapping

Hostnames are used to identify device ownership and organizational structure.

Examples:

Accounting Department

Hostname: LAXACTPC002
IP Address: 17.110.120.2
Subnet Mask: 255.255.255.0

IT Department

Hostname: LAXITPC002
IP Address: 17.110.121.2
Subnet Mask: 255.255.255.0

Hostname: LAXITPC003
IP Address: 17.110.121.3
Subnet Mask: 255.255.255.0

Using naming conventions and subnet assignments, the platform can automatically determine department ownership and apply access policies.

---

## Future Access Control Features

Future versions will support department-based authorization rules.

Examples:

* Accounting printers can only be installed on Accounting devices.
* Accounting network drives can only be mapped to Accounting computers.
* Unauthorized software deployment requests will be blocked.
* Devices located in incorrect subnets will be flagged for review.

This simulates common enterprise security and compliance practices.

---

## Technical Learning Goals

This project demonstrates understanding of:

* Python programming
* Flask web development
* SQLite database design
* CRUD operations
* Inventory management systems
* CMDB concepts
* Endpoint management workflows
* PowerShell automation
* IT infrastructure architecture

The project serves as both a learning platform and a portfolio project demonstrating practical IT Support and Systems Administration skills.

created by Takehiro Ito