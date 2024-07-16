#
# Interface for ntJobsOS FrontEnd Application
# JOBS_Start_Read: Legge INI di Configurazione
# JOBS_End_Write: Scrive INI di Fine attività
# JOBS_ARGS: Recupero parametri secondo varie opzioni permesse nel lancio FrontEnd ntJobsOS
#
import nlSys
import nlDataFiles
from nlDataFiles import NC_CSV
import argparse
import os
import locale

# Test mode
NT_ENV_TEST_JIO = True

# ----------------------- CLASSI ---------------------------

# ---------- NC_SYS - jData - ntJobs.App -------------------
class NC_Sys:
    # Arguments and Setup
    sID = ""              # ID Applicazione
    bINI = False          # INI Obbligatorio
    bTest = False         # Test Mode Obbligatorio
    sIniTest = ""         # INI File di Test (se TestMode=True)
    bLog=False            # Implementazione LOG e Transazioni collegate ai LOG
    # Application Path
    sSys_Path = ""        # ntJobs Kit Path Root
    sJob_Path = ""        # Job File Path
    sJob_File = ""        # Job File (Normalizzato completo)
    sJob_Name = ""        # JOB.ID come somma di più JOBS
# TimeStamp
    sTS_Start = ""        # TimeStamp: Start
    sTS_End = ""          # TimeStart: End
# INI Config + Actions in sequenza
    dictConfig = {}       # Config (Sezione Config)
    dictConfigFields = {} # Tipizzazione particolare (per tutte le sezioni).
    dictJobs = {}         # Jobs/Sections - Config + Parametri richiamo Actions in sequenza
    asJobs = []           # Jobs Names List (config....ecc)
    dictJob = {}          # JobCorrente. Action, Files.*=, Vars.*= )
    sAction = ""          # Azione Corrente
# Azione Corrente: Ingresso
    sJob = ""
# Sezione(jobs) Corrente da cui deriva dictJob che viene separato in singolo jobs.ini e passato a ntjobs.OS
# Azione Corrente - RITORNO
    lResult = []          # Return from CallBack
    cbActions = None      # CallBack Function
    sResult = ""          # Return Value
    sRetType = ""         # Return Type, E=Errore, ""=Ok, W=Warning
    dictReturnFiles = {}  # Eventuali file di ritorno dict [FILE.ID=FILE.PATH.NORM]
    dictReturnVars = {}   # Variabili di ritorno del job corrente
    dictReturn = {}       # dictReturn di Ritorno Calcolata per scrittura - SINGOLA SEZIONE - Da aggiungere da ReturnAdd
# Ritorno di tutte le azioni Eseguite (sezione= nome_sezione_non_config, RET.VAL, RET.TYPE, FILE.ID=VALORE, CONFIG=Sezione ritorni prima delle azioni)
    dictReturnS = {}      # Sezioni dictReturn di Ritorno Calcolata per scrittura - UNA VOLTA SOLA VIENE SCRITTO il file
# CSV Main Data
    sFileCSV = ""         # File.CSV - LETTO DA self.dictConfig FILE.CSV. Se Presente allora legge se no no.
    asFieldsCSV = []      # Fields FileCSV
    objCSV = None         # Oggetto CSV creato se esiste file
    sJobPath = ""         # Path singolo job (dopo lettura file INI del JOB)
# File di LOG Singola Sessione (job) e Globale (File)
    bLogJob = False       # Log singola sessione
    bLogFile = False      # Log globale in global ntJobs Log folder
    sLogFile = ""         # File di log Globale
    sLogJob  = ""         # File di log Singolo Job

# Metodi (Init)
# --------------------------------------------------------------------------------
    def __init__(self, sID_set):

    # Init jData
        locale.setlocale(locale.LC_ALL, "it_IT.UTF8")
        self.sID = sID_set
        self.sSys_Path = os.getcwd()
        print("ntJob.Start: " + self.sID + ", TS: " + self.sTS_Start)
    # Log Start (quello di transazione solo dopo lettura INI perché non si conosce JobPath)
        if self.bLog:
            self.sLogFile = self.sSys_Path + "\\Log\\" + self.sID + ".log"
            sResult=self.Log("Start", type="s", proc="init")
            if sResult != "": print("Errore scrittura log file " + self.sLogFile)

