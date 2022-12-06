# Lancio ntJobs e Schedulazione -
# ntJ_Sys: Classe Base
# ntJ_Get: Classe GET
# ntJ_Exec: Classe EXEC
# ntJ_Archive: Classe RITORNO e ARCHIVIAZIONE
import ntJobsClass, ntSys

# Setup
JOBS_WAIT_STD=120
jData=None

# Start
def JOBS_Start():

# Avvio con lettura Config
    jData=NC_Jobs()
    if jData.sResult=="": sResult=jData.INI_Read()
    if sResult=="":

# Ciclo
# -----------------------------------------------------
        while bExit==False:
# Prende Processi
            sResult=jData.Get()
            if sResult != "":
                bExit=True
                break
            ntSys.NF_Wait(JOBS_WAIT_STD)

# Esegue Processi
            sResult=jData.Exec()
            if sResult != "":
                bExit=True
                break
            ntSys.NF_Wait(JOBS_WAIT_STD)

# Uscita da motore ntJobs
            sResult=jData.Quit()
            if sResult != "":
                bExit=True
                break

# Uscita
    sResult=ntSys.NF_ErrorProc(sResult,sProc)
    return sResult

# ----------------------------- MAIN --------------------------

def main():
    sProc="Main"
    sArgs=""
    lResult=JOBS_Start()
    sResult=lResult[0]
    if sResult=="":
        sResult="Jobs scheduling " + str(lResult[2])
    ntSys.NF_DebugFase(NT_ENV_TEST_JOB, "Completamento NTM_Start: " + sResult, sProc)
    exit()

# Start Default Python code
if __name__=="__main__": main()

