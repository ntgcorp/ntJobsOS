#!/bin/bash
# ==============================================================
# aiJobsOS2.sh  –  script di lancio Linux equivalente a aiJobsOs2.cmd
#
# Logica identica al CMD Windows:
#   - All'avvio cancella i file flag residui
#   - Lancia aiJobsOS2.py
#   - Se al ritorno esiste ntjobs.restart  → rilancia (SYS.RELOAD)
#   - Se al ritorno esiste ntjobs.shutdown → esegue shutdown -h now
# ==============================================================

SYSROOT="/opt/ntjobsos"
PYTHON="python3"

cd "$SYSROOT" || { echo "ERRORE: impossibile accedere a $SYSROOT"; exit 1; }

while true; do

    echo "NTJOBSOS.START"

    # Cancella file flag residui del ciclo precedente
    for FLAG in ntjobs.reload ntjobs.restart ntjobs.shutdown; do
        [ -f "$FLAG" ] && rm -f "$FLAG"
    done

    # Lancia lo script Python
    $PYTHON "$SYSROOT/ntjobsos.py"

    # Controlla i file flag al ritorno
    if [ -f "ntjobs.restart" ]; then
        echo "NTJOBSOS.RESTART - riavvio configurazione..."
		shutdown -s now
		break        
    fi	
    if [ -f "ntjobs.restart" ]; then
        echo "NTJOBSOS.RELOAD - riavvio configurazione..."
		continue
    fi	

    if [ -f "ntjobs.shutdown" ]; then
        echo "NTJOBSOS.SHUTDOWN"
        shutdown -h now
        break
    fi

    # Nessun flag → uscita normale
    break

done

echo "NTJOBSOS.END"
