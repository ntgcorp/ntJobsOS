DA RIVEDERE - TRASFORMARE IN CLASSE con CHIAMATA solo di MAILSEND

# ntJobs.Mail - Modulo
# -----------------------------------------------------------
# Invio mail massive parametrizzato
# Formato ntJobs.Mail: ID; TO;CC;BCC;SUBJECT;ATTACH;FORMAT;BODY;F1;F2;F3;ATTR
# MAIL_SEND: Tramite vari canali, singola e multipla.
# Parametri nel dictionario:
# MASSIVE: True/False. SINGOLA se MASSIVE=False o se non specificato FILE.IN
# False = Se non massivo, si crea dictCSV con BODY, TO, SUBJECT obbligatori e ATTACH, BCC, CC opzionali
# SMTP.SERVER, SMTP.USER SMTP.PASSWORD, SMTP.PORT(numero supportato), SMTP.SSL(boolen) CHANNEL=SMTP/WS/GMAIL
# SUBJECT, TO, BCC, CC, BODY, ATTACH(lista), FROM FILE.IN=FileCSV, MASSIVE[opziomale]: True, False
# CSV.DELIMITER, CSV.QUOTE, CSV.TRIM
# import nlMail
# sResult=nlMail.

# ------------------------------- Setup ----------------------

# ntJobsOs Layer
import nlSys, nlDataFiles
from nlDataFiles import NC_CSV
from nlDataFiles import sCSV_DELIMITER

# Librerie Python
import os
from pathlib import Path

# Mailing Layer
from ncMail import NC_Mail
from ncMail import asFMT_MAIL_HDR, asFMT_MAIL_SMTP

# Test Mode
NT_ENV_TEST_APP=True

class NC_MailSend()
    

# Creazione di un CSV in memoria 
# ---------------------------------------------------------------------------------------
    def MailSingle(dictParams):
        sProc="MAIL.SINGLE"
        sResult=""
        objCSV=NC_CSV()
        objCSV.nLines=1                # Record, letti/scritti, compreso header
        objCSV.sFileCSV="MEMORY"       # Nome file csv
#asFMT_MAIL_HDR=("ID","TO","CC","BCC","SUBJECT","ATTACH","FORMAT","BODY","F1","F2","F3","ATTR"
        avRecord=["0",
                    dictParams["TO"],dictParams["CC"],dictParams["BCC"],
                    dictParams["SUBJECT"],dictParams["ATTACH"],dictParams["FORMAT"],
                    dictParams["BODY"],
                    dictParams["F1"],dictParams["F2"],dictParams["F3"],dictParams["ATTR"]]
    objCSV.avTable=[avRecord]             # Record CSV Singolo
    objCSV.asHeader=asFMT_MAIL_HDR        # Header Effettivo
    objCSV.asFields=asFMT_MAIL_HDR        # Header Da verificare
    objCSV.sDelimiter=sCSV_DELIMITER      # Delimiter
    objCSV.sFieldKey="ID"                 # Campo Chiave. FACOLTATIVO (SE C'E' il ToDict è convertibile in tabella)
    objCSV.dictParams=objCSV

# Ritorno
    return [nlSys.NF_ErrorProc(sResult,sProc),dictParams

# Principale MAIL.SEND. Se singola chiama MailSendSingle
# -----------------------------------------------
def MailSend(dictParams):
    sProc="MAIL.SEND.MASSIVE"
    global jData
    sResult=""

    if (dictParams["MASSIVE"]==False):
     # MONORIGA
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Mail Monoriga, crea dato CSV", sProc)
        sResult=MailSingle()
    else:
        # Legge ile CSV
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Lettura CSV " + jData.sFileCSV, sProc)
        # Prende tabella dati da file CSV esterno
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Tabella CSV: " + str(jData.objCSV.lines), sProc)
        else:
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Errore lettura file CSV mail: " + sResult, sProc)

# Inizializzazione Engine Mail - avMail = Mail da spedire letta
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Inizializzazione engine mail", sProc)
        objMail=NC_Mail(dictParams)
        sResult=objMail.sResult

# Invio MAIL - CSV dict
    if sResult=="" and objMail.bLogin:
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Invio mail", sProc)
        objMail.dictCSV=dictParams.objCSV
        sResult=objMail.MailSendCSV()

# Quit Server dopo invio Massivo
    if objMail.bLogin: objMail.MailSmtpQuit()

# Ritorno
    return nlSys.NF_ErrorProc(sResult,sProc)
