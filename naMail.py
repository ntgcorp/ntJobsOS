# ntJobs.Mail - Programma
# -----------------------------------------------------------
# Invio mail massive parametrizzato
# Formato ntJobs.Mail: ID; TO;CC;BCC;SUBJECT;ATTACH;FORMAT;BODY;F1;F2;F3;ATTR
# Sintax: ntMail inputFileINI.ini
# Fasi:
# 1=Argomenti
# 2a=File_INI in Dictionary - 2b=Verifica_Parametri_INI
# 3a=LeggeFileCSV 3b=VerificaCSV
# 4a=Ciclo di Invio_Mail
#    4b=InvioMailSingola
# Azione MAIL.SEND. Invio singolo o massivo (se specificato FILE.CSV)
# ------------------------------- Setup ----------------------

# ntJobsOs Layer
import nlSys, nlDataFiles, ncJobsApp
from ncJobsApp import NC_Sys
from nlDataFiles import NC_CSV
from nlDataFiles import sCSV_DELIMITER

# Librerie Python
import os
from pathlib import Path

# Mailing Layer
from ncMail import NC_Mail
from ncMail import asFMT_MAIL_HDR, asFMT_MAIL_SMTP

# Global App Container
jData=None

# Test Mode
NT_ENV_TEST_NTM=True

# --------------------- Funzioni Accessorie --------------------------
# MAIL_SEND: Tramite vari canali, singola e multipla.
# SINGOLA se MASSIVE=False o se non specificato FILE.IN
# Se non massivo, si crea dictCSV con BODY, TO, SUBJECT obbligatori e ATTACH, BCC, CC opzionali
# SMTP.SERVER, SMTP.USER SMTP.PASSWORD, SMTP.PORT(numero supportato), SMTP.SSL(boolen) CHANNEL=SMTP/WS/GMAIL
# SUBJECT, TO, BCC, CC, BODY, ATTACH(lista), FROM FILE.IN=FileCSV, MASSIVE[opziomale]: True, False
# CSV.DELIMITER, CSV.QUOTE, CSV.TRIM

# Sezione Invio Mail
# Richiama le varie fasi
# Ritorno lResult. di MAIL_SendMailCSV
# -------------------------------------------------------
def NTM_Start():
    sProc="NTM.Start"
    global jData
    sResult=""

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData=NC_Sys("NTMAIL")                          # Application Object
    jData.bINI=True                                 # Ini Presente
    jData.bTest=True                                # Test Mode
    jData.sIniTest="Test\Test_ntMail_demo.ini"      # Test file
    jData.asActions=["MAIL.SEND"]                   # Azioni supportate
    jData.cbActions=NTM_cbActions                   # CallBack Azioni
    jData.dictINI_Fields={"WAIT":"I", "SMTP.SSL":"B", "SMTP.PORT":"I"}
    
# Legge Argomenti
    sResult=jData.Args()

# Parametri: Lettura INI JOB - Specificando extra i campi del CSV
    if sResult=="": sResult=jData.ReadINI()

# Parametri di default
    jData.dictINI["MASSIVE"]=False

# Debug
    if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "INI CONFIG. Keys " + nlSys.NF_DictStr(jData.dictINI), sProc)

# Parametri: Lettura CSV se presende
    if sResult=="": sResult=jData.ReadCSV()
    if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_NTM, f"Lettura file CSV [{jData.sFileCSV}]:" + sResult, sProc)
    
# Caso MonoRiga - Crea CSV in memoria
    if (jData.sFileCSV!="") and (sResult==""):
        jData.dictINI["FIELDS.CSV"]=asFMT_MAIL_HDR
        jData.dictINI["MASSIVE"]=True
        sResult=NTM_MailSingleCSV()

# Run (All in One)
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.Run()

# Ritorno
    return sResult

# --------------------------------- BODY SINGOLE AZIONI ----------------------

# CallBack Azioni
def NTM_cbActions(dictParams):
    sProc="NTM_cbActions"

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Start Azione: " + sAction, sProc)

# Azioni dell'App
    if sAction=="MAIL.SEND":
        lResult=NTM_MailSend(dictParams)
        sResult=lResult[0]
    else:
        sResult="Azione Non trovata " + sAction

# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult

# Creazione di un CSV in memoria da jData.dictINI
# ---------------------------------------------------------------------------------------
def NTM_MailSingleCSV():
    sProc="NTM.MAIL.SINGLE.CSV"
    sResult=""
    objCSV=NC_CSV()
    objCSV.nLines=1                # Record, letti/scritti, compreso header
    objCSV.sFileCSV="MEMORY"       # Nome file csv
#asFMT_MAIL_HDR=("ID","TO","CC","BCC","SUBJECT","ATTACH","FORMAT","BODY","F1","F2","F3","ATTR"
    avRecord=["0",
                jData.dictINI["TO"],jData.dictINI["CC"],jData.dictINI["BCC"],
                jData.dictINI["SUBJECT"],jData.dictINI["ATTACH"],jData.dictINI["FORMAT"],
                jData.dictINI["BODY"],
                jData.dictINI["F1"],jData.dictINI["F2"],jData.dictINI["F3"],jData.dictINI["ATTR"]]
    objCSV.avTable=[avRecord]             # Record CSV Singolo
    objCSV.asHeader=asFMT_MAIL_HDR        # Header Effettivo
    objCSV.asFields=asFMT_MAIL_HDR        # Header Da verificare
    objCSV.sDelimiter=sCSV_DELIMITER      # Delimiter
    objCSV.sFieldKey="ID"                 # Campo Chiave. FACOLTATIVO (SE C'E' il ToDict è convertibile in tabella)
    jData.objCSV=objCSV                   # Assegnazione dopo riempimento
    
    return sResult

# ------------------------------- AZIONI --------------------

# Azione MAIL.SEND
# -----------------------------------------------

def NTM_MailSend(dictParams):
    sProc="MAIL.SEND.MASSIVE"
    global jData
    sResult=""

    if (jData.dictINI["MASSIVE"]==False):
     # MONORIGA
        nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Mail Monoriga, crea dato CSV", sProc)
        sResult=NTM_MailSingleCSV()
    else:
        # Legge ile CSV 
        nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Lettura CSV " + NTM_sFileCSV, sProc)        
        # Prende tabella dati da file CSV esterno
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Tabella CSV: " + str(jData.objCSV.lines), sProc)
        else:
            nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Errore lettura file CSV mail: " + sResult, sProc)

# Inizializzazione Engine Mail - avMail = Mail da spedire letta
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Inizializzazione engine mail", sProc)
        objMail=NC_Mail(dictParams)
        sResult=objMail.sResult

# Invio MAIL - CSV dict
    if sResult=="" and objMail.bLogin:
        nlSys.NF_DebugFase(NT_ENV_TEST_NTM, "Invio mail", sProc)
        objMail.dictCSV=dictParams.objCSV
        sResult=objMail.MailSendCSV()

# Quit Server dopo invio Massivo
    if objMail.bLogin: objMail.MailSmtpQuit()

# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult

# --------------------------------- MAIN -------------------------------------
def main():
    NTM_Start()

if __name__ == '__main__':
    main()
