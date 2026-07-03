async function runCommand(command){

    if(command==="printer"){

        const response=await fetch("/api/printers");

        const printers=await response.json();

        let output=
`PS C:\\Users\\Administrator> Get-Printer

`;

        output+="Name                Status\n";
        output+="-----------------------------------\n";

        printers.forEach(p=>{

            output+=`${p.printer_name.padEnd(20)}${p.status}\n`;

        });

        document.getElementById("terminal-output").textContent=output;

    }

}