# Scrive Riga LOG. Parametri:
# Log(Obbligatorio): Riga di commento Log
# type=tipo log (s=start.app, tk=trans.ok, te=trans.err, e=errore generico, w=warning, l(default)=log, f=end.app),
# tag=Log.Tag, proc=Log.Proc
# Formato Log. TYPE;TS;TAG;LOG.NOTE
# ---------------------------------------------------------------------------------------------------------------
    def Log(self, sLog, **kaArgs):

    # Parametri Facoltativi
        if (kaArgs != None):
            for sKey,sValue in kaArgs.keys:
                sValue=str(sValue)
                if sKey=="type":
                    if sValue=="s":
                        sLogP="App.Start"
                    elif sValue=="tk":
                        sLogP="Trans.End.Ok"
                    elif sValue=="te":
                        sLogP="Trans.End.Err"
                    elif sValue=="e":
                        sLogP="Error"
                    elif sValue=="w":
                        sLogP="Warning"
                    elif sValue=="l":
                        sLogP="Log"
                    elif sValue=="f":
                        sLog="App.Start"
                    else:
                        sLogP="NA"
                elif sKey=="tag":
                    sLogTag=sValue
                elif sKey=="proc":
                    sLogProc=sValue
    # Creazione riga di LOG
        sText = f"{self.sID}.{sLogProc}.{sLogTag}"
        sText = sText + ", " + nlSys.NF_TS_ToStr() + "," + sLogTag + ": "  + sLog
    # Scrive riga di Job su LogFile e LogTrans
        if self.sLogFile != "":
            nlSys.NF_FileFromStr(sText, self.sLogFile, "a")
        else:
            print(sLog)
        if self.sLogJob != "": nlSys.NF_FileFromStr(sText, self.sLogJob, "a")

    # Ritorno
        return sText

# Sezione Legge file INI + Parametri di default
# Ritorno lResult. 0=Stato, 1=dictINI se trovato File.INI di config con sezione [CONFIG] o None, 2=FileCSV_normalizzato, 3=Records
# Parametri:
#    FILE.INI=File da leggere - Gia' normalizzato
#    FIELDS.TYPE: dict. Campi accettati come valore hanno il tipo "(N)Number o (B)Boolean o (I)Integer (D)ata"
#    ACTIONS: Array Stringa azioni accettate
# Ritorno: sResult (e impostato self.sJob_File, self.dictConfig)
# --------------------------------------------------------------------------------
    def ReadINI(self):
        sProc = "JOBS.APP.ReadINI"
        sResult = ""
        lResult = []
# Setup
        self.dictConfig = {}
        self.sResult = ""

# Parametri - Prende e Verifica
# -------------------------------------------------------
# Verifica su 3 parametri
        if self.sJob_File == "": sResult=nlSys.NF_StrAppendExt(sResult, "FILES.INI mancante")
        if self.asJobs == None: sResult=nlSys.NF_StrAppendExt(sResult, "Lista azioni mancante, anche vuota")
# Normalizzazione e JobPath
        if sResult=="":
            # 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
            lResult=nlSys.NF_PathNormal(self.sJob_File)
            self.sJob_Path=lResult[1]
            self.sJob_File=lResult[5]
            self.sJob_Name=lResult[2]

# Legge INI
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura file INI:" + self.sJob_File, sProc)
            lResult=nlDataFiles.NF_INI_Read(self.sJob_File)
            sResult=lResult[0]

# Prende sezione CONFIG
        if sResult == "":
# Verifica che ci sia Config
            self.dictJobs=lResult[1]
            self.dictConfig=nlSys.NF_DictGet(self.dictJobs, "CONFIG", {})
            if nlSys.NF_DictLen(self.dictConfig)<1: sResult="sezione CONFIG vuota o non esistente"
# Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
        if sResult == "":
            self.asJobs=self.dictJobs.keys()
            for self.sJob in self.asJobs:
                self.dictConfig = nlSys.NF_DictConvert(self.dictConfig, self.dictConfigFields)
                if nlSys.NF_DictLen(self.dictConfig) == 0:
                    sResult="Conversione KEYS CONFIG in dict"
                    break
# Completamento:
        nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Letto file INI. Eventuali errori: " + sResult, sProc)
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Legge file CSV di dati del JOB (se previsto)
# Parametri:
#   dictINI: Standard ntJobs CONFIG
# Ritorno
#   sResult=Risultato
#   Cambia , 2=FileCSV normalizzato se trovato File.csv, 3=Records
# -------------------------------------------------------
    def ReadCSV(self):
        sProc="JOBS.APP.ReadCSV"
        sResult=""

# Legge Parametri da Config
        self.sFileCSV=nlSys.NF_DictGet(self.dictConfig,"FILE.CSV","")
# Se non c'è File CSV Esce
        if self.sFileCSV=="": return ""
# Conversione FIELDS.CSV da String a Array
        sFieldsCSV=nlSys.NF_DictGet(self.dictConfig,"FIELDS.CSV","")
        asFieldsCSV=nlSys.NF_StrSplitKeys(sFieldsCSV,",")
        nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura CSV: " + str(asFieldsCSV), sProc)
# Normalizzazione CSV FILE
        lResult=nlSys.NF_PathNormal(self.sFileCSV)
        sResult=lResult[0]
        if sResult=="":
            self.sFileCSV=lResult[5]
            dictParams={
                "FILE.IN": self.sFileCSV,
                "FIELDS": asFieldsCSV,
                "FIELD.KEY": nlSys.NF_DictGet(self.dictConfig,"FIELD.KEY","")
            }
# Crea componente NC_CSV in jData
            self.objCSV=NC_CSV()
# Lettura CSV File e Ritorno
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura CSV: " + nlSys.NF_DictStr(dictParams), sProc)
            sResult=self.objCSV.Read(dictParams)
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Arguments
# Parametri
# INI.YES: Obbligatorio File INI
# TEST.YES: Previsti file di test, allora ci deve essere anche TEST.INI
# Ritorno lResult. 0=sFileINI
# ------------------------------------------------------------------------------------
    def Args(self):
        sProc="JOBS.APP.ARGS"
        sResult=""

# INI Obbligatorio o Facoltativo

# Controlli
    # Se da TEST
        if self.sIniTest != "":
            self.sJob_File = self.sIniTest
            self.bTest = True
            nlSys.NF_DebugFase(self.bTest, "Utilizzo INI Demo. INI: " + self.sJob_File, sProc)
        if self.sJob_File != "": self.bINI=True
    # INI.TEST
        if self.bINI and (self.sJob_File == ""):
    # Oppure Prende INI da ARGS reale
            parser = argparse.ArgumentParser()
            parser.add_argument("sFileINI", help="InputFileConfig.INI ")
            args = parser.parse_args()
            if args.count>0 and self.bINI: self.sJob_File=args.sFileINI
            nlSys.NF_DebugFase(self.bTest, "Utilizzo INI da CMDLINE: " + self.sJob_File, sProc)
    # Verifica Parametri
        if self.sJob_File=="": sResult="Non specificato parametro File INI"

        # Debug
        if sResult == "":
            dictParams={"INI.YES": self.bINI, "TEST.YES": self.bTest, "INI.TEST": self.sIniTest, "ACTIONS": self.asJobs}
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Parametri job: " + nlSys.NF_StrObj(dictParams), sProc)

    # Normalizzazione INI
        if sResult=="":
            lResult=nlSys.NF_PathNormal(self.sJob_File)
            self.sJob_File=lResult[5]
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "File INI: " + self.sJob_File, sProc)

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Aggiunge dictReturn a dictReturnS
# ------------------------------------------------------------------------------------
    def ReturnAdd(self):
        self.dictReturnS[self.sJob]=self.dictReturn.copy()

