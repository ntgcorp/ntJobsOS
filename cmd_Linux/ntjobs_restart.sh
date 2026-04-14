#!/bin/bash
# ==============================================================
# ntjobs_reboot.sh
# Invia il comando SYS.REBOOT ad aiJobsOS2.
# Lo script Python crea ntjobs.shutdown e termina.
# NOTA: il launcher attuale mappa il reboot su shutdown -h now.
# Per abilitare il riavvio effettivo aggiungere in aiJobsOS2.sh:
#   if [ -f "ntjobs.reboot" ]; then shutdown -r now; fi
# e in aiJobsOS2.py cambiare il flag di SYS.REBOOT
# da ntjobs.shutdown a ntjobs.reboot.
# ==============================================================

USERPATH="/opt/ntjobsai2"

echo "Creazione jobs.ini SYS.REBOOT..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_REBOOT

[JOB_REBOOT]
ACTION=SYS.REBOOT
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - Il sistema si spegnera al termine del ciclo corrente."
echo "NOTA: per il riavvio effettivo aggiornare aiJobsOS2.sh come da istruzioni nel file."
