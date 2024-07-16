commerciale@autobase.it
jenny

#-------------------------------------------------------------------------------
# Schedulazione Pool Azioni in ricezione ed esecuzione fino a ricezione jobs.end di Quit
# Creazione istanza classe NC_Jobs, start per verifica caricamento dati e LOOP azioni di polling/esecuzione/ritorno
# 20240616: Prima creazione
#-------------------------------------------------------------------------------

from ncJobsApp import NC_Sys
from ncJobsOS import NC_Jobs
import nlJobsCmd as objJobs

# Setup OGGETTI GLOBALI
jData=None
objJobs=None
JOBS_WAIT_STD=120

# Start NTJOBSOS (NJOS)
# -----------------------------------------------------------------------------
def NJOS_Start(*args):
    global objJobs,jData
    jData=NC_Sys("JOBSOS")                          # Application Object
    jData.bINI=False                                # Ini Presente
    jData.bTest=True                                # Test Mode
    jData.asActions=[ \
        "NJOS.START", "NJOS.LOOP",                  # NTJOBSOS ACTIONS
        "NJOS.RESTART","NTJOS.QUIT",
        "XLS2CSV","CSV2XLS" ]                       # CONVERSIONI XLS-cCSV
    jData.cbActions=JOBS_cbActions                  # CallBack Azioni

 # Test File
 #jData.sIniTest="Test\Test_jobsos.ini"           # Test file
    jData.sIniTest=""

# Avvio App e ntJobsOS con lettura Config
    if jData.sResult=="": objJobs=NC_Jobs(jData)

# Argomenti
    axArgs=[ \
        ["filein","Filename Input",False,""],
        ["fileout","Filename Output",False,""]]
    lResult=nlSys.NF_Args(axArgs)
    sResult=lResult[0]

# NJOS.Start (Args + Read INI/CSV)
    if sResult=="": sResult=jData.Start()

# NJOS.Run (All in One)
    if sResult=="": sResult=jData.Run()

# Fine
    return sResult

# --------------------------------- BODY SINGOLE AZIONI ----------------------

# CallBack Azioni
def NJOS_cbActions(dictParams):
    sProc="NTD_cbActions"
    global objJobs

# Setup per Ritorno
    lResult=["",{},{}]
    sAction=dictParams["ACTION"]
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "Start Azione: " + sAction, sProc)

# Azioni dell'App
# -------------------------------- NJOS ----------------------
    if sAction=="NJOS.START":
        sResult=objJobs.cmd_Start(dictParams)
    elif sAction=="NJOS.LOOP":
        sResult=objJobs.cmd_Loop(dictParams)
    elif sAction=="NJOS.RESTART":
        sResult=objJobs.cmd_Restart()
    elif sAction=="NJOS.QUIT":
        sResult=objJobs.cmd_Quit()
# -------------------------------- ALTRE AZIONI ----------------------
    elif sAction=="XLS2CSV":
# Read the Exsycel file
        sResult=cmd_XLS2CSV(sFileIn=dictArgs[0],sFileOut=dictArgs[1])
# Write CSV to XLS
    elif sAction=="CSV2XLS":
        sResult=cmd_CSV2XLS(sFileIn=dictArgs[0],sFileOut=dictArgs[1])
# ----------------------------- FINE AZIONI -------------------------
    else:
        sResult="Azione Non trovata: " + sAction

# Ritorno
    nlSys.NF_DebugFase(NT_ENV_TEST_NTD, "End Azione: " + sAction + ": " + sResult, sProc)
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult
