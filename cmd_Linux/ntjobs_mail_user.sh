#!/bin/bash
# ==============================================================
# ntjobs_mail_user.sh
# Invia il comando SYS.MAIL.USER ad aiJobsOS2.
# Il sistema mandera una mail di test all'utente admin
# configurato in USER_MAIL del file ntjobs_users.csv.
# ==============================================================

USERPATH="/opt/ntjobsai2/users/admin"

echo "Creazione jobs.ini SYS.MAIL.USER..."

cat > "$USERPATH/jobs.ini" << 'EOF'
[CONFIG]
TYPE=NTJOBS.APP.1.0
NAME=SYS_MAIL_USER

[JOB_MAIL_USER]
ACTION=SYS.MAIL.USER
EOF

if [ $? -ne 0 ]; then
    echo "ERRORE: impossibile creare jobs.ini in $USERPATH"
    exit 1
fi

echo "OK - aiJobsOS2 inviera una mail all'utente corrente al prossimo ciclo."
