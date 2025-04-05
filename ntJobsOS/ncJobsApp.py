#
# Interface for ntJobsOS FrontEnd Application. Ha sempre un file .ini come parametro (e solo quello)
# JOBS_Start_Read: Legge INI ntJobsApp
# JOBS_End_Write: Scrive INI di Fine attività
# JOBS_ARGS: Recupero parametri secondo varie opzioni permesse nel lancio FrontEnd ntJobsOS
# A differenza di NTJOBS.VBA la [CONFIG] contiene SOLO DEI SETTINGS DI CONFIGURAZIONE
# Tutte le altre sezioni vengono eseguite "in sequenza" e contengono il COMANDO e I PARAMETRI IN USCITA.
# In uscita viene creato un file .END stesso nome del .INI che contiene i RITORNI PER OGNI COMMANDO ESEGUITO con lo stesso nome della sezione 
#
import nlSys, nlExt
#import nlDataFiles
import argparse
import os, sys, locale
import ncParams

# Test mode
NT_ENV_TEST = True

# ----------------------- CLASSI ---------------------------

# ---------- NC_SYS - jData - ntJobs.App -------------------
class NC_Sys:
# Arguments and Setup
    sID = ""              # ID Applicazione
    bTest = False         # Test Mode Attivo - Deve esserci inifile
    bBreak=False          # Uscita per errore di un job (flag ebreak=true)
    nLive = 0             # Verifica processo in Live dopo N.Secondi
    sIniAppFile = ""      # INI File - File di inizializzazine applicazione, in stessa cartella dell'app. Contiene solo la [CONFIG]    
# System
    sSys_Path = ""        # ntJobs App Path Root
    sSys_File = ""        # ntJobs File Name
    dictParams={}         # Parametri per singolo comando
    objParams=None        # Gestione Parametri
# Argomenti di lancio applicazione (iniziali file.ini file.csv facoltativo)
    asArgs=[]             # Array Argomenti ntJobsApp in forma Array "posizionale", copia di sys.argv o passato come parametro per test
# jOBS.INI
    sJob_Version=""       # VERSIONE JOBFILE
    sJob_Type = ""        # Single(A)=CommandLine o Multi[I]=Letto da FILE INI
    sJob_Path = ""        # Job File Path
    sJob_File = ""        # Job File (Normalizzato completo) e ANCHE DI PARTENZA (VIENE CAMBIATO da iNIT) File dei jobs da eseguire in sequenza, passato come parametro. 
                          # Comincia con la [CONFIG] e poi le altre in sequenza
    sJob_Name = ""        # JOB.ID come somma di più JOBS - senza estensione
# TimeStamp
    sTS_Live=""           # TimeStamp Live, all'inizio = TS
    sTS=""                # TimeStamp Attuale 
    sTS_Start = ""        # TimeStamp: Start
    sTS_End = ""          # TimeStart: End
# INI Config + Actions in sequenza
    dictConfigApp={}      # INI.APP
    dictConfigJobs={}     # INI.JOB (del file JOB\.INI)
    dictConfig = {}       # Config (Sezione Config) - Da file INI.APP+INI.JOBS fusione delle 2    
    dictConfigFields = {} # Tipizzazione particolare (per tutte le sezioni).
    dictJobs = {}         # Jobs/Sections - JOBS + Parametri richiamo Actions in sequenza.
    asJobs = []           # Jobs Names List (config....ecc). CONFIG non viene utilizzato per jobs. List delle sezioni
# Job/Azione Corrente: Ingresso
    dictJob = {}          # JobCorrente. Riservate le KEYS ACTION, FILE.* VAR.* per i file associati al job e poi altri parametri 
    sAction = ""          # Azione Corrente - NON VIENE CONTROLLATO DIRITTO DI ESEGUIRLA - SOLO PER QUESTA APP
    sJob = ""             # Job corrente ID (Nome SECTION file INI)
