#
# CLASSE Jobs Orchestratore. Gestisce Users e dati correlati, Actions e dati correlati
# Fasi:
# 1: Legge USERS
# 2: Legge ACTIONS
# 3: Legge Groups
# 4: Legge CONFIG (comune a tutti gli scripts JOBS) - A differenza degli altri è un dict non un Table
# 5: Genera lista PATHS/CANALI da ricercare
# ---- Actions ----
# __init__: Inizializzazione
# Get: Cerca jobs nei folders e sposta in Inbox
# Exec: Esegue Jobs
# End: Trova quelli finiti
# Archive: Ritorna risultati Jobs & Archiviazione del Job da Inbox in Archive

# Per Wait ed altro
import ntSys, ntDataFiles, ntTableClass

asFMT_JOBS_USERS=("USERID","USERPASSWORD","USERNAME","USERNOTES","USERGROUPS","USERPATHS","USERMAIL","USERACTIONS")
asFMT_JOBS_GROUPS=("GROUPID","GROUPNAME","GROUPNOTES")
asFMT_JOBS_ACTIONS=("ACTIONID","ACTIONNAME","ACTIONGROUPS","ACTIONSCRIPT","ACTIONENABLED","ACTIONUSERS","ACTIONPATH","ACTIONORDER","ACTIONTIPS","ACTIONHELP")

NT_ENV_TEST_JOBS=True
JOBS_CFG=0
JOBS_ACT=1
JOBS_USR=2
JOBS_USG=3
asPath=[]

# ----------------------------- CLASSI ---------------------------
# ntJobs System Class APP + LOGF
class NC_Jobs:
# ID dictUsers="ID"(id_utente), dictActions=ID(idAction). Poi Array con camp
    
    sResult=""
    dictJob=dict()
    dictPaths=dict()
    sFilesJob=[]
    asCSV=["CONFIG","ACTION","USERS","GROUPS"]
    
    objMail=None
    
    asUsers=[]
    asActions=[]
    asGroups=[]
    asConfig=[]

    JOB_DAT_INI=0
    JOB_DAT_ACT=1
    JOB_DAT_USR=2
    JOB_DAT_USG=3
    
    tabData[JOB_DAT_INI]=dict()
    tabData[JOB_DAT_ACT]=NC_Table()
    tabData[JOB_DAT_USR]=NC_Table()
    tabData[JOB_DAT_USG]=NC_Table()
    
# Init
# ------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.sResult=self.INI_Read()
        if (self.sResult==""): self.sResult=self.Paths()
        
# Legge DATI di partenza, config.ini, users.csv, actions.csv
# --------------------------------------------------------------------    
    def INI_Read(self):
        sProc="INI_Read"
        sResult=""
        self.sResult=""

        # Lettura DATI
        for nIndex=0 in ntSys.NF_DictLen(self.asCSV)-1:

        # NomeFile e Normalizzazione
            sFile="Data/ntjobs_" + asCSV[nIndex] + ".csv"
            lResult=ntSys.NF_PathNormal(sFile)
            sResult=lResult[0]
            if sResult=="": sResult=ntSys.NF_FileExistErr(lResult[1])

        # Lettura INI o CSV =dict Interno
            if sResult=="":
                sFile=lResult[1]
                ntSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Legge config " + sFile, sProc)
                if nIndex==self.JOB_DAT_INI: 
                    lResult=ntDataFiles.NF_INI_Read(sFile)
                else:
                    lResult=ntDataFiles.NF_CSV_Read(sFile)
                sResult=lResult[0]

        # Fine e Ritorno
            if sResult=="":
                self.tabData[nIndex]=lResult[1].copy()
            else:
                break
            
        # Aggiorna Tabelle
        if sResult=="":
            asUsers=self.Users()
            asActions=self.Actions()
            asGroups=self.Groups()
            asConfig=self.Configs()

        # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult
    
# Users/Groups/Actions
# --------------------------------------------------------------------
    def Users(self):
        asResult=self.tabData[JOB_DAT_USR].GetCol("USERNAME")
        return asResult
    
    def Configs(self):
        asResult=ntSys.NF_DictKeys(self.tabData[JOB_DAT_INI])
        return asResult
        
    def Groups(self):
        asResult=self.tabData[JOB_DAT_USG].GetCol("GROUPNAME")
        return asResult
    
    def Actions(self):
        asResult=self.tabData[JOB_DAT_ACT].GetCol("ACTIONNAME")
        return asResult
    
# Creazione path da esplorare
# Dato Array di Paths divisi da ",", vengono splittati ed aggiunti ad Array finale, togliendo gli spazi
# Per gestire il ritorno di errori legati al path viene creato un dict ed associato lo user 
# --------------------------------------------------------------------
    def Paths(self):
        asPaths=self.tabData[JOB_DAT_USR].GetCol("USERPATHS")
                
    # Split di tutti i paths e manda su array asResult
        for sTemp in asPath
        # Split+Norm
            asPaths=sTemp.split(",")
            asPaths=NF_ArrayNorm(asPaths,"LR")        
        # Cerca Usser
            nIndex=tabData[JOB_DAT_USR].Index("USERPATHS",sTemp)
            if nIndex > 0:
                sUser=tabData[JOB_DAT_USR].GetValue(nIndex, "USERID")                
        # Per Ogni Path attribuisce user come valore
            for sPath in asPaths
                self.dictPaths[sPath]=sUxdf        

