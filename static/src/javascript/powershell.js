
function runCommand(command){

    switch(command){

        case "printer":
            printerCommand();
            break;

        case "service":
            serviceCommand();
            break;

        case "process":
            processCommand();
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