# Sezione(jobs) Corrente da cui deriva dictJob che viene separato in singolo jobs.ini e passato a ntjobs.OS
# Azione Corrente - RITORNO
    lResult = []          # Return from CallBack
    cbActions = None      # CallBack Function
    sResult = ""          # Return Value ""=noerr, ALTRIMENTI ERRORE
    sResultNotes=""       # Maggiori chiarimenti ritorno NON NECESSARIAMENTE ERRORE
    sRetType = ""         # Return Type, E=Errore, ""=Ok, W=Warning - NON GESTITO PER ORA    
    dictReturnFiles = {}  # Eventuali file di ritorno dict [FILE.ID=FILE.PATH.NORM]
    dictReturnVars = {}   # Variabili di ritorno del job corrente
    dictReturn = {}       # dictReturn di Ritorno Calcolata per scrittura - Uns sezione per comando del file .INI - Da aggiungere da ReturnAdd
# Ritorno di tutte le azioni Eseguite (sezione= nome_sezione_non_config, RET.VAL, RET.TYPE, FILE.ID=VALORE, CONFIG=Sezione ritorni prima delle azioni)
    dictReturnS = {}      # Sezioni dictReturn di Ritorno Calcolata per scrittura - UNA VOLTA SOLA VIENE SCRITTO il file
# File di LOG Singola Sessione (job) e Globale (File)
    sLogFile = ""         # File di log Globale
    sLiveFile=""          # File di Live

#  Inizializza Applicazione
# --------------------------------------------------------------------------------
    def __init__(self):
        pass

# Inizializzazione ntJobsApp
    def Init(self, sID_set, args,**kwargs):
        sProc="JOBS.APP.INIT"
        sResult=""        
        
# Argomenti
        self.asArgs=args.copy()
        print ("App.LenArgs" + str(len(self.asArgs)))        
# Forzatura
        if NT_ENV_TEST: self.bTest=True        
# Configurazione App da Paraemtri di inizializzazione
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "Parametri di Setup App", sProc)
            asKeys=kwargs.keys()
            aValues=kwargs.values()
            for key in asKeys:
                value=kwargs[key]
        # Attiva LOG (sottinteso True)
                if key=="log":
                    if value==True:
                    # Da sistemare dopo
                        self.sLogFile = "*"
        # Attiva Test Mode - Prende File test.ini predisposto -
                elif key=="test":
                    self.bTest=value
        # Break on Error
                elif key=="ebreak":
                    self.bBreak=value
        # Callback
                elif key=="cb":
                    self.cbActions=value
        # Params
                elif key=="params":
                    self.dictParams=value.copy() 
                    self.objParam=ncParams.NC_Params                   
        # Live
                elif key=="live":
                    self.nLive=value
# TimeStart di Partenza 
        self.sTS_Start=nlSys.NF_TS_ToStr2()             
# Init jData
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "Start: Init App / Set Locale", sProc)
            try:
                locale.setlocale(locale.LC_ALL, "it_IT.UTF8")
                self.sID = sID_set
            except Exception as e:
                sResult="Errore SetLocale: " + getattr(e, 'SetLocale/GetCwd', repr(e))                       
# Set App/File Path
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "App/File Set", sProc)
            self.sSys_File=nlSys.NF_PathScript("ID.NE")
            self.sSys_Path=nlSys.NF_PathScript("PATH") 
            if self.sLogFile=="*": self.sLogFile=nlSys.NF_PathMake(self.sSys_Path + "\\Log",self.sSys_File,"log")
# Read INI.APP (Confgurazione non i jobs) - Legge se c'è, test mode o no
        if sResult=="":
            self.sIniAppFile=nlSys.NF_PathMake(self.sSys_Path,self.sSys_File,"ini")
            nlSys.NF_DebugFase(self.bTest, "Read INI File App: " + self.sIniAppFile, sProc)                    
            if nlSys.NF_FileExist(self.sIniAppFile):
                sResult=self.ReadIni("app")                         
