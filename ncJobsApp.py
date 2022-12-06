#
# Interface for ntJobsOS FrontEnd Application
# JOBS_Start_Read: Legge INI di Configurazione
# JOBS_End_Write: Scrive INI di Fine attività
# JOBS_ARGS: Recupero parametri secondo varie opzioni permesse nel lancio FrontEnd ntJobsOS
#
import ntSys, ntDataFiles
from ntDataFiles import NC_CSV
import argparse
# Per Wait ed altro
import time, locale
from datetime import datetime
import os
# YYYYMMDD.HHMMSS.MSEC
NT_ENV_DATE_DIV="."
# Test mode
NT_ENV_TEST_JIO=True

# ------------------------------- TEMPO E DATE -------------------------

# B=Base(def), N=Normal, X=Esteso
def NF_TS_ToDict(dtDate,sType="B"):

# Setup
    tt=dtDate.timetuple
    dictTime=dict()
    nID=0
    dictID={0:"Y", 1:"M", 2:"D", 3:"HH", 4:"MM", 5:"SS", 6:"DW", 7:"DY", 8:"DY", 9:"IY", 10:"YW", 11:"YD"}

# Scomposizione
# Assegna e incrementa Indice
    for nValue in tt:
    # Conversione nID->sID
        sID=dictID[nValue]
        dictTime[sID]=nValue
        nID=nID+1

    # Aggiunge IC (Tipo N/X)
    if (sType!="B") :
        ic=dtDate.isocalendar()
        for nValue in ic:
            sID=dictID[nValue]
            dictTime[sID]=nValue
            nID=nID+1

# Ritorno
    return dictTime

# TIMESTIME: ToStr
# L=Light, P(o altro)=Python
# L=YYYYMMDD.HHMMSS, P=YYYYMMDD.HHMMSS.MILLISEC
def NF_TS_ToStr(sType="L"):
    sResult=""

# TimeStamp
    now=datetime.today()
# Conversione
    if sType=="X":
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now) + "." + str(now.microsecond)
    else:
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now)
# Uscita
    return sResult

# TIMESTIME: ToStr. Ritorna lresult, 0=sResult, 1=Date, 2=Time, 3=Msec
# sDateTime: DATE.TIME[.MSEC]
def NF_TS_FromStr(sDateTime):
    sResult=""
    sProc="TS_FromStr"
    nMsec=0

# Split
    if sDateTime=="": sResult="NoDateTime"
    if (sResult==""):
        asDate=sDateTime.split(NT_ENV_DATE_DIV)
        asDate=ntSys.NF_ArrayStrNorm(asDate,"SLR")
        nLen=len(asDate)
        if nLen<2: sResult="NoValid sep"
    if (sResult==""):
        # Estrae
        sDate=asDate[0]
        sTime=asDate[1]
        if nLen==3: nMsec=int(asDate[3])
        # Converte da Str a dt/tm
        dtDate=NF_DateYYYYMMDD_fStr(sDate)
        tmTime=NF_TimeHHMMSS_fStr(sTime)

# Uscita
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult, dtDate, tmTime, nMsec]
    return lResult

# Ritorna microsecondi
def NF_DateMsec(dtDate):
    return int(dtDate.strftime("%f"))

# Da Data a AAAAAMMDD Str
def NF_DateStrYYYYMMDD(dtDate):
    sResult=str(dtDate)
    #print("D1:" + sResult)
    sResult=sResult.replace("-","")
    #print("D2:" + sResult)
    sResult=ntSys.NF_StrLeft(sResult,8)
    #print("D3:" + sResult)
    return sResult

# Da YYYYMMDDStr a Data
def NF_DateYYYYMMDD_fStr(sDate):
    nYear=int(ntSys.NF_StrLeft(sDate,4))
    nMonth=int(ntSys.NF_StrMid(sDate,6,2))
    nDay=int(ntSys.NF_StrMid(sDate,7,2))
    dtDate=datetime(nYear,nMonth,nDay)
    return dtDate

# Da HHMMSSStr a Time
def NF_TimeHHMMSS_fStr(sTime):
    tmTime=datetime.strptime(sTime, '%H%M%S')
    return tmTime