# Scrive dictReturnS in file JOBS.END nella stessa cartella file JOBS.INI . Per tutte le sezioni di ritorno
# Se vuoto scrive file vuoto
# Parametri:
#   JOB.PATH: Cartella del JOB.
# Ritorno: sResult
# ------------------------------------------------------------------------------------
    def ReturnWrite(self):
        sProc="JOBS.APP.RETURN.WRITE"
        sResult=""

# Calcola File End
        sFileEnd=nlSys.NF_PathMake(self.sJob_Path, "jobs", "end")
        nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "File END: " + sFileEnd, sProc)

# Scrive File END di ritorno
        sResult=nlDataFiles.NF_INI_Write(sFileEnd, self.dictReturnS)
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Calcola Dictionary di Ritorno da Scrivere su File
# Imposta dictReturn, Ritorno: sResult
#   RETURN.TYPE: RETURN.TYPE=E=Errore/W=Working/Nulla=OK
#   RETURN.VALUE=Messaggio di ritorno
#   TS.START, TS.END = TimeStamp di inizio e fine
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalc(self,lResult):

# Conclusione JOB.SECTION
        self.sTS_End=nlSys.NF_TS_ToStr()
        print ("JOB.SECTION.END: " + self.sJob + ", TS: " + self.sTS_End)

# Calcola RetType
        self.sResult=lResult[0]
        if self.sResult!="":
            self.sRetType="E"
        else:
            self.sRetType=""

# Prende Files - Anche un EMPTY
# Prende Variabili di Ritorno
        nLen=len(lResult)
        if nLen>1: self.dictReturnFiles=lResult[1]
        if nLen>2: self.dictReturnVars=lResult[2]

# Crea dictReturn
        self.dictReturn={
            "TS.START": self.sTS_Start,
            "TS.END": self.sTS_End,
            "RETURN.TYPE": self.sRetType,
            "RETURN.VALUE": self.sResult,
            "JOB.PATH": self.sSys_Path
            }
# Aggiunge Files PDF Creati
        self.ReturnCalcAddExtra("FILES")
        self.ReturnCalcAddExtra("VARS")

# Aggiuge Files o Vars al ritorno
# Ritorno: sResult
# Parametro: sType(VARS,FILES,"")
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAddExtra(self, sType=""):
        sProc="ReturnCalcAddExtra"
        dictAdd={}
        sResult=""
        sTag=""

    # dict Da Aggiungere
        if sType=="VARS":
                dictAdd=self.dictReturnVars
                sTag="VAR"
        if sType=="FILES":
                dictAdd=self.dictReturnFiles
                sTag="FILE"
    # Aggiunta
        if nlSys.NF_DictLen(dictAdd)>0:
            nCounter=0
            for sKey in nlSys.NF_DictKeys(dictAdd):
                nCounter=nCounter+1
                sValue=nlSys.NF_DictGet(dictAdd, sKey,"")
                self.dictReturn[sTag + "." + sKey]=sValue
    # Uscita Nulla
        return sResult

# Calcola Ritorno e Lo Aggiunge al Pool di Ritorni
#   Oggetto ntJobs.App, Scrive sResult e dictReturnFiles
# Ritorno: sResult
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAdd(self,lResult):
# Calcola Ritorno e Scrive
        self.ReturnCalc(lResult)
        self.ReturnAdd()

# Azioni di Setup di Base
# -----------------------------------------------------------------------------
    def Start(self):
        sResult=""
        sProc="JOBS.APP.START"

# Legge Argomenti
        self.sTS_Start=nlSys.NF_TS_ToStr()
        sResult=self.Args()

# Parametri: Lettura INI JOB
        if sResult=="" and self.bINI:
            sResult=self.ReadINI()
            if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Jobs letti:" + str(nlSys.NF_DictLen(self.dictJobs)), sProc)
            if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "INI CONFIG. Keys " + nlSys.NF_DictStr(self.dictConfig), sProc)

