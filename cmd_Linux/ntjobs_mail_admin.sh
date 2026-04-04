#!/bin/bash
# ==============================================================
# ntjobs_mail_admin.sh
# Invia il comando SYS.MAIL.ADMIN ad aiJobsOS2.
# Il sistema mandera una mail di test all'amministratore
# configurato in ADMIN.EMAIL del file ntjobs_config.ini.
# ==============================================================

USERPATH="/opt/ntjobsai2/users/admin"

echo "Creazione jobs.ini SYS.MAIL.ADMIN..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_MAIL_ADMIN

[JOB_MAIL_ADMIN]
COMMAND=SYS.MAIL.ADMIN
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - aiJobsOS2 inviera una mail all'amministratore al prossimo ciclo."
