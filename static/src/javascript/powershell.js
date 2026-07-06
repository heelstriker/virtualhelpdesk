
function runCommand(command){

    showTerminal(commands[command]);

}


const prompt = "PS C:\\Users\\Administrator>";


function showTerminal(output){

    output += `
    
    ${prompt}<span class='terminal-cursor'></span>`;

    document.getElementById("terminalOutput").innerHTML = output;
    document.getElementById("terminalPopup").style.display = "flex";

}



const commands = {

printer:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Printer

Name                Status      Driver
-----------------------------------------------------
Canon-ACC01         Online      Canon UFR II
HP-HR01             Online      HP Universal
Epson-MKT01         Offline     Epson ESC/P
`,
    
service:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Service

Status Name DisplayName
---------------------------------------------------------
Running Spooler Print Spooler
Running W32Time Windows Time
Running LanmanWorkstation Workstation
Stopped Fax Fax Service
`,
        
    
psdrive:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-PSDrive

Name Used(GB) Free(GB) Provider     Root
---------------------------------------------------------
C    118      220      FileSystem   C:\\
A    85       415      FileSystem   \\\\NYCSERVER01\\Accounting
H    42       258      FileSystem   \\\\LAXSERVER01\\HR_Shared
`,
 
                             
testconnection:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Test-Connection LAXSERVER01

Source        Destination      IPV4Address       Bytes    Time(ms)
-----------------------------------------------------------------------
LAXACTPC001   LAXSERVER01      192.168.100.10    32       1
LAXACTPC001   LAXSERVER01      192.168.100.10    32       1
LAXACTPC001   LAXSERVER01      192.168.100.10    32       2
LAXACTPC001   LAXSERVER01      192.168.100.10    32       1
`,


hotfix:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-HotFix

Source Description HotFixID InstalledOn
---------------------------------------------------------------
LAXACTPC001 Update KB5062553 07/02/2026
LAXACTPC001 Security Update KB5061007 06/12/2026
LAXACTPC001 Update KB5059806 05/18/2026
LAXACTPC001 Update KB5056579 04/09/2026
`,


computerinfo:
`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-ComputerInfo

CsName                 : LAXACTPC001
WindowsProductName     : Windows 11 Enterprise
WindowsVersion         : 24H2
OsArchitecture         : 64-bit
CsManufacturer         : Dell Inc.
CsModel                : OptiPlex 7420
CsProcessors           : Intel(R) Core(TM) i7-13700
CsTotalPhysicalMemory  : 32 GB
`,

netadapter:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-NetAdapter

Name           InterfaceDescription            Status     LinkSpeed
-----------------------------------------------------------------------
Ethernet       Intel(R) Ethernet I219-LM       Up         1 Gbps
Wi-Fi          Intel(R) Wi-Fi 6 AX201          Disconnected 0 Mbps
`,


process:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Process

Handles NPM(K) PM(M) CPU(s) ProcessName
---------------------------------------------------------
340     25     180   10.23 explorer
512     48     320   56.72 chrome
215     18      95    2.15 Teams
148     10      60    0.81 OneDrive
`,


ipconfig:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> ipconfig

Windows IP Configuration

Ethernet adapter Ethernet

IPv4 Address . . . . . . : 192.168.100.21
Subnet Mask . . . . . . : 255.255.255.224
Default Gateway . . . . : 192.168.100.1
DNS Servers . . . . . . : 192.168.100.2
`,
  
nslookup:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\UC:\\Users\\Administratorsers\Administrator> nslookup LAXSERVER01

Server:  dns.bananacorp.local
Address: 192.168.100.2

Name:    LAXSERVER01
Address: 192.168.100.10
`,    
 
      
resolvednsname:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Resolve-DnsName LAXSERVER01

Name Type TTL Section IPAddress
-------------------------------------------------------
LAXSERVER01 A 600 Answer 192.168.100.10
`,

wmiobject:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-WmiObject Win32_ComputerSystem

Manufacturer : Dell Inc.
Model        : OptiPlex 7420
TotalMemory  : 34359738368
UserName     : BANANACORP\Administrator
`,


volume:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Volume

DriveLetter FileSystem SizeRemaining Size
---------------------------------------------------------
C           NTFS       220 GB        338 GB
D           NTFS       450 GB        500 GB
`,
        
wingetlist:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> winget list

Name                     Version
---------------------------------------------------------
Google Chrome            137.0.7151
Microsoft Teams          25153.1002
Adobe Acrobat Reader     25.001
7-Zip                    24.09
Notepad++                8.8.1
`,

wingetinstall:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> winget install "Google Chrome"

Found Google Chrome [Google.Chrome]
Downloading...
██████████████████████████████ 100%

Installing...

Successfully installed Google Chrome.
`,

smbmapping:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-SmbMapping

LocalPath RemotePath                          Status
---------------------------------------------------------------
A:        \\NYCSERVER01\Accounting Shared     OK
G:        \\LAXSERVER01\General               OK
H:        \\LAXSERVER01\HR_Shared             OK
I:        \\LAXSERVER01\IT_Shared             OK
M:        \\LAXSERVER01\Marketing_Shared      OK
O:        \\LAXSERVER01\Operation_Shared      Disconnected
S:        \\NYCSERVER01\Sales_Shared          OK
Z:        \\LAXSERVER01\System                OK
`,

childitem:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-ChildItem A:\\

Directory: A:\

Mode LastWriteTime Length Name
---------------------------------------------------------
d----- 07/01/2026 Reports
d----- 06/18/2026 Payroll
d----- 06/30/2026 Invoices
-a---- 07/02/2026 08:21 153284 Budget2026.xlsx
-a---- 06/28/2026 15:40 82213 AP_Report.pdf
`,
                                    
arpa:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> arp -a

Interface: 192.168.100.21 --- 0x6

Internet Address Physical Address Type
---------------------------------------------------------
192.168.100.1 00-15-5d-01-10-01 Dynamic
192.168.100.10 00-15-5d-01-10-10 Dynamic
192.168.100.20 00-15-5d-01-10-20 Dynamic
192.168.100.50 00-15-5d-01-10-50 Dynamic
`,

routeprint:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> route print

===========================================================================
Interface List
11...00 15 5d 01 10 21......Intel(R) Ethernet I219-LM
===========================================================================

IPv4 Route Table

Network Destination Netmask Gateway
----------------------------------------------------------
0.0.0.0 0.0.0.0 192.168.100.1
127.0.0.0 255.0.0.0 On-link
192.168.100.0 255.255.255.224 On-link
`,
                                                                                                                                                    
smbshare:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-SmbShare

Name Path Description
---------------------------------------------------------------------------
Accounting D:\Shares\Accounting Accounting Shared Folder
General D:\Shares\General General Documents
HR_Shared D:\Shares\HR Human Resources
IT_Shared D:\Shares\IT IT Department
Marketing_Shared D:\Shares\Marketing Marketing Files
Operation_Shared D:\Shares\Operations Operations
System D:\System System Files
`,

disk:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Disk

Number Friendly   Name          Size   Partition Style
------------------------------------------------------------
0      Samsung    SSD 990 Pro   1 TB   GPT
1      WD Blue    HDD           2 TB   GPT
`,

partition:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Partition

DiskPath DriveLetter Size
-----------------------------------------
Disk 0   C           500 GB
Disk 0   D           500 GB
Disk 1   E           2 TB
`,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

acl:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Acl "\\LAXSERVER01\HR_Shared"

Path Owner
------------------------------------------------
Microsoft.PowerShell.Core\FileSystem::\\LAXSERVER01\HR_Shared
BANANACORP\Domain Admins

Access
------------------------------------------------
HR Team             Allow   FullControl
IT Administrators   Allow   FullControl
Accounting Team     Deny    Read
Everyone            Deny    Write
`,

package:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Package

Name                      Version       Provider
-------------------------------------------------------------
Google Chrome             137.0.7151    Programs
Microsoft Teams           25153.1002    Programs
Adobe Acrobat Reader      25.001        Programs
7-Zip                     24.09         Programs
Notepad++                 8.8.1         Programs
`,
           
appxpackage:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-AppxPackage

Name Version
-------------------------------------------------------------
Microsoft.WindowsCalculator 11.2503.0
Microsoft.WindowsStore 22505.1401
Microsoft.WindowsTerminal 1.22.10352
Microsoft.Paint 11.2502.1         
`,
                                                                                                                                                                                                                                                                                


wingetsearch:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> winget search chrome

Name                         Id                         Version
----------------------------------------------------------------------
Google Chrome                Google.Chrome             137.0.7151
Google Chrome Beta           Google.Chrome.Beta        138.0.7200
Google Chrome Dev            Google.Chrome.Dev         139.0.7215
`,


wingetupgrade:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> winget upgrade

Name                     Id                      Version     Available
---------------------------------------------------------------------------
Google Chrome            Google.Chrome          137.0       138.0
Notepad++                Notepad++.Notepad++   8.8.0       8.8.1
7-Zip                    7zip.7zip             24.08       24.09
`,


wingetuninstall:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> winget uninstall "Google Chrome"

Found Google Chrome

Uninstalling...
█████████████████████████████ 100%

Successfully uninstalled Google Chrome.
`,


msiexec:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Start-Process msiexec.exe -ArgumentList "/i ChromeEnterprise.msi"

Launching Windows Installer...

Installing Google Chrome Enterprise...

Installation completed successfully.

`,


setupexe:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Start-Process .\\setup.exe

Launching installer...

BananaVPN Client Setup

Installation completed successfully.

`,

eventlog:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-EventLog -LogName System -Newest 5

Time                 EntryType    Source              EventID
---------------------------------------------------------------------
07/04/2026 09:15     Information  Service Control     7036
07/04/2026 09:13     Warning      DNS Client          1014
07/04/2026 09:10     Error        Disk               7
07/04/2026 09:08     Information  EventLog           6005
07/04/2026 09:01     Information  Kernel-General     12

`,

winevent:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-WinEvent -LogName Security -MaxEvents 5

TimeCreated           Id    Level      Message
---------------------------------------------------------------------------
07/04/2026 09:12      4624  Information Successful logon
07/04/2026 09:11      4672  Information Special privileges assigned
07/04/2026 09:05      4625  Warning     Failed logon
07/04/2026 08:57      4634  Information Logoff
07/04/2026 08:42      4624  Information Successful logon

`,

localuser:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-LocalUser

Name                 Enabled Description
--------------------------------------------------------------
Administrator        True    Built-in administrator
Helpdesk             True    IT Support Account
Training             False   Training Account
Guest                False   Built-in guest account
`,

localgroup:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-LocalGroup

Name
---------------------------------------
Administrators
Backup Operators
Power Users
Remote Desktop Users
Users
`,

groupmember:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-LocalGroupMember Administrators

Name                           PrincipalSource
---------------------------------------------------------
Administrator                  Local
BANANACORP\\IT_Admins           Active Directory
BANANACORP\\Helpdesk            Active Directory
`,

                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                   
};




function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";
}