# Get: Ricerca tra i path jobs.ini, lo legge  e lo sposta in inbox insieme ai files associati
# Se Trova JOB ma non trova tutti i file con errori effettua un return senza spostamento all'utente
# ------------------------------------------------------------------------------------------
    def Get(self):
        sProc="Jobs.Get"
        sResult=""
        self.sResult=""
        
    # Per tutti i Paths Previsti
        for sPath in ntSys.NF_DictKeys(self.dictPaths)
        # Prende utente associato al path
            sUser=self.dictPaths[sPath]
        # Lista dei files jobs*.ini
            lResult=self.Jobs_Find(sPath,"J")
            sResult=lResult[0]
        # Per tutti i files JOBS*.INI del path trovato, salvo errore
            if sResult=="":
                asFiles=lResult[1]
                nFiles=NF_ArrayLen(asFiles)
            # Se Trovato almeno 1
                if nFiles>0: 
            # Legge INI e Sposta File o ritorno MAIL            
                    for sFile in asFiles:                        
                        sResultGet=self.Get_Move(sFile)
                        if sResultGet != "":
                            dictReturn={"USER": sUser, "RESULT": sResult, "JOBFILE": sFile, "TYPE": "G"}
                            self.Jobs_Return(dictReturn)
                        
        # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult
            
# Legge INI di un JOB. Tutti i file che iniziano per jobs
    def Jobs_Read(self, sFileJob):
        sProc="Jobs.IniRead"
        sResult=""
        
    # Legge INI
    # Ritorna lResult 0=Ritorno, 1=IniDict, dove Trim/UCASE.KEY e valori "trimmati"
        lResult=ntDataFile.NF_INI_Read(sFileJob)
        sResult=lResult[0]
        if (sResult==""):
            self.dictJob=lResult[1]
            self.asFilesJob=[]
            asKeys=ntSys.NF_DictKeys(self.dictJob)
            for sKey in asKeys
            # Se lo trova, lo estra, lo Normalizza e lo aggiunge ai file Extra
                if ntSys.NF_StrSearch("FILE.",sKey,-1):
                    asFileExtra=self.dictJob(sKey)
                    lResult=ntSys.NF_PathNormal(asFileExtra)
                    sFileExtra=lResult[1]
                    asFilesJob.append(sFileExtra)
            # Aggiunge File Jobs
            self.asFilesJob.Append(sFileJob)
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Sposta i files di un job in cartella Inbox\JOB_ID
# 
# Path: Cartella da spostare dove ci deve essere almeno un file jobs.ini ma ci sono anche più jobs
# Importante ci siano anche i files associati o il processo viene bloccato
    def Jobs_Move(self, dictJob):
        sProc="Jobs.Move"
        sResult=""
                
    # Estrae
        sPath=dictJob["JOBFILE"]
        if ntSys.NF_NullToStr(sPath)=="": sResult="job.ini non specificato"
                
    # Estrae Job. Toglie "_" che identifica finito
        lResult=ntSys.NF_PathScompose(sPath)
        sJobID_in=lResult[1]
        sJobPath_in=lResult[1]
            
    # Lista files da spostare
        if sResult=="":
            asFiles=[sPath]
            for sKey in ntSys.NF_DictKeys(dictJob):
                if ntSys.NF_StrSearch(-1,sKey,"FILE."):
                    sFileToMove=ntSys.NF_PathMake(self.sInbox,dictJob[sKey],"")
                    asFiles.append(sFileToMove)
                    
    # Verifica esisgtenza, se non esistono tutti NON PROSEGUE
            for sFile in asFiles:
                if ntSys.NF_FileExist(sFile)==False: sResult=NF_StrAppendExt(sResult, "not.exist=" + sFile, ",")
                
    # Creazione Folder + Spostamento files 
            if sResult=="":                
            # Crea Folder
                sJobID_out=ntSys.NF_TS_Now()
                sPathJob_out=ntSys.NF_PathMake(self.sInbox,sJobID_out)
                sResult=os.makedir(sPathJob)
            # Se creato folder, sposta file
                if sResult=="":
                    for sFile in asFiles:
                        lResult=ntSys.NF_PathScompose(sFile)
                        sFileOut=ntSys.NF_PathMake(self.sInbox, lResult[1], lResult[2])
                        sResult=os.move(sFile,sPathJob_Out)                
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult

        
# Exec: 1: Cerca se ci sono JOBS
# ------------------------------------------------------------------------------------------

