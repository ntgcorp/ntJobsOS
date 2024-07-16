#ftp = ftplib.FTP("ftp.nluug.nl")
#ftp.login("anonymous", "ftplib-example-1")
#data = []
#ftp.dir(data.append)
#ftp.quit()
#for line in data:
#    print "-", line

# naTransfer - File Transfer
# -----------------------------------------------------------
# File Transfer batch
# Sintax: naTransfer inputFileINI.ini
# Azioni naTransfter:
#  LOGIN (user, pwd, host, type: ftp)
#  DIR (ritorna lista di una cartella)
#  CD dir (posiziona in cartella)
#  PUT file (invia file singolo)
#  GET path (download path)
#  DEL path (cancella path)
#  LOGOFF(esce)
# ------------------------------- Setup ----------------------
import nlSys
import ftplib
from ncJobsApp import NC_Sys

# Test Mode
NT_ENV_TEST_NTF=True

# Global App Container
jData=None

# Init Transfer Class
objTrans=NC_Transfer()

# Transer Class
class NC_Transfer:
    sHost=""
    sPassword=""
    sUser=""
    sType=""
    sPath=""
    sFile=""
    objFtp=None
    bLogin=True

    def ft_login(self):
        sProc="FTRANS.LOGIN"
        sResult=""
    # FTP
        if sType=="ftp":
            try:
                objTrans.objFtp = ftplib.FTP(self.sHost)
            except:
                sResult="Ftp Host Error"
        if sResult=="":
            try:
                objTrans.objFtp.login(self.sUser, self.sPassword)
            except:
                sResult="Ftp Login Error"
    # Logged
        if sResult=="": bLogin=True

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_dir(self):
        sProc="FTRANS.DIR"
        sResult=""

        sResult=self.ft_LogTest()
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_del(self):
        sProc="FTRANS.DEL"
        sResult=""

        sResult=self.ft_LogTest()
     # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_cd(self):
        sProc="FTRANS.CD"
        sResult=self.ft_LogTest()

     # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_logoff(self):
        sProc="FTRANS.LOGOFF"
        sResult=self.ft_LogTest()

    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_put(self):
        sProc="FTRANS.PUT"
        sResult=self.ft_LogTest()
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_get(self):
        sProc="FTRANS.GET"
        sResult=self.ft_LogTest()
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

    def ft_LogTest(self):
        sResult=""
        if self.bLogin==False: sResult="Not logged"
    # Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Partenza
# Ritorno sResult
# 1: Setup interno
# 2: Argomenti di lancio
# 3: Lettura INI Setup
# 5: Esecuzione Azioni scelte
# 6: Return Execution Job
# -------------------------------------------------------
def NTF_Start():
    sProc="NTF.Start"
    global jData
    sResult=""

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    jData=NC_Sys("NTTRANS")                         # Application Object
    jData.sIniTest="Test\Test_ntTrans_FTP.ini"      # Test file
    jData.asActions=["LOGIN","DIR","PUT","GET","DEL","LOGOFF"]
    jData.cbActions=NTF_cbActions                   # CallBack Azioni

# Start (Args + Read INI/CSV)
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.Start()

# Run (All in One)
# ---------------------------------------------------------------------------
    if sResult=="": sResult=jData.Run()

# Ritorno
    return sResult

# --------------------------------- BODY SINGOLE AZIONI ----------------------

# CallBack Azioni
def NTF_cbActions(dictParams):
    sProc="NTF_cbActions"

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_NTF, "Start Azione: " + sAction, sProc)

# Azioni dell'App
    if nlSys.NF_ArrayFind(jData.asActions,sAction):
        lResult=NTF_Standard(sAction,dictParams)
        sResult=lResult[0]
    else:
        sResult="Azione Non trovata"

# Ritorno a chiamante
    nlSys.NF_DebugFase(NT_ENV_TEST_NTF, "End Azione: " + sAction + ": " + sResult, sProc)
    lResult[0]=sResult
    return lResult

# Azione ntJobs: Multipla per Trans
# ------------------------------------------------------------------------------
# Parametri: da jData
# Ritorno: lResult 0=sResult, 1=Files di ritorno (ID=PATH)
# dictParams solo per compatibilità Interfaccia ntJobs ma non usato
def NTF_Standard(sAction, dictParams):
    global objTrans
    sProc="NTF.Actions"
    dictReturnFiles={}

# Parametri
    sUser=NF_DictGet("USER","")
    sPwd=NF_DictGet("PASSWORD","")
    sHost=NF_DictGet("HOST","")
    sDir=NF_DictGet("FOLDER","")
    sFile=NF_DictGet("FILE","")
    sPath=NF_DictGet("PATH","")

# Verifica

# Esecuzione
    if sAction=="LOGIN":
        sResult=""
    elif sAction=="LOGOFF":
        sResult=""
    elif sAction=="GET":
        sResult=""
    elif sAction=="PUT":
        sResult=""
    elif sAction=="DEL":
        sResult=""
    elif sAction=="CD":
        sResult=""
    elif sAction=="DIR":
        sResult=""
# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult, dictReturnFiles]
    return lResult

# --------------------------------- MAIN -------------------------------------
def main():
    NTF_Start()
if __name__ == '__main__':
    main()
