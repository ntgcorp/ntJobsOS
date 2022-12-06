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
import nlSys, nlDataFiles, naJobs
from ntJobsApp import NC_Sys
from ntDataFiles import NC_CSV

# Da Conveti
import argparse, configparser

# Librerie Python
import os
from pathlib import Path

# ntJobsOs Mailing Layer
from ntMailClass import NC_Mail
from ntMailClass import asFMT_MAIL_HDR, asFMT_MAIL_SMTP

NT_ENV_TEST_MAIL=True
NT_ENV_TEST_MAIL_ARGS=True

# Variabili Globali
NTM_sFileINI="" # File.INI
NTM_sFileCSV="" # File.CSV
NTM_dictINI=dict()
NTM_dictCSV=dict()

# --------------------- Funzioni Accessorie --------------------------
# MAIL_SEND: Tramite vari canali, singola e multipla.
# SINGOLA se MASSIVE=False o se non specificato FILE.IN
# Se non massivo, si crea dictCSV con BODY, TO, SUBJECT obbligatori e ATTACH, BCC, CC opzionali
# SMTP.SERVER, SMTP.USER SMTP.PASSWORD, SMTP.PORT(numero supportato), SMTP.SSL(boolen) CHANNEL=SMTP/WS/GMAIL
# SUBJECT, TO, BCC, CC, BODY, ATTACH(lista), FROM FILE.IN=FileCSV, MASSIVE[opziomale]: True, False
# CSV.DELIMITER, CSV.QUOTE, CSV.TRIM
# -------------------------- FASI -----------------------

def NTM_MassiveSet(bMassive, sFileCSV):
    sProc="MAIL.MassiveSet"
    NTM_dictINI["MASSIVE"]=bMassive
    NTM_dictINI["FILE.IN"]=NTM_sFileCSV
    ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Setting MASSIVE: " + str(bMassive) + ", FILE.IN: " + str(NTM_sFileCSV), sProc)

# Arguments
def NTM_Args(sArgs):
# -------------------------------------------------------
    sProc="MAIL.ARGS"
    sResult=""
    global NTM_sFileINI, NTM_sFileCSV, NTM_dictINI

# Args
    if (sArgs!=""):
        asArgs.split(" ")
        # ArrayTrim  & CASE
# LR=Trim Space Left/Right, UCZ=UCase, LCase, Capitalize, S=StripSpaces, X=StripNoAsc, F=ForzaStr
        asArgs=ntSys.NF_ArrayStrNorm(asArgs, "LR")
        if len(asArgs)>0: NTM_sFileINI=asArgs[0]
        if len(asArgs)>1: NTM_sFileCSV=asArgs[1]
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Utilizzo INI/CSV da PARAM: " + NTM_sFileINI + "," + NTM_sFileCSV, sProc)
# inFile, outFile
    elif NT_ENV_TEST_MAIL_ARGS == True:
        NTM_sFileINI="Temp/Test_ntMail1.ini"
        NTM_sFileCSV="Temp/Test_ntMail.csv"
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Utilizzo INI/CSV demo: " + NTM_sFileINI + "," + NTM_sFileCSV, sProc)
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("NTM_sFileINI", help="InputFileConfig.INI ")
        parser.add_argument("NTM_sFileCSV", help="InputFile.CSV, ntJobs.Mail format")
        args = parser.parse_args()
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Utilizzo INI/CSV da CMDLINE: " + NTM_sFileINI + "," + NTM_sFileCSV, sProc)
# Uscita
    return sResult

# Sezione Legge file INI + Parametri di default
# Ritorno sResult
# -------------------------------------------------------
def NTM_INI_Read():
    sProc="MAIL.INI_Read"
    global NTM_sFileINI, NTM_dictINI

# Legge File INI
    lResult=ntJobsApp.JOBS_StartRead(dictParams)
    sResult=lResult[0]
    if sResult=="":
        NTD_dictINI=lResult[1]

# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# Legge INI in dictMail
    ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Lettura file INI:" + NTM_sFileINI, sProc)
    lResult=ntDataFiles.NF_INI_Read(NTM_sFileINI)
    sResult=lResult[0]
    #print(sProc + " " + sResult)
    if sResult=="":
        NTM_dictINI=lResult[1]["CONFIG"]
        # Verifica sia stata letta la sezione config
        if ntSys.NF_DictLen(NTM_dictINI)<1: sResult="assente sezione config"

# Conversioni da str a numero/bool
    if sResult=="":
        dictConvert={"WAIT":"I", "SMTP.SSL":"B", "SMTP.PORT":"I"}
        NTM_dictINI=ntSys.NF_DictConvert(NTM_dictINI,dictConvert)
        if len(NTM_dictINI)==0: sResult="conversione keys in dict"