# Da Time a AAAAAMMDD Str
def NF_TimeStrHHMMSS(tmTime):
    sResult=str(tmTime)
    sResult=ntSys.NF_StrMid(sResult,11,8)
    sResult=sResult.replace(":","")
    sResult=ntSys.NF_StrLeft(sResult,6)
    return sResult

# Attesa
def NF_Wait(nSecondi):
    time.sleep(nSecondi)

# ----------------------- CLASSI ---------------------------

# ---------- NC_SYS - jData - ntJobs.App -------------------
# ntJobs System Class APP + LOG
class NC_Sys:
# Arguments and Setup
    sID=""              # ID Applicazione
    bINI=False          # INI Obbligatorio
    bTest=False         # Test Mode Obbligatorio
    sIniTest=""         # INI File di Test (se TestMode=True)
# Application Path
    sSys_Path=""        # ntJobs Kit Path Root
    sJob_Path=""        # Job File Path
    sJob_File=""        # Job File (Normalizzato)
# TimeStamp
    sTS_Start=""        # TimeStamp: Start
    sTS_End=""          # TimeStart: End
# INI Config + Actions in sequenza
    sFileINI=""         # File INI
    dictINI={}          # Config dict - Che viene passato a ntJobs.OS
    dictINI_Fields={}   # Tipizzazione particolare (per tutte le sezioni).
    dictSections={}     # Sections - Config + Parametri richiamo Actions in sequenza
    dictJob             = JobCorrente. Action, Files.*=, Vars.*= )
# Azione Corrente: Ingresso
    sSection=""          # Sezione Corrente da cui deriva dictJob che viene separato in singolo jobs.ini e passato a ntjobs.OS
# Azione Corrente - RITORNO
    sResult=""          # Return Value
    sRetType=""         # Return Type, E=Errore, ""=Ok, W=Warning
    dictReturnFiles={}  # Eventuali file di ritorno dict [FILE.ID=FILE.PATH.NORM]
# Ritorno di tutte le azioni Eseguite (sezione= nome_sezione_non_config, RET.VAL, RET.TYPE, FILE.ID=VALORE, CONFIG=Sezione ritorni prima delle azioni)
    dictReturn={}       # Sezione END di Ritorno Calcolata per scrittura - UNA VOLTA SOLA VIENE SCRITTO

# CSV Main Data
    sFileCSV=""         # File.CSV - LETTO DA self.dictINI
    objCSV=None         # Oggetto CSV creato se esiste file
# File di LOG Globale - DA IMPLEMENTARE
    sLogFile=""
    sLogTag=""
    sLogToFile=False
    sLogProc=""

# Metodi (Init)
# --------------------------------------------------------------------------------
    def __init__(self,sID_set):

# Init jData
        locale.setlocale(locale.LC_ALL, "it_IT.UTF8")
        self.sID=sID_set
        self.sTS_Start=NF_TS_ToStr()
        self.sSys_Path=os.getcwd()
        self.sLogFile=self.sSys_Path + "\\Log\\" + self.sID + ".log"
        print("ntJob.Start: " + self.sID + ", TS: " + self.sTS_Start)

# Attributi
# --------------------------------------------------------------------------------
    def LogAttr(self, sAttr, vValue):
        if sAttr=="P": self.sLogProc=vValue
        elif sAttr=="T": self.sLogTag=vValue
        elif sAttr=="F": self.sLogToFile=vValue

    # Scrive Riga LOG
    def Log(self, sLog):
        sText=f"{self.sID}.{self.sLogProc}.{self.sLogTag}"
        sText=sText + NF_TS_ToStr() + ": " + sLog
        if self.sLogFile!="":
            ntSys.NF_FileFromStr(sLog, self.sLogFile,"a")
        else:
            print(sLog)

# Sezione Legge file INI + Parametri di default
# Ritorno lResult. 0=Stato, 1=dictINI se trovato File.INI di config con sezione [CONFIG] o None, 2=FileCSV_normalizzato, 3=Records
# Parametri:
#    FILE.INI=File da leggere - gia' normalizzato
#    FIELDS.TYPE: dict. Campi accettati come valore hanno il tipo "(N)Number o (B)Boolean o (I)Integer (D)ata"
#    ACTIONS: Array Stringa azioni accettate
# Ritorno: sResult (e impostato self.sFileINI, self.dictINI
# -------------------------------------------------------
    def ReadINI(self):
        sProc="JOBS.ReadINI"
        sResult=""

