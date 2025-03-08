#
# TEST LIBRARY
# DataFiles Lobrary
#
import nlSys, nlDataFiles
from nlDataFiles import NC_CSV
import ncMail
import sys

NT_ENV_TEST_TDATA=True
TEST_FILE_CSV="Test\Test_ntMail.csv"
TEST_FILE_INI="Test\Test_ntData_PDF_FILL.ini"
        
def TEST_CSV_Read():
    sProc="TEST_CSV_Read"
    global TEST_FILE_CSV
    
# Normalizzazione nome file
    print (sProc + " Fase: Normalizzazione")
    lResult=nlSys.NF_PathNormal(TEST_FILE_CSV)
    sResult=nlSys.NF_ErrorProc(lResult[0],sProc)
    
# Lettura CSV
    if sResult == "":
        sFileCSV=lResult[5]
        print (sProc + " Fase: Lettura CSV " + sFileCSV)
        objCSV=NC_CSV()
        dictParams={"FILE.IN": sFileCSV, "FIELDS": ncMail.asFMT_MAIL_HDR}
        sResult=objCSV.Read(dictParams)
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
# Fine
    if sResult=="":
        print("Lettura CSV completa. Risultato: \n" + objCSV.ToStr())
    else:
        nlSys.NF_DebugFase(NT_ENV_TEST_TDATA, nlSys.NF_StrTestResult(sResult,sProc), sProc)

def TEST_INI_Read():
    sProc="TEST_INI_Read"
    global TEST_FILE_INI
    
# Normalizzazione nome file
    print (sProc + " Fase: Normalizzazione")
    lResult=nlSys.NF_PathNormal(TEST_FILE_INI)
    sResult=nlSys.NF_ErrorProc(lResult[0],sProc)
    
# Lettura INI. Recupero dict Letto
    if sResult=="":
        sFileINI=lResult[5]
        print (sProc + " Fase: Lettura INI " + sFileINI)
        lResult=nlDataFiles.NF_INI_Read(sFileINI)
        sResult=nlSys.NF_ErrorProc(lResult[0],sProc)
        if sResult=="":
            dictINIs=lResult[1]
            dictINI=dictINIs["CONFIG"]
            nlSys.NF_DebugFase(True, "CONFIG letto: " + nlSys.NF_StrObj(dictINI), sProc)
        else:
            print(nlSys.NF_ErrorProc(sResult,sProc))
        
# Conversioni da str a numero/bool
    if sResult=="":
        dictConvert={"WAIT":"I", "SMTP.PORT":"I", "SMTP.SSL":"B"}
        dictINI=nlSys.NF_DictConvert(dictINI,dictConvert)
        print("Dict.INI Letto: " + str(dictINI))
    
# Fine
    nlSys.NF_DebugFase(NT_ENV_TEST_TDATA, nlSys.NF_StrTestResult(sResult, sProc),sProc)
        
def TEST_CSV_Header():
    global TEST_FILE_CSV
    sProc="TEST_CSV_Header"
    sFile=TEST_FILE_CSV
    lResult=nlSys.NF_PathNormal(sFile)
    sFile=lResult[5]
    objCSV=NC_CSV()
    print(nlSys.NF_DebugFase(NT_ENV_TEST_TDATA, "File CSV da leggere formato ntjobs.ntMail: " + sFile, sProc))    
    dictParams={"FILE.IN": sFile, "FIELDS": ncMail.asFMT_MAIL_HDR}
    sResult=objCSV.Read(dictParams)
    nlSys.NF_DebugFase(NT_ENV_TEST_TDATA, "Risultato: " + sResult, sProc)
    
def main():

    sep="----------------------------------------------------------------"
# Start
    print("Test Start")
    TEST_INI_Read()
    print (sep)
    TEST_CSV_Header()
    print (sep)
    TEST_CSV_Read()

    
# Fine
    print("Test End")
    sys.exit()
    
# Start Default Python code
if __name__=="__main__":
    main()    
    