# Completmento
    ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Letto file INI. Eventuali errori: " + sResult, sProc)
    print(str(NTM_dictINI))

# Ritorno
    return sResult

# Verifica parametri INI Letto e altro
# Ritorna sResult con tutti errori
def NTM_INI_Verify():
    sProc="MAIL.INI_Verify"
    sResult=""
    bMassive=False
    global NTM_dictINI, NTM_sFileCSV, NTM_dictCSV

# Verifica DICT_INI - USCITA RAPIDA se non leto
    if not (ntSys.NF_IsDict(NTM_dictINI)):
        sResult=ntSys.NF_ErrorProc("non letto dizionario INI", sProc)
        return sResult

# Verifica: Massiva e Update Bool + Esistenza file CSV e assegnazione
    # Se specificato prende CSV
    sFileCSV=ntSys.NF_DictGet(NTM_dictINI,"FILE.IN", "")
    if sFileCSV != "":
        NTM_sFileCSV=sFileCSV
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Lettura CSV da FILE.IN: " + NTM_sFileCSV, sProc)
        bMassive=True
        # Normalizzazione FileCSV
        lResult=ntSys.NF_PathNormal(sFileCSV)
        sResult=lResult[0]
        if sResult=="": NTM_sFileCSV=lResult[5]

# Se non Massivo crea dictCSV con un record da NTM_dictINI
    if bMassive and (sResult==""):
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Creazione CSV in memoria monoriga", sProc)
        asTemp = asFMT_MAIL_HDR + asFMT_MAIL_SMTP
        NTM_dictTemp=dict()
        bMassive=False
        for sKey in asTemp:
            if ntSys.NF_DictExistKey(NTM_dictINI,sKey):
                NTM_dictTemp[sKey]=ntSys.NF_DictGet(NTM_dictINI,sKey,"")
        # Completamento dict con ID
                sID="1"
                NTM_dictTemp["ID"]=sID
        # Assegnazione DICTCSV
        NTM_dictCSV.clear()
        NTM_dictCSV[sID]=NTM_dictTemp.copy()

# Update dictINI per MASSIVI - Se previsto MASSIVO NON FARE
    NTM_MassiveSet(bMassive, NTM_sFileCSV)

# Verifica esistenza CSV se MASSIVO
    if bMassive and (sResult==""):
        print(sProc + ", Test esistenza file")
        sResult=ntSys.NF_FileExistErr(NTM_sFileCSV)

# Ritorno
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    print("NTM:" + sResult)
    return sResult

# Sezione Legge file CSV
# Ritorna Risultato NF_CSV_Read() - lResult
# NTM_sFileCSV già normalizzato
# -------------------------------------------------------
def NTM_CSV_Read():
    sProc="MAIL.CSV_Read"
# Estrae File CSV di spedizione
# Ritorno lResult 0=sResult, 1=dictCSV
    global NTM_sFileCSV, NTM_dictINI, NTM_dictCSV
    sResult=""
    objCSV=NC_CSV()

# Legge CSV Mail da spedire
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, CSV.DELIMITER=Delimiter campi, CSV.TRIM=Trim Prima e dopo. CSV.QUOTE=Campo delimitatore testi
    if (sResult=="") and (NTM_sFileCSV != ""):
        dictParams={'FILE.IN': NTM_sFileCSV,
                    'FIELDS': asFMT_MAIL_HDR,
                    'DELIMITER': NTM_dictINI.get("CSV.DELIMITER",ntDataFiles.sCSV_DELIMITER),
                    'TRIM': NTM_dictINI.get("CSV.TRIM",True),
                    'QUOTE': NTM_dictINI.get("CSV.QUOTE", ntDataFiles.sCSV_QUOTE)}
        sResult=objCSV.Read(dictParams)
        if sResult=="":
            nRecords=objCSV.nLines
            lResult=[sResult,objCSV.ToDict).copy(),nRecords]
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Lettura CSV. File=" + dictParams["FILE.IN"] + ", Righelette=" + str(nRecords) + ", Status=" + sResult, sProc)
    else:
        lResult=[sResult,[]]

# Ritorno
    return lResult

# Sezione Invio Mail
# Richiama le varie fasi
# Ritorno lResult. di MAIL_SendMailCSV
# -------------------------------------------------------
def NTM_Start(sArgs):
    sProc="MAIL.Start"
    sResult=""
    global NTM_sFileCSV, NTM_sFileINI, NTM_dictINI, NTM_dictCSV

# Application Object
    jData=NC_Sys("NTMAIL")

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    dictParams={
        "FILE.INI": "",
        "INI.YES": True,
        "TEST.YES": True,
        "INI.TEST": "Test\Test_ntMail_HTML_1.ini"
    }

