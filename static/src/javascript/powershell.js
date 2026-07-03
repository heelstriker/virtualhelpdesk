
function runCommand(command){

    switch(command){

        case "printer":
            printerCommand();
            break;

        case "service":
            serviceCommand();
            break;

        case "psdrive":
            psdriveCommand();
            break;
    }

}



function printerCommand(){

    let output = "";

    
        output=`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Printer

Name                Status      Driver
-----------------------------------------------------
Canon-ACC01         Online      Canon UFR II
HP-HR01             Online      HP Universal
Epson-MKT01         Offline     Epson ESC/P

PS C:\\Users\\Administrator>`;
    
    

    document.getElementById("terminalOutput").textContent = output;

    document.getElementById("terminalPopup").style.display = "flex";

}

function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";

}



function serviceCommand(){

    let output = "";

    
        output=`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\\Users\\Administrator> Get-Service

Status Name DisplayName
---------------------------------------------------------
Running Spooler Print Spooler
Running W32Time Windows Time
Running LanmanWorkstation Workstation
Stopped Fax Fax Service

PS C:\\Users\\Administrator>`;
    
    

    document.getElementById("terminalOutput").textContent = output;

    document.getElementById("terminalPopup").style.display = "flex";

}

function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";

}




function psdriveCommand(){

    let output = "";

    
        output=`Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator> Get-PSDrive

Name Used(GB) Free(GB) Provider     Root
---------------------------------------------------------
C    118      220      FileSystem   C:\
A    85       415      FileSystem   \\NYCSERVER01\Accounting
H    42       258      FileSystem   \\LAXSERVER01\HR_Shared

PS C:\\Users\\Administrator>`;
    
    

    document.getElementById("terminalOutput").textContent = output;

    document.getElementById("terminalPopup").style.display = "flex";

}

function closeTerminal(){

    document.getElementById("terminalPopup").style.display = "none";

}






