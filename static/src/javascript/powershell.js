
function runCommand(command){

    showTerminal(commands[command]);

}

function showTerminal(output){

    output += "\n\nPS C:\\Users\\Administrator> <span class='terminal-cursor'></span>";

    document.getElementById("terminalOutput").innerHTML = output;

    document.getElementById("terminalPopup").style.display = "flex";

}

const prompt = "PS C:\\Users\\Administrator>";



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

PS C:\Users\Administrator> Get-ComputerInfo

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

PS C:\Users\Administrator> Get-NetAdapter

Name           InterfaceDescription            Status     LinkSpeed
-----------------------------------------------------------------------
Ethernet       Intel(R) Ethernet I219-LM       Up         1 Gbps
Wi-Fi          Intel(R) Wi-Fi 6 AX201          Disconnected 0 Mbps
`,


process:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Get-Process

Handles NPM(K) PM(M) CPU(s) ProcessName
---------------------------------------------------------
340     25     180   10.23 explorer
512     48     320   56.72 chrome
215     18      95    2.15 Teams
148     10      60    0.81 OneDrive

PS C:\Users\Administrator>
`,


ipconfig:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> ipconfig

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

PS C:\Users\Administrator> nslookup LAXSERVER01

Server:  dns.bananacorp.local
Address: 192.168.100.2

Name:    LAXSERVER01
Address: 192.168.100.10

`,    
 
      
resolvednsname:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Resolve-DnsName LAXSERVER01

Name Type TTL Section IPAddress
-------------------------------------------------------
LAXSERVER01 A 600 Answer 192.168.100.10`

`,

wmiobject:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Get-WmiObject Win32_ComputerSystem

Manufacturer : Dell Inc.
Model        : OptiPlex 7420
TotalMemory  : 34359738368
UserName     : BANANACORP\Administrator

`,


volume:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Get-Volume

DriveLetter FileSystem SizeRemaining Size
---------------------------------------------------------
C           NTFS       220 GB        338 GB
D           NTFS       450 GB        500 GB

`,
        
wingetlist:
`
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> winget list

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

PS C:\Users\Administrator> winget install "Google Chrome"

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

PS C:\Users\Administrator> Get-SmbMapping

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

PS C:\Users\Administrator> Get-ChildItem A:\

Directory: A:\

Mode LastWriteTime Length Name
---------------------------------------------------------
d----- 07/01/2026 Reports
d----- 06/18/2026 Payroll
d----- 06/30/2026 Invoices
-a---- 07/02/2026 08:21 153284 Budget2026.xlsx
-a---- 06/28/2026 15:40 82213 AP_Report.pdf
`,
                                     
                                        
            
                                    
};



function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";
}







