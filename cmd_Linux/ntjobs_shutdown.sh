#!/bin/bash
# ==============================================================
# ntjobs_shutdown.sh
# Invia il comando SYS.SHUTDOWN ad aiJobsOS2.
# Lo script Python crea ntjobs.shutdown e termina.
# Il launcher rileva ntjobs.shutdown ed esegue shutdown -h now.
# ==============================================================

USERPATH="/opt/ntjobsai2"

echo "Creazione jobs.ini SYS.SHUTDOWN..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_SHUTDOWN

[JOB_SHUTDOWN]
COMMAND=SYS.SHUTDOWN
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - Il sistema si spegnera al termine del ciclo corrente."
