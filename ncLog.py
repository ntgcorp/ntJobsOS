#-------------------------------------------------------------------------------
# Name:        Log Class
#-------------------------------------------------------------------------------
# Scrive LOG di esecuzione JOBS anche a fine metrice e fatturazioni
# Parametri:
# sLogUser (log_user)
# sLogTypeID (log_type); error,info, warning
# sLogTS=TimeStamp (log_ts)
# sLogCat=Category (log_cat)
# sLogText=Text (log_text)
# bLogAppend (log_append)
# sLogFile (log_file)
# NO RETURN
# -----------------------------------------------------------------------------
import nlSys

NT_ENV_TEST_LOG=True

class NC_LOG:
    sLogUser=""
    sLogType=""
    sLogTS=""
    sLogCat=""
    sLogText=""
    sLogFile=""
    sLogName=""
    bLogAppend=False

# -------------- METODI --------------
    def __init__(self):
        pass

# Attività di LOG
    def Log(self, sText, **kwargs):
        sProc="LOG.ADD"
        sResult=""
        sDelim=";"

    # Setup
        self.sLogText=sText
        sOld=self.sLogTS
        self.sLogTS==""

    # Parametri
        for key,value in kwargs.items():
            if key=="log_user":
                self.sLogUser=value
            elif key=="log_type":
                self.sLogType=value
            elif key=="log_ts":
                self.sLogTS=value
            elif key=="log_cat":
                self.sLogCat=value
            elif key=="log_file":
                self.sLogFile=value
            elif key=="log_name":
                self.sLogName=value

    # Calcoli parametri automaticamente
        #if self.sLogTS=="": self.sLogTS=nlSys.NF_TS_ToStr("X",sOld)
        self.sLogTS=nlSys.NF_TS_ToStr("X",sOld)
        if self.sLogType=="": self.sLogType="info"
        if self.sLogUser=="": self.sLogUser="nouser"
        if self.sLogName=="": self.sLogName="ntjobs"
        if self.sLogFile=="": self.sLogFile=nlSys.NF_PathMake(nlSys.NF_PathCurDir("log"),self.sLogName,"log")

    # Riga log scritta dopo (forse)
        asLog=[self.sLogTS, self.sLogType, self.sLogCat, self.sLogUser, self.sLogText]
        sLog=nlSys.NF_StrJoin(fast=True, text=asLog, delim=sDelim)

    # Header. Se Append non fa nulla, se il file non esiste scrive l'header e quindi poi sarà sempre append
        if nlSys.NF_FileExist(self.sLogFile)==False:
            sHeader=nlSys.NF_StrJoin(fast=True, delim=sDelim, text=["TS","TYPE","CAT","USER","TEXT"])
            sResult=nlSys.NF_FileWrite(self.sLogFile,sHeader + "\n","w")
            nlSys.NF_DebugFase(NT_ENV_TEST_LOG, "Test Header Write " + self.sLogFile + ", Result: " + sResult, sProc)

    # Write (in append sempre)
        if sResult=="":
            sResult=nlSys.NF_FileWrite(self.sLogFile,sLog + "\n","a")
            nlSys.NF_DebugFase(NT_ENV_TEST_LOG, "Test Log Write " + self.sLogFile + ", Result: " + sResult, sProc)

    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)

# LOG RESET, SOLO HEADER (DA RICHIAMARE POI IN LOG DOPO TEST
    def Reset(self, **kwargs):
        sProc="LOG.RESET"
        sResult=""

    # Parametri
        for key,value in kwargs.items():
            if key=="log_file":
                self.sLogFile=value
            elif key=="log_name":
                self.sLogName=value

    # Calcoli parametri automaticamente
        if self.sLogName=="": self.sLogName="ntjobs"
        if self.sLogFile=="": self.sLogFile=nlSys.NF_PathMake(nlSys.NF_PathCurDir(),self.sLogName,"log")

    # Scrive Header
        sHeader=nlSys.NF_StrJoin(fast=True, delim=self.sDelim, text=["TS","TYPE","CAT","USER","TEXT"])
        sResult=nlSys.NF_FileWrite(self.sLogFile,sHeader + "\n","w")

    # Uscita
        return nlSys.NF_ErrorProc(sResult, sProc)        