# Legge Argomenti (dictArgs da sommare poi a dictConfig.App)
# Per ora viene usato solo il primo argomento se finisce per .INI o viene creato un job con argomenti action, 1,2,3,4 nel dictionary 
# poi verificati dalle funzioni cmd e trasformati in parametri per le act
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "Gestione Argomenti APP: " + str(self.asArgs), sProc)
            sResult=self.ArgsJobs()            
# Creazione dictConfigMerge
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "Config Merge", sProc)                        
            sResult=self.ConfigMake()
# Altre Variabili oggetto
        if sResult=="":
            self.asJobs=self.dictJobs.keys()
# Primo Log
        if sResult=="":
            nlSys.NF_DebugFase(self.bTest, "Log Start", sProc)
            self.Log("Start", proc="App.Init")
# Se Live scrive file di live iniziale
        if sResult=="" and self.nLive>0:
            nlSys.NF_DebugFase(self.bTest, "Live Set", sProc)
            self.sLiveFile=nlSys.NF_PathMake(self.sJob_Path,self.sJob_Name,"live")
            sResult=self.Live()
# Debug
        if sResult == "":
            nlSys.NF_DebugFase(self.bTest, f"File INI.APP {self.sIniAppFile}, File INI.JOBS {self.sJob_File}", sProc)
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
    
# ----------------------- FUNZIONI ARGOMENTI ---------------------------

# Interpreta Args SPECIFICO PER ncJobsApp
# Caso 1: Se il primo parametro è file .ini lo legge come Job, in questo caso la lista dei JOBS è MULTIPLA
# Caso 2: Se non è ini il primo deve essere action, gli altri key=valore, in questo caso la section è ACTION ed è SINGOLO JOB
# Ritorno: lResult 0=sResult, 1=dictLetto INI o creato, NO PARAMETRI=ERRORE
# La verifica del dictionary viene fatta da JobVerifyAll
    def ArgsJobs(self):
        sProc="ARGS.JOBS"
        sResult=""
        dictResult={}   
        sAction=""
        sArgFirst=""
        
# Determina tipologia arg(singolo job) o ini(multijob)
        nLen=nlSys.NF_ArrayLen(self.asArgs)
        nlSys.NF_DebugFase(self.bTest, "Argomenti:" + str(self.asArgs) + ", Len:" + str(nLen), sProc)        
        if nLen>1:            
            sArgFirst=str(self.asArgs[1]).lower()        
            if sArgFirst.endswith("ini"):
            # JOB DA FILE INI
                self.sJob_Type="I"
                nlSys.NF_DebugFase(self.bTest, "Legge JOBS da file ini:" + sArgFirst, sProc)
            # MONO JOB                                
            else:
                nlSys.NF_DebugFase(self.bTest, "Crea JOBS da argomenti:" + sArgFirst, sProc)
                self.sJob_Type="A"
        else:
            nlSys.NF_DebugFase(self.bTest, "No Argomenti",sProc)

# Lettura JOBS in base a TYPO JOBFILE
        # Caso "I": Deve essere con [CONFIG]
        if self.sJob_Type=="I":            
            # Scompose Job File - Get Path & Name
            # Prende IniJobFile se c'è
            self.sJob_File=nlSys.iif(nlSys.NF_ArrayLen(self.asArgs)>0,self.asArgs[1],"")
            nlSys.NF_DebugFase(self.bTest, "INI JOBFILE:" + self.sJob_File, sProc)                        
            # Normalizzazione e JobPath
            # 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
            lResult=nlSys.NF_PathNormal(self.sJob_File)
            self.sJob_Path=lResult[1]
            self.sJob_File=lResult[5]
            self.sJob_Name=lResult[2]            
            nlSys.NF_DebugFase(self.bTest, "Read INI Jobs. Path: " + self.sJob_Path + ", File: " + self.sJob_File + ", Name: " + self.sJob_Name, sProc)
            # Legge Job.INI                                
            sResult=self.ReadINI("jobs")                                    
        # Caso "A" (tutti devono essere nella forma -key value, quelli senza key davanti vengono scartati)
        else:
            sResult=self.ArgsJobs2()                    
