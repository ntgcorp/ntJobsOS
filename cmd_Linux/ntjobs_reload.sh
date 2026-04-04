#!/bin/bash
# ==============================================================
# ntjobs_reload.sh
# Invia il comando SYS.RELOAD ad aiJobsOS2.
# Lo script Python crea ntjobs.restart e termina.
# Il launcher rileva ntjobs.restart e riparte dal while (continue),
# ricaricando da zero config, utenti e azioni.
# ==============================================================

USERPATH="/opt/ntjobsai2"

echo "Creazione jobs.ini SYS.RELOAD..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_RELOAD

[JOB_RELOAD]
COMMAND=SYS.RELOAD
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - aiJobsOS2 ripartira con la configurazione aggiornata."