# Argomenti
    lResult=ntJobsApp.JOBS_Args(dictParams)
    sResult=lResult[0]

# Parametri: Lettura INI JOB
# ----------------------------------------------------------------------------
    if sResult=="":
        NTD_sFileINI=lResult[1]
        lResult=ntJobsApp.JOBS_ReadINI(dictParams)
        sResult=lResult[0]
        # Prende parametri JOB
        if sResult=="":
            NTD_dictINI=lResult[1]
            jData.setJob(NTD_sFileINI)

# Veifica INI eventuale creazione dictCSV monoriga o IN.FILE=CSV normalizzato
    if sResult=="":
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Verifica INI ed eventuale dictCSV: " + NTM_sFileINI, sProc)
        sResult=NTM_INI_Verify()
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Completamento INI_VERIFY: " + sResult, sProc)

# Eventuale lettura CSV o MONORIGA
# ----------------------------------------------------------------------------
    if sResult=="":
    # Se FILE.CSV=="" allora è monoriga
        NTM_sFileCSV=ntSys.NF_DictGet(NTM_dictINI,"FILE.CSV","")
    # Debug
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Argomenti CMDLINE.     INI=" + NTM_sFileINI + ", CSV: " + NTM_sFileCSV + ", Result: " + sResult, sProc)

# Parametri: Lettura CSV se presende
# ----------------------------------------------------------------------------
    if sResult=="":
        sResult=ntJobsApp.JOBS_ReadCSV(NTD_dictINI)
        if sResult=="": NTM_dictCSV=lResult[1]

# Azioni
# -----------------------------------------------------------------------------
    if sResult=="":
        sAction=ntSys.NF_DictGet(NTM_dictINI,"ACTION","")
        if sAction=="MAIL.SEND":
            lResult=NTM_MailSend()
            sResult=lResult[0]
            if sResult=="": ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Inviato flusso di mail: " + str(lResult[2]), sProc)
        else:
            sResult="Azione non riconosciuta: " + sAction

# Conclusione
# -------------------------------------------------------------------------------

# 1: Tag Proc sResult, 2: EndJob 3: Calcolo Return
    dictReturnFiles=None
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    jData.EndJob()
    sResult=ntJobsApp.JOBS_ReturnCalcWrite(sResult,jData,dictReturnFiles)
    if sResult != "": print("Errore calcolo/scrittura ritorno JOB: " + sResult)


# Ritorno
    return sResult

# ------------------------------- AZIONI --------------------

# Azione MAIL.SEND
# -----------------------------------------------

def NTM_MailSend():
    sProc="MAIL.SEND.MASSIVE"
    global  NTM_dictINI
    sResult=""

    if (NTM_dictINI["MASSIVE"]==False):
     # MONORIGA
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "DictCSV Monoriga: " + str(NTM_dictCSV), sProc)
    else:
        # Legge ile CSV o E' GIA' PRESENTE IN MEMORIA
        # Ritorna lResult. 0=RitornoStr, 1=Campi, 2=SchemaCompleto(OPZIOMALE o None), 3=dictTableCSV
        # Se NON PRESENTE DICTCSV lo legge
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "dictCSV Lettura CSV: " + NTM_sFileCSV, sProc)
        lResult=NTM_CSV_Read()
        sResult=lResult[0]
        # Prende tabella dati da file CSV esterno
        if sResult=="":
            NTM_dictCSV=lResult[3]
            ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Letto da file CSV. mail: " + str(len(NTM_dictCSV)-1), sProc)
        else:
            ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Errore lettura file CSV mail: " + sResult, sProc)

# Inizializzazione Engine Mail - avMail = Mail da spedire letta
    if sResult=="":
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Inizializzazione engine mail", sProc)
        objMail=NC_Mail(NTM_dictINI)
        sResult=objMail.sResult

# Invio MAIL - CSV dict
    if sResult=="" and objMail.bLogin:
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Invio mail", sProc)
        objMail.dictCSV=NTM_dictCSV
        sResult=objMail.MailSendCSV()

# Quit Server dopo invio Massivo
    if objMail.bLogin: objMail.MailSmtpQuit()

# Costruisce lResult in caso di problema
    sResult=ntSys.NF_ErrorProc(sResult, sProc)
    if sResult!="": lResult=[sResult,""]
    return lResult

# ----------------------------- MAIN --------------------------

def main():
    sProc="Main"
    sArgs=""
    lResult=NTM_Start(sArgs)
    sResult=lResult[0]
    ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Completamento NTM_Start: " + sResult, sProc)
    exit()

# Start Default Python code
if __name__=="__main__": main()
