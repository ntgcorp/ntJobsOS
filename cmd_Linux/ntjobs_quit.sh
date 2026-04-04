#!/bin/bash
# ==============================================================
# ntjobs_quit.sh
# Invia il comando SYS.QUIT ad aiJobsOS2.
# Lo script Python termina in modo pulito senza creare
# alcun file flag: il launcher cade fuori dal loop e si chiude.
# ==============================================================

USERPATH="/opt/ntjobsai2"

echo "Creazione jobs.ini SYS.QUIT..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_QUIT

[JOB_QUIT]
COMMAND=SYS.QUIT
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - aiJobsOS2 terminera al prossimo ciclo."