# Conclusione
        if sResult=="":
            if nlSys.NF_DictLen(self.dictJobs)==0:
                sResult="Errore no parametri"
                                   
# Ritorno
        sTemp="JOBS Read. Type: " + self.sJob_Type + ", Jobs Read: " + str(nlSys.NF_DictLen(self.dictJobs)) + ", INI: " + self.sJob_File
        nlSys.NF_DebugFase(self.bTest,sTemp,sProc)
        return sResult
    
# ArgsJobs2: Crea una funzione di nome ArgsJobs2. Dati i parametri del programma argv, crea un dictionary di nome dictResult. 
# Assegna alla chiave "ACTION" del dictionary il valore di argv[1]. 
# A partire da argv[2] a coppie di 2, fino alla fine degli argomenti, 
# assegna il valore del primo di ogni coppia che deve cominciare per "-" (ma togli "-" dal suo nome), come chiave del dictionary [e in maiuscolo] e il valore del dictionary il secondo di ogni coppia
# Scarta tutte le coppie di argomenti dove il primo dei 2 non comincia per "-"

    def ArgsJobs2(self):
# Crea il dictionary da command line
        sProc="ARGS.JOBS2"
        sResult=""
        dictJob = {}
        self.dictJobs={}
        nLen=nlSys.NF_ArrayLen(self.asArgs)
    
    # Assegna il valore di argv[1] alla chiave "ACTION"
        if nLen > 1:
            dictJob["ACTION"] = self.asArgs[1]
        else:
        # Se non ci sono abbastanza argomenti, restituisci un dictionary vuoto
            sResult="Manca parametro Action"
    
# Itera a partire da argv[2] a coppie di 2
        i = 2
        while i < nLen - 1:
        # Prendi la coppia di argomenti
            key = self.asArgs[i]
            value = self.asArgs[i + 1]
        
        # Verifica se il primo elemento della coppia inizia con "-"
            if key.startswith("-"):
            # Rimuovi il "-" e converti in maiuscolo
                key = key[1:].upper()
            # Aggiungi la coppia al dictionary
                dictJob[key] = value
                i += 2  # Passa alla prossima coppia
            else:
            # Scarta la coppia se il primo elemento non inizia con "-"
                i += 1
                
# Imposta dizionario JOB di ritorno
        if sResult=="":
            self.dictJobs["CONFIG"]=""
            self.dictJobs["ACTION"]=dictJob.copy()
            self.sJob_File="MEMORY"
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Scrive Riga LOG. Parametri:
# Log(Obbligatorio): Riga di commento Log
# type=tipo log (s=start.app, tk=trans.ok, te=trans.err, e=errore generico, w=warning, l(default)=log, f=end.app),
# tag=Log.Tag, proc=Log.Proc
# Formato Log. TYPE;TS;TAG;LOG.NOTE
# ---------------------------------------------------------------------------------------------------------------
    def Log(self, sLog, **kaArgs):
        sProc="JOBS.APP.LOG"
        sResult=""
        sLogProc=""
        sLogTag=""
        sLogP=""        
        
    # Esci se non E' PREVISTO IL FILE DI LOG
        if self.sLogFile=="": return ""

    # Parametri Facoltativi
        if (nlSys.NF_DictLen(kaArgs)>0):
            for sKey in kaArgs.keys():                
                sValue=nlSys.NF_DictGet(kaArgs,sKey,"")
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
                        sLog="App.End"
                    else:
                        sLogP="NA"
                elif sKey=="tag":
                    sLogTag=sValue
                elif sKey=="proc":
                    sLogProc=sValue
                else:
                    sResult="Log key not supported: " + sKey

    # Creazione riga di LOG
        if sResult=="":
            sText = f"ID={self.sID} PROC={sLogProc} TYPE={sLogP} TAG={sLogTag}"
            lResult=nlSys.NF_TS_ToStr()
            sTS=lResult[1]
            sText = str(sText) + ", " + sTS + ": " + str(sLog)
    # Scrive riga di Job su LogFile e LogTrans
            sResult=nlSys.NF_StrFileWrite(self.sLogFile, sText,"a")       

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
        
