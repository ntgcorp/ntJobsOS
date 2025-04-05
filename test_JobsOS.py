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
    print("Test Configs:" + str(objNOS.Configs()))
    print("Test Users:" + str(objNOS.Users()))
    print("Test Groups:" + str(objNOS.Groups()))
    print("Test Cmds:" + str(objNOS.Cmds()))
    print("Test Paths:" + str(objNOS.Paths()))
    
    return 

def test_Jobs_Loop():
    sProc="TEST.JOBSOS.LOOP"
    
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    sResult=objNOS.Start()
    if sResult=="": sResult=objNOS.Loop()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Crea dict di CONFIG (con Merge) e lo scrive su file Inbox
def test_Jobs_Get():
    sProc="TEST.JOBSOS.GET"
    sResult=""
    
# Crea Dictionary Merge
    dictTest=["CONFIG", {"ACTION": "MAIL.SEND", "LOGIN": "ntjobs.test", "PASSWORD": "Test.0123"}]
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

# Test Inizializzazione ambiente mail
def test_Mail_Init():
    sProc="TEST.JOBSOS.MAIL"
    sResult=""
    
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Start", sProc)
    if sResult=="": sResult=objNOS.Mail_Init()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Test Creazione jobs.end in cartella ntJobs
def test_Write_Quit():
    sProc="TEST.JOBSOS.WRITE.OUT"    
    sFile=nlSys.NF_PathMake(objNOS.jData.sPath,"jobs","end")
    sResult=nlSys.NF_StrWriteFile(sFile, "Quit")
    
# Test Jobs_Temp
def test_Jobs_Temp():
    sProc="TEST.JOBSOS.TEMP"
    sResult=""        
    
    sResult=objNOS.Start()
    dictINIs={"CONFIG": {"RETURN.VALUE": "ERR"}}
    if sResult=="": sResult=objNOS.Jobs_Temp(dictINIs)
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)
    return sResult

# Test Read
def test_Jobs_Read():
    sProc="TEST.JOBSOS.READ"
    sResult=objNOS.Jobs_Read()
    nlSys.NF_DebugFase(NT_ENV_TEST_JOBS, "Risultato: " + sResult, sProc)

def main():
    
# Crea Oggetto JOBS
    objNOS=NC_Jobs()
    sResult=objNOS.Init()
            
# Test SOLO START
    if sResult=="":
        print("Test njJobs.Start")
        sResult=test_Jobs_Start()

# Test VISIONE DATACONFIG
    if sResult=="":
        print("Test njJobs.DataNames")
        sResult=test_DataNames()
    
# Test GET
    if sResult=="": 
        print("Test njJobs.Get")
        sResult=test_Jobs_Get()    
    
# Test LOOP
    if sResult=="":
        print("Test njJobs.Loop")
        sResult=test_Jobs_Loop()

# Fine
    print("Fine dei test")
    sys.exit()

# Start Default Python code
if __name__=="__main__":
    main()