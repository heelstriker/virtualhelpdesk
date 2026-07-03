
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



  
    
      
        
            
};


function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";

}