# Crea Config come somma di config.app e config.job
# Ritorno: sResult
# --------------------------------------------------------------------------------        
    def ConfigMake(self):
        sProc="JOBS.APP.ConfigMake"
        sResult=""        
# Merge   
        self.dictConfig=self.dictConfigApp.copy()
        self.dictConfig=nlSys.NF_DictMerge(self.dictConfig,self.dictConfigJobs)        
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
        
# Sezione Legge file INI (type= app/jobs)
# Ritorno lResult. 0=Stato, 1=dictINI se trovato File.INI di config con sezione [CONFIG] o None, 2=FileCSV_normalizzato, 3=Records
# Ritorno: sResult
# --------------------------------------------------------------------------------
    def ReadINI(self,sType):
        sProc = "JOBS.APP.ReadINI"
        sResult = ""
        sFileINI=""
              
# Caso INI.APP
        if sType=="app":
            sFileINI=nlSys.TestFile(self.sIniAppFile)
            lResult=nlSys.NF_INI_Read(sFileINI)        
            sResult=lResult[0]                        
            if sResult=="":
                self.dictConfigApp = nlSys.NF_DictConvert(lResult[1], self.dictConfigFields)
# Caso INI.JOBS
        elif sType=="jobs":                            
            lResult=nlSys.NF_INI_Read(self.sJob_File)
            sResult=lResult[0]                        
            if sResult=="":                        
                self.dictJobs=lResult[1].copy()
# Caso INI.JOBS.ACTIONS: Sezioni dei Jobs
        # Impostazioni Post caricamento Jobs
                self.asJobs=self.dictJobs.keys()
                nlSys.NF_DebugFase(NT_ENV_TEST, "Jobs letti:" + str(nlSys.NF_DictLen(self.dictJobs)) + "," + str(self.asJobs), sProc)
        # dictJobs.Riempie: Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
                #for sKey in self.asJobs:
                    #dictJob=nlSys.NF_DictConvert(self.dictJobs[sKey], self.dictConfigFields)
                    #self.dictJobs[sKey]=dictJob.copy()
# Verifica che ci sia la config
                dictConfig=nlSys.NF_DictGet(self.dictJobs, "CONFIG", {})
                if nlSys.NF_DictLen(dictConfig)<1:
                    sResult="sezione CONFIG vuota o non esistente"
                else:
                    self.dictConfigJobs=dictConfig.copy()
# Caso Type non supportato
        else:
            sResult="Type INI non supportato"
# Completamento:
        nlSys.NF_DebugFase(NT_ENV_TEST, "Letto file INI. Eventuali errori: " + sResult, sProc)

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

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
        nlSys.NF_DebugFase(NT_ENV_TEST, "File.End: " + sFileEnd, sProc)
        nlSys.NF_DebugFase(NT_ENV_TEST, "Returns: " + str(self.dictReturnS), sProc)

# Scrive File END di ritorno
        sResult=nlSys.NF_INI_Write(sFileEnd, self.dictReturnS)
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Calcola Dictionary di Ritorno da Scrivere su File
# Imposta dictReturn, Ritorno: sResult
#   RETURN.TYPE: RETURN.TYPE=E=Errore/W=Working/Nulla=OK
#   RETURN.VALUE=Messaggio di ritorno
#   TS.START, TS.END = TimeStamp di inizio e fine
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalc(self,lResult):
        sProc="APP.RETURN.CALC"
        dictReturnExtra={}
        nLen=len(lResult)
        
