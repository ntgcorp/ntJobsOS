#
# Test ntJobOS Class e Launcher
#
import unittest
import sys
import nlSys
import nlDataFiles
from ncJobsOS import NC_Jobs 

# Test mode
NT_ENV_TEST_JOBS=True

# ntJobsOS
objNOS=NC_Jobs()

def test_Jobs_Start():
    sProc="TEST.JOBSOS.START"
    print ("Test Start ntJobsOS")
    sResult=objNOS.Jobs_Loop()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

def test_DataNames():
    sProc="TEST.JOBSOS.DATANAMES"
    
    print("Test DataNames")
    print("Test Configs:" + str(objNOS.Sys_Configs()))
    print("Test Users:" + str(objNOS.Sys_Users()))
    print("Test Groups:" + str(objNOS.Sys_Groups()))
    print("Test Actions:" + str(objNOS.Sys_Actions()))
    print("Test Paths:" + str(objNOS.Sys_Paths()))
    
    return 

def test_Jobs_Search():
    sProc="TEST.JOBSOS.SEARCH"
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)    
    # Prende Jobs Nuovi Nelle Cloud e copia in INBOX su cartelle dedicate al JOB
    sResult=objNOS.Jobs_Search()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Crea dict di CONFIG (con Merge) e lo scrive su file Inbox
def test_Jobs_Get():
    sProc="TEST.JOBSOS.GET"
    sResult=""
    
# Crea Dictionary Merge
    dictTest=["CONFIG", {"ACTION": "MAIL.SEND", "USER": "test", "PASSWORD": "password"}]
    sFileIn="Test\test_ntMail_SINGLE.ini"
    lResult=nlSys.NF_PathNormal(sFile)
    sFile=lResult[1]
    lResult=nlDataFiles.NF_INI_Read(sFileIn)
    dictINI=lResult[1]
    dictMail=dictINI["CONFIG"]
    dictTest=nlSys.NF_DictMerge(dictTest,dictMail)
    print("Dictionary JOBS.INI TEST MAIL: " + nlSys.NF_dictPrint(dictTest))
    dictINI["CONFIG"]=dictTest
    sFileOut=objNOS.Jobs_Temp()
    sResult=nlDataFiles.NF_INI_Write(sFileOut,dictTest)

# End
    test_Write_Quit()

    if sResult=="": sResult=objNOS.Loop()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + str(lResult), sProc)
    return sResult

# Test Inizializzazione ambiente mail + Invio mail
def test_Mail_Init():
    sProc="TEST.JOBSOS.MAIL"
    sResult=""
 
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    
 # Invia Mail
    dictMail={
        "TO": "Test Mail",
        "SUBJECT": "Test ntjobsos mail",
        "FROM": "$ADMIN.EMAIL",
        "BODY": "Test ntjobsos mail"
        }
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Invio mail " + str(dictMail), sProc)    
    sResult=objNOS.Mail.Init(dictMail)

    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Test Creazione jobs.end in cartella ntJobs
def test_Write_Quit():
    sProc="TEST.JOBSOS.WRITE.OUT"    
    sResult=""

    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sFile=nlSys.NF_PathMake(objNOS.jData.sPath,"jobs","end")
    sResult=nlSys.NF_StrWriteFile(sFile, "Quit")
    return sResult
    
# Test Jobs_Temp
def test_Jobs_Temp():
    sProc="TEST.JOBSOS.TEMP"
    sResult=""        
    
    sResult=objNOS.Start()
    dictINIs={"CONFIG": {"USER": "TEST","PASSWORD": "PASSWORD"},"EXAMPLE": {"RETURN.VALUE": "ERR"}}
    if sResult=="": sResult=objNOS.Jobs_Temp(dictINIs)
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Test Read
def test_Jobs_Read():
    sProc="TEST.JOBSOS.READ"
 
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sResult=objNOS.Jobs_Read()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# TestVerifica se ci sono processi conclusi
def test_Jobs_End():
    sProc="TEST.JOBSOS.END"

    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc) 
    sResult=objNOS.Jobs_End()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult


# Tst jobs Return
# TestVerifica se ci sono processi conclusi
def test_Jobs_Return():
    sProc="TEST.JOBSOS.RETURN"

    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sResult=objNOS.Jobs_Return()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult  

# Test Archiviazione
def test_Jobs_Archive():
    sProc="TEST.JOBSOS.RETURN"

    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sResult=objNOS.Jobs_Archive()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult  

def test_Jobs_Loop():
    sProc="TEST.JOBSOS.LOOP"
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sResult=objNOS.Start()
    if sResult=="": sResult=objNOS.Loop()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult
  
def main():
    
# Crea Oggetto JOBS
    sResult=objNOS.Init()
# Test VISIONE DATACONFIG
    if sResult=="":
        print("Test njJobs.DataNames")
        sResult=test_DataNames()
# Crea Temp Job
    if sResult=="":
        print("Test Create Temp Job")
        dictJob={"CONFIG":{"USER":"test","PASSWORD":"password"},
                 "ACTION.TEST":{"ACTION":"user.test"}
                 }
        sResult=objNOS.Jobs_Temp(dictJob)
# Test SEARCH
    if sResult=="":
        print("Test njJobs.Search")
        sResult=test_Jobs_Search()

# Fine anticipata
    print(f"Result Tests: {sResult}" )
    return

# Test MAIL INIT
    if sResult=="":
        print("Test njJobs.MailInit")
        sResult=test_Mail_Init()

# Test SOLO START
    if sResult=="":
        print("Test njJobs.Start")
        sResult=test_Jobs_Start()
    
# Test GET
    if sResult=="": 
        print("Test njJobs.Get")
        sResult=test_Jobs_Get()    


# Test END
    if sResult=="":
        print("Test njJobs.End")
        sResult=test_Jobs_End()

# Test ARXHIVE
    if sResult=="":
        print("Test njJobs.Archive")
        sResult=test_Jobs_Archive()

# Test RETURN
    if sResult=="":
        print("Test njJobs.Return")
        sResult=test_Jobs_Return()

# Test LOOP
    if sResult=="":
        print("Test njJobs.Loop")
        sResult=test_Jobs_Loop()

# Fine
    print("Fine dei test: " + sResult)
    sys.exit()

# Start Default Python code
if __name__=="__main__":
    main()