# Setup
        self.dictINI=dict()
        self.sResult=""

# Parametri - Prende e Verifica
# -------------------------------------------------------

# Verifica su 3 parametri
        if self.sFileINI=="": sResult=ntSys.NF_StrAppendExt(sResult, "FILES.INI mancante")
        if self.asActions==None: sResult=ntSys.NF_StrAppendExt(sResult, "Lista azioni mancante")

# Legge INI
        if sResult=="":
            ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura file INI:" + self.sFileINI, sProc)
            lResult=ntDataFiles.NF_INI_Read(self.sFileINI)
            sResult=lResult[0]

# Prende sezione CONFIG
        if sResult=="":
    # Verifica che ci sia Config
            self.dictSections=lResult[1]
            if ntSys.NF_DictExistKey(self.dictSections,"CONFIG"):
                self.dictINI=self.dictSections["CONFIG"]
                if ntSys.NF_DictLen(self.dictINI)<1: sResult="sezione CONFIG vuota"
            else:
                sResult="Sezione CONFIG non esistente"

# Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
        if sResult=="":
            self.dictINI=ntSys.NF_DictConvert(self.dictINI, self.dictINI_Fields)
            if len(self.dictINI)==0: sResult="Conversione KEYS CONFIG in dict"

# Verifica Azione
        if sResult=="":
            self.sAction=self.dictINI["ACTION"]
            if ntSys.NF_ArrayLen(self.asActions)>-1:
                if ntSys.NF_ArrayFind(self.asActions,self.sAction)==-1:
                    sResult="Azione non prevista: " + self.sAction

# Completamento:
        ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Letto file INI. Eventuali errori: " + sResult, sProc)

# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Legge file CSV di dati del JOB (se previsto)
# Parametri:
#   dictINI: Standard ntJobs CONFIG
# Ritorno
#   sResult=Risultato
#   Cambia , 2=FileCSV normalizzato se trovato File.csv, 3=Records
# -------------------------------------------------------
    def ReadCSV(self):
        sProc="JOBS.ReadCSV"
        sResult=""

# Legge Parametri da Config
        self.sFileCSV=ntSys.NF_DictGet(self.dictINI,"FILE.CSV","")
# Conversione FIELDS.CSV da String a Array
        sFieldsCSV=ntSys.NF_DictGet(self.dictINI,"FIELDS.CSV","")
        asFieldsCSV=ntSys.NF_StrSplitKeys(sFieldsCSV,",")
        ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura CSV: " + str(asFieldsCSV), sProc)
# Se non c'è File CSV Esce
        if self.sFileCSV=="": return ""
# Normalizzazione CSV FILE
        lResult=ntSys.NF_PathNormal(self.sFileCSV)
        sResult=lResult[0]
        if sResult=="":
            self.sFileCSV=lResult[5]
            dictParams={
                "FILE.IN": self.sFileCSV,
                "FIELDS": asFieldsCSV,
                "FIELD.KEY": ntSys.NF_DictGet(self.dictINI,"FIELD.KEY","")
            }
# Crea componente NC_CSV in jData
            self.objCSV=NC_CSV()
# Lettura CSV File e Ritorno
            ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Lettura CSV: " + ntSys.NF_DictStr(dictParams), sProc)
            sResult=self.objCSV.Read(dictParams)
# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Arguments
# Parametri
# INI.YES: Obbligatorio File INI
# TEST.YES: Previsti file di test, allora ci deve essere anche TEST.INI
# Ritorno lResult. 0=sFileINI
# ------------------------------------------------------------------------------------
    def Args(self):
        sProc="JOBS.ARGS"
        sResult=""

# INI Obbligatorio o Facoltativo