# Job di Ritorno. CONFIG o JOBNAME
        sJob=nlSys.iif(self.sJob=="","CONFIG",self.sJob)        
        sReturnFiles=str(self.dictReturnFiles)
        sReturnVars=str(self.dictReturnVars)
# Calcola RetType
        self.sResult=lResult[0]
        if self.sResult!="":
            self.sRetType="E"
        else:
            self.sRetType=""
# Prende Files - Anche un EMPTY
# Prende Variabili di Ritorno        
        if nLen>1: 
            self.dictReturnFiles=lResult[1]
            nlSys.NF_DictMerge(dictReturnExtra,self.dictReturnFiles)
            sReturnFiles=str(self.dictReturnFiles)
        if nLen>2: 
            self.dictReturnVars=lResult[2]
            nlSys.NF_DictMerge(dictReturnExtra,self.dictReturnVars)
            sReturnVars=str(self.dictReturnVars)
# Conclusione JOB.SECTION
        self.sTS_End=nlSys.NF_TS_ToStr2()
        sTemp=f"JOB.SECTION.END: {self.sJob}, TS: {self.sTS_End}, Section: {sJob}, Files: {sReturnFiles}, Vars: {sReturnVars}"
        nlSys.NF_DebugFase(NT_ENV_TEST, sTemp, sProc)                                        
# Crea dictReturn
        self.dictReturn={
            "TS.START": self.sTS_Start,
            "ACTION": self.sAction,
            "JOB": self.sJob,
            "JOB.NAME": self.sJob_Name,
            "TS.END": self.sTS_End,
            "RETURN.TYPE": self.sRetType,
            "RETURN.VALUE": self.sResult,
            "RETURN.NOTES": self.sResultNotes,
            "JOB.PATH": self.sSys_Path
            }
# Aggiunge Extra se Presenti (FILES o VARS)
        #if nlSys.NF_DictLen(dictReturnExtra)>0:
        #    self.NF_DictMerge(self.dictReturn,dictReturnExtra)

# Aggiuge Files o Vars al ritorno
# Ritorno: sResult
# Parametri: 
# sType(VARS,FILES,"")
# dictAdd=ID senza spazi maiuscolo -> Valore 
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAddExtra(self, sType="", dictAdd={}):
        sProc="JOBS.APP.ReturnCalcAddExtra"        
        sResult=""
        sTag=""    
    
    # Aggiunta
        if nlSys.NF_DictLen(dictAdd)>0:                    
            asKeys=nlSys.NF_DictKeys(dictAdd)
            print(sProc + str(asKeys))
            for sKey in asKeys:
                print(sProc + str(sKey))
                if sKey != "":                    
                    if sType=="VARS":                    
                        print(sProc + " " + sType + " " + str(sKey) )
                        self.dictReturnVars[sKey]=nlSys.NF_DictGet(dictAdd,sKey,"")
                    elif sType=="FILES":
                        print(sProc + " " + sType + " " + str(sKey) )
                        self.dictReturnFiles[sKey]=nlSys.NF_DictGet(dictAdd,sKey,"")
                    else:
                        sResult=f"Tipo non previsto {sType}"
                        break
                
                    self.dictReturnFiles[sKey]=dictAdd[sKey]
    # Uscita Nulla
        return nlSys.NF_ErrorProc(sResult,sProc)

# Calcola Ritorno e Lo Aggiunge al Pool di Ritorni
#   Oggetto ntJobs.App, Scrive sResult e dictReturnFiles
# Ritorno: sResult
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAdd(self,lResult):
# Calcola Ritorno e Scrive
        self.ReturnCalc(lResult)
        self.ReturnAdd()

