# Lancio ntJobs e Schedulazione -
# ntJ_Sys: Classe Base
# ntJ_Get: Classe GET
# ntJ_Exec: Classe EXEC
# ntJ_Archive: Classe RITORNO e ARCHIVIAZIONE
import ntJobsClass, ntSys
JOBS_WAIT=STD=120

def JOBS_Start():
    
# Creazione e carica dati
    jData=NC_Jobs()
    if jData.sResult=="":
        if jData.INI_Read()=="":
# Ciclo
            while bExit==False:
    # Prende Processi
                if jData.Get()=="":
                    ntSys.NF_Wait(JOBS_WAIT_STD)
                else:
                    break
    # Esegue Processi
                if jData.Exec()=="":
                    ntSys.NF_Wait(JOBS_WAIT_STD)
                else:
                    break
    # Uscita per problemi su Get e Exec
                if jData.sResult != "":  bExit=True
    # Uscita
            if ntSys.NF_FileExist(sFileExit) and bExit==False:
                bExit=True
                sResult=ntSys.NF_FileDelete(sFileExist)
            if jData.sResult != "":  bExit=True
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