# Controlli
    # Se da TEST
        if self.bTest:
        # Debug
            dictParams={"INI.YES": self.bINI, "TEST.YES": self.bTest, "INI.TEST": self.sIniTest, "ACTIONS": self.asActions}
            ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Parametri job: " + ntSys.NF_DictStr(dictParams), sProc)
        # INI.TEST
            if self.bINI:
                if self.sIniTest=="":
                    sResult="Non previsto file TEST.INI in Test Mode"
                else:
                    self.sFileINI=self.sIniTest
                ntSys.NF_DebugFase(self.bTest, "Utilizzo INI Demo. INI: " + self.sFileINI, sProc)
        else:
    # Oppure Prende INI da ARGS reale
            if self.bINI:
                parser = argparse.ArgumentParser()
                parser.add_argument("sFileINI", help="InputFileConfig.INI ")
                args = parser.parse_args()
                if args.count>0 and self.bINI: self.sFileINI=args.sFileINI
                ntSys.NF_DebugFase(self.bTest, "Utilizzo INI da CMDLINE: " + self.sFileINI, sProc)

    # Verifica Parametri
                if self.sFileINI=="": sResult="Non specificato parametro File INI"

# Normalizzazione INI
        if sResult=="":
            lResult=ntSys.NF_PathNormal(self.sFileINI)
            self.sFileINI=lResult[5]
            ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "File INI: " + self.sFileINI, sProc)

# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Crea file JOBS.END nella stessa cartella file JOBS.INI con sezione [END]
# Parametri:
#   JOB.PATH: Cartella del JOB.
#   RETURN.TYPE: RETURN.TYPE=E=Errore/W=Working/Nulla=OK
#   RETURN.VALUE=Messaggio di ritorno
#   TS.START, TS.END = TimeStamp di inizio e fine
# Ritorno: sResult
# ------------------------------------------------------------------------------------
    def WriteEnd(self):
        sProc="JOBS.WRITE.END"
        sResult=""

# Setup
        self.sTS_END=NF_TS_ToStr()

# Verifiche
        if self.sRetType=="": sResult=ntSys.NF_StrAppendExt(sResult, "Return type null")
        if self.sTS_START=="": sResult=ntSys.NF_StrAppendExt(sResult, "TS_START null")
        if self.sJob_Path=="": sResult=ntSys.NF_StrAppendExt(sResult, "JobPath null")

# Preparazione dict di tipo "INI" sezione [END] del file JOBS.END
        if sResult=="":
            sFileEnd=ntSys.NF_PathMake(sJobPath, "jobs", "end")
            self.dictReturn={
                "RETURN.TYPE":  self.sRetType,
                "RETURN.VALUE": self.sResult,
                "TS.START": self.sTS_START,
                "TS.END": self.sTS_END
            }
        # Scrive Ritorno
            dictReturnS={"END",dictReturn}
            sResult=ntDataFiles.NF_INI_Write(sFileEnd, dictReturnS)

# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        ntSys.NF_DebugFase(NT_ENV_TEST_JIO, "Scritto FILE.END " + sFileEnd + ", Eventuali errori: " + sResult, sProc)
        return sResult

# Calcola Dictionary di Ritorno da Scrivere su File
# Imposta dictReturn, Ritorno: sResult
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalc(self):
        sProc="JOBS.RETURN.CALC"
        sResult=""

# Conclusione JOB
        self.sTS_End=NF_TS_ToStr()
        print ("ntJob.End: " + self.sID + ", TS: " + self.sTS_End)

# Calcola RetType
        if self.sResult!="":
            self.sRetType="E"
        else:
            self.sRetType=""

# Crea dictReturn
        self.dictReturn={
            "TS.START": self.sTS_Start,
            "TS.END": self.sTS_End,
            "RETURN.TYPE": self.sRetType,
            "RETURN.VALUE": self.sResult,
            "JOB.PATH": self.sSys_Path
            }

# Aggiunge Files PDF Creati
        if ntSys.NF_DictLen(self.dictReturnFiles)>0:
            asKeys=ntSys.NF_DictKeys(self.dictReturnFiles)
            nCounter=0
            for sKey in asKeys:
                nCounter=nCounter+1
                sFile=ntSys.NF_DictGet(self.dictReturnFiles, sKey,"")
                self.dictReturn["FILE." + sKey]=sFile
                self.dictReturn["RETURN.FILES"]=str(nCounter)

# Fine
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Calcola Ritorno e Lo scrive
#   Oggetto ntJobs.App, Scrive sResult e dictReturnFiles
# Ritorno: sResult
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcWrite(self):
        sProc="JOBS.RETURN.CALC.WRITE"

# Calcola Ritorno
        sResult=self.ReturnCalc()

# Scrive Ritorno
        if sResult=="": sResult=self.WriteEnd()

# Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