# Esecuzione Singoli jobs (Azioni) del JOB.INI complessivo
# ------------------------------------------------------------------------------
    def Run(self):
        sProc="JOBS.APP.RUN"
        sResult=""
        lResult=[]

# Setup
# -------------------------------------------------------------------------------------
        dictReturnS=[]

# CurrentDir = ScriptDir.
# Dichiarare TIMESTAMP.START e TIMESTART.END
        self.sTS_Start=nlSys.NF_TS_ToStr2()
        nlSys.NF_DebugFase(self.bTest, "Job Dir: " + self.sJob_Path + ", TS: " + self.sTS_Start, sProc)    
        
# Directory dove si trova il JOBFILE                                            
        os.chdir(self.sJob_Path)
                                  
# Esecuzione
# -------------------------------------------------------------------------------------

    # Ciclo Azioni
        for sJob in self.asJobs:                            
        # TimeStamp e Reset Return
            self.dictReturn={}
            self.dictReturnFiles={}
            self.dictReturnVars={}
            self.sResult=""
            self.sResultNotes=""                        
            self.sTS=nlSys.NF_TS_ToStr2()
        # Job/Azione Corrente
            self.dictJob=self.dictJobs[sJob]
            self.sJob=sJob
        # Log
            sTemp="Job.Start: " + self.sJob + ", TS: " + self.sTS
            nlSys.NF_DebugFase(self.bTest, sTemp, sProc)
            sResult=self.Log(sTemp,type="l")
        # Call Back il primo deve essere config
            if (sResult=="") and (sJob=="CONFIG"):
                self.sJob_Version=nlSys.NF_DictGet(self.dictJob,"NTJ","2.0")
                if self.sJob_Version<"2.0":
                    sResult="Errore versione NTJ " + self.sJob_Version
        # Altre Sezioni Ciclo Standard
        # 1: CallBack
            if (sResult=="") and (sJob!="CONFIG"):
                lResult=self.cbActions(self.dictJob)
        # 2: Memorizzazione ritorni per ritorno locale e jData 0=Result, 1=Files, 2=Vars, 3: Note di ritorno non errore
                self.lResult=lResult
                self.sResult=lResult[0]
                if len(lResult) > 1: self.dictReturnFiles=lResult[1]
                if len(lResult) > 2: self.dictReturnVars=lResult[2]
                if len(lResult) > 3: self.sResultNotes=""
        # 3: Aggiunge Ritorno
                self.ReturnCalcAdd(lResult)
        # Debug
                sTemp="Job.End: " + sJob + ", Ritorno: " + str(self.dictReturn)
                nlSys.NF_DebugFase(self.bTest, sTemp, sProc)
                sResult=self.Log(sTemp,type="l")
        # 4: Live 
#                if sResult=="" and (self.nLive>0):
#                nlSys.NF_DebugFase(self.bTest, "Live Set. Job: " + self.sJob + ", Live: " + self.sTS, sProc)
#                sResult=self.Live()
        # 5: Uscitta
            if (sResult != "") and self.bBreak:
                break
                                
# Fine Esecuzione JOB
# -------------------------------------------------------------------------------------

# END Job.Complessivo
        nlSys.NF_DebugFase(NT_ENV_TEST, "End " + sResult, sProc)
        self.End()
            
# Scrive Return
        sTemp="Jobs.Return: " + str(self.dictReturn)
        nlSys.NF_DebugFase(self.bTest, sTemp, sProc)        
        sResult=self.ReturnWrite()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Risultato scrittura ritorno" + sResult, sProc)
            
# Directory di partenza
        os.chdir(self.sSys_Path)

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

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
        return nlSys.NF_ErrorProc(sResult,sProc)

