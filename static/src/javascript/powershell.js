
function runCommand(command){

    showTerminal(commands[command]);

}

}

function showTerminal(output){

    document.getElementById("terminalOutput").textContent = output;

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

PS C:\\Users\\Administrator>`,
    
    
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

PS C:\\Users\\Administrator>`,
    
    
psdrive:

`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Get-PSDrive

Name Used(GB) Free(GB) Provider     Root
---------------------------------------------------------
C    118      220      FileSystem   C:\
A    85       415      FileSystem   \\NYCSERVER01\Accounting
H    42       258      FileSystem   \\LAXSERVER01\HR_Shared

PS C:\\Users\\Administrator>`;
        
};


showTerminal(output);




function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";

}