# Archive & Return
# --------------------------------------------------------------
----------------------------
    def Archive(self):
        sProc="Archive"
        sResult=""
        sJobEnd=""
        
    # Ricerca
        asFind=self.Jobs_Find("A")
        sResult=lResult[0]
        if sResult=="":    
    # Spostamento (Archiviazione) + Archiviazione
            # Per ogni cartella...
            asFind=lResult[1]
            for sFind in asFind:
            # Legge Job
                sResult=
            # Email di ritorno
                sResult=self.Arc_Return(dictJob)
            # Archiviazione
                if sResult=="":
                    sResult=self.Arc_Archive(sResult)    
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult
    
    # Cerca Cartelle Job con caratteristiche - Ritorna lResult. Se 0=ERROR, 1=Lista path jobs da arhiviare
    # Type="A"= DaArchiviare, "J": Da Eseguire
    def Jobs_Find(self, sType="J"):
        sProc="Arc.Return"
        asResult=[]
        
    # Prende Inbox
        sPathInbox=self.Config("INBOX")
        sPathInboxJ=ntSys.NF_PathMake(sPathInboxJ,"jobs*","")
        sResult=ntSys.NF_FileExistsErr(sPathInbox):        
        
    # Cerca Path da archiviare. Solo Folder non ricorsivo
        switch sType:        
        case "A":
            sPath="_" + sPath
        case "E":
            sPath=nt
        lResult=ntSys.NF_PathFind(sPath,"DN")
        
    # Uscita
        return lResult                            
    
    def Jobs_Archive(self):
        sProc="Jobs.Arc"
        sResult=""
                
    # Muove Files
        sResult=ntSys.NF_FolderMove(sPath, sFolderArc)

    # Uscita
        return sResult
    
# Ritorno MAIL ed eventuale LOG    
    def Jobs_Return(self, dictReturn):
        sProc="Jobs.Return"
        sResult=""
        
    # Parametri
        sUser=dictReturn["USER"]
        sType==dictReturn["TYPE"]
        sJobID=dictReturn["JOBID"]
        sPath=dictReturn["JOBFILE"]
        sReturn=dictReturn["RESULT"]
        
        if sType=="A":
            sSubject="Completamento Job: " + sJobID
            sBody = sSubject + ", archiviato job."
        else
            sSubject="Errore lettura job in file " + sPath
            sBody = sSubject + "\n" + sReturn.
        
    # Invia Mail
        sResult=Jobs_MailInit()
        if sResult=="":
            dictMail=
            {
                "TO": sUser
                "SUBJECT": sSubject
                "BODY": sBody                                
            }
            sResult=self.objMail.Send(dictMail)    

    # Uscita
        return sResult
    
# Inizializzazione ambiente mail
    def MailInit(self):
        sProc="Jobs.Mail.Init"
        sResult=""
        
    # Esci se già inizializzato
        if self.bMailLogin==True: return ""
        
    # Inizializzazione oggetto mail
    # Prende da config
        asKeys=["SMTP.FROM","SMTP.USER","SMTP"]
        for sKey in asKeys:
            dictMail[sKey]=self.Config(sKey)
    # Inizializazioneg
        self.objMail=NC_Mail(dictMail)
        sResult=self.objMail.sResult
    
    # Flag Mail.Init Inizializzazione
        if sResult=="": self.bMailLogin=True
        
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# Diretto da tabConfig (che è un dictionary)
    def Config(self, sKey):
        if ntSys.NF_ArrayFind(sKey,self.asConfig)>-1:
            vValue=self.tabData[JOB_DAT_INI][sKey]
        return vValue
    
# Exec Action
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Per quelli trovati legge jobs.ini nella cartella. SOLO se TROVA JOBS.INI esegue
# 3: Read jobs.ini
# 4: Crea file JOBS.RUN
# 4: Esegue processo con wait o no.
    def Exec(self):
        sProc="Job.Exec"
        sResult=""
        
    # Uscita
		return sResult
        
# End Action
# 1: Cerca in Inbox se ci sono jobs da eseguire
# 2: Se trova jobs.end rinomina cartella con "_" davanti per indicare che è da archiviare
    def End(self):
        sProc="Job.End"
        sResult=""
        
    # Prende Inbox Path e ed 
        lResult=self.Jobs_Find("E")
        sResult=lResult[0]
        
    # Cancellazione e Rinomina
        if sResult=="":
            asPathInboxJ=lResult[1]
            for sPathInBoxJ=sPathInbox
            
                sResult=End_Archive(sPathInboxJ)
                                        
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
		return sResult

# Sottofunzione di Job.End, cerca jobs.end. se lo trova 
    def End_Archive(self, sPathInboxJ):
        sProc="Job.End.Arc"
        sResult=""
        
    # Ricerca jobs.end
        lResult=ntSys.NF_PathNormal(sPathInboxJ)
        if sResult=="":
            sPathInboxA=ntSys.NF_PathMake("_" + lResult[1])
            sResult=ntSys.NF_FileRename(sPathJobxJ,sPathInboxA)
            
    # Uscita
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
		return sResult