# String del Return
    def ReturnStr(self):
        sResult=f"Ritorno JOB. Nome: {self.sJob_Name} , Section: {self.sJob}, LenDict: {str(len(self.dictReturnS))}\n"
        for xKey in self.dictReturnS.keys():
            sResult = sResult + str(xKey) + " " + nlSys.NF_DictStr(self.dictReturnS[xKey]) + "\n"
        return sResult

# Job Verify: Verifica parametri DI TUTTI I JOBS
    def JobVerify(self):
        sProc="JOBS.VERIFY"
        sResult=""
        
    # Per tutti i JOBS caricati
        for sJob in self.asJobs:
    # Prende Job da Tabella Jobs Caricati
            sResult=self.JobGet(sJob)
            if sResult=="":
    # Caso Config
                if sJob=="CONFIG":
                    sResult=self.JobVerifyConfig()
                else:
    # Verifica Azione    
                    sAction=nlSys.NF_DictGet(self.dictJob,"ACTION","")
    # Prende dictionary Azione del Job Corrente
                    if sAction=="": 
                        sResult="Azione non dichiarata in JOB: " + sJob                        
                    else:
    # Prende Azione Corrente dal Dizionario
                        lResult=self.JobActionConfigGet(sAction)
                        sResult=lResult[0]
                        if sResult=="":
                            dictActionConfig=lResult[1].copy()
    # Verifica Parametri Job sulla base azione corrente
                            self.objParam.Reset()
                            sResult=self.objParam.Check(self.dictJob,dictActionConfig)
    # Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
    
# Prende JobCorrente dalla Tabella Job Caricati
    def Jobget(self,sJob):
        sProc="JOB.GET"
        sResult=""
# Verifica ed Assegna
        if nlSys.NF_DictExistKey(sJob):
            self.dictJob=self.dictJobs(sJob)
        else:
            self.dictJob={}
            sResult="Job non trovato nella lista: " + sJob
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)
        
# Prende da dizionario parametri l'azione corrente
    def JobActionConfigGet(self, sAction):
        sProc="JOB.ACTION.CFG.GET"
        sResult=""
        dictParam={}
# Verifica ed Assegna
        if nlSys.NF_DictExistKey(self.dictParams,sAction):
            dictParam=self.dictAction(sAction).copy()
        else:
            sResult="Action non trovata nella lista: " + sAction
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return [sResult,dictParam]
        
# TestFile
# Aggiunge _test se siamo in testmobe
# ----------------------------------------------------------------------------------------------------
    def TestFile(self,sFile):
        sResult=""
# Solo se test mode
        if self.bTest:
            sPath,sFile,sExt=nlSys.NF_FileScompose(sFile)
            sResult=nlSys.NF_PathMake(sPath,sFile + "_test", sExt)
        else:
            sResult=sFile
# Ritorno
        return sResult

# Live: Aggiunge Live ogni x secondi
# Utilizza un TS di Live specifico
# ----------------------------------------------------------------------------------------------------
    def Live(self):
        sResult=""
        sProc="APP.LIVE"

        self.sTS_Live=nlSys.NF_TS_ToStr()
        sResult=nlSys.NF_FileWrite(self.sLive_file, self.sTS_Live)

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Genera dictionary da array con chiavi pari e valori dispari
# ----------------------------------------------------------------------------------------------------
    def ArgsToDict(self, aInput):
        sProc="APP.ARGSTODICT"
        sResult=""
        dictResult = {}

        # Verifica lunghezza minima
        if len(aInput) < 2:
            sResult = "Errore: array deve contenere almeno 2 elementi"
        
        # Verifica lunghezza pari
        if sResult=="":
            if (len(aInput) - 2) % 2 != 0:
                sResult = "Errore: array deve avere lunghezza pari dopo aver saltato i primi 2 elementi"

        # Genera dictionary saltando i primi 2 elementi
        if sResult=="":
            for i in range(2, len(aInput), 2):
                dictResult[aInput[i]] = aInput[i+1]

        return nlSys.NF_ErrorProc(sResult,sProc),dictResult