# Config Speciali standard
        if sResult == "":
            self.sFileCSV=nlSys.NF_DictGet(self.dictConfig,"FILE.CSV","")
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "File CSV da leggere " + self.sFileCSV, sProc)
            sTemp=nlSys.NF_DictGet(self.dictConfig,"FIELDS.CSV","")
            if sTemp == "":
                sResult="Specificato file CSV ma non campi del file"
            else:
                self.asFieldsCSV=sTemp.split(",")
                self.asFieldsCSV=nlSys.NF_ArrayStrNorm(self.asFieldsCSV,"LRU")

# Parametri: Lettura CSV se presende
        if sResult=="" and (self.sFileCSV != ""):
            sResult=self.ReadCSV()
            if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura file CSV. Risultato: " + sResult, sProc)

# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        if sResult != "": nlSys.NF_DebugFase(NT_ENV_TEST_JIO, sResult, sProc)
        return sResult

# Esecuzione Singoli jobs (Azioni) del JOB.INI complessivo
# ------------------------------------------------------------------------------
    def Run(self):
        sProc="JOBS.APP.RUN"
        sResult=""
        lResult=[]

    # Setup
        dictReturnS=[]

    # Ciclo Azioni
        for sJob in self.asJobs:
        # TimeStamp e Reset Return
            self.dictReturn={}
            self.dictReturnFiles={}
            self.dictReturnVars={}
       # Job/Azione Corrente
            self.dictJob=self.dictJobs[sJob]
        # Start Azione mediante CallBack - Ritorno previsto lResult, ad uso dinamico
            nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "JOB.SECTION.END: " + self.sJob + ", TS: " + self.sTS_Start, sProc)
        # Verifica Parametri Job
            sResult=self.JobVerify()
            if sResult=="": lResult=self.cbActions(self.dictJob)
        # Memorizzazione ritorni per ritorno locale e jData 0=Result, 1=Files, 2=Vars
            self.lResult=lResult
            self.sResult=lResult[0]
            if len(lResult) > 1: self.dictReturnFiles=lResult[1]
            if len(lResult) > 2: self.dictReturnVars=lResult[2]
            print("Ritorno JOB: " + sJob + ", Files: " + nlSys.NF_DictStr(self.dictReturnFiles) + ", Vars: " + nlSys.NF_DictStr(self.dictReturnVars))

        # Aggiunge Ritorno
        self.ReturnCalcAdd(lResult)

    # END Job.Complessivo
        self.End()
        print(self.ReturnStr())

    # Scrive Return
        sResult=self.ReturnWrite()
        nlSys.NF_DebugFase(NT_ENV_TEST_JIO, "Risultato scrittura ritorno" + sResult, sProc)

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Prende parametro da dictionary job, oppure ritorna errore, tipizzazione di default se precisata
# -----------------------------------------------------------------------------------------------------
    def GetParam(self, sParam, sError, sType=None):
        sResult,vDato=nlSys.NF_DictGetParam(self.dictJob, sParam, sError, sType)
        return sResult,vDato

# Fine Job (subito dopo RUN. Separato per motivi di test)
# -----------------------------------------------------------------------------------------------------
    def End(self):
        sProc = "JOBS.APP.END"
        sResult = ""
    # PER ORA NON FA NULLA
    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# String del Return
    def ReturnStr(self):
        sResult=f"Ritorno JOB. Nome: {self.sJob_Name} , Section: {self.sJob}, LenDict: {str(len(self.dictReturnS))}\n"
        for xKey in self.dictReturnS.keys():
            sResult = sResult + str(xKey) + " " + nlSys.NF_DictStr(self.dictReturnS[xKey]) + "\n"
        return sResult

# Job Verify: Verifica parametri del JOB
# -----------------------------------------------------------------------------------------------------
    def JobVerify(self):
        sProc="JOBS.VERIFY"
        sResult=""

    # Verifica Azione
        sAction=nlSys.NF_DictGet(self.dictJob,"ACTION","")
        if sAction=="": sResult="Azione non dichiarata in INI"

        # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

