#
# TEST LIBRARY
# ntJob Framework
#
import ntSys, ntDataFiles
import ssl, smtplib
import sys
from ntMailClass import NC_Mail
#import MySQLdb
NT_ENV_TEST_TBASE=True

def TEST_NF_ArrayCompare():    
    sProc="ArrayCompare"
    
# Test 1: Array di tipo NON ARRAY 1
    av1=["a","b",3]
    av2=3    
    sResult=ntSys.NF_ArrayCompare(av1,av2)    
    print ("Test 1 Array compare diversi deve dare errore:" + sResult)
    
# Test 2: Array OK
    av2=["a","b",3]
    sResult=ntSys.NF_ArrayCompare(av1,av2)    
    print ("Test 2 Array compare OK:" + sResult)
    
# Test 3: Array con un elemento di tipo diverso
    av2=["a","b","3"]
    sResult=ntSys.NF_ArrayCompare(av1,av2)
    print ("Test 3 Array compare uguale deve essere vuoto:" + sResult)

# Test 4: Array con meno elementi per uno dei 2
    av2=["a","b"]
    sResult=ntSys.NF_ArrayCompare(av1,av2)
    print ("Test 4 Array compare uguale deve essere errore len diverse:" + sResult)

def TEST_NF_StrDictReplace():
    dictREC2=dict()
    dictREC2["TO"]=["to.x@x.com","to.y@y.com"]
    dictREC2["CC"]=["cc.x@x.com","cc.y@y.com"]
    dictREC2["BCC"]=["bcc.x@x.com","bcc.y@y.com"]
    sProc="TEST_NF_StrDictReplace"
    dictFields={"FROM": "from@x.com",
                "TO": ",".join(dictREC2["TO"]),
                "CC": ",".join(dictREC2["CC"]),
                "BCC": ",".join(dictREC2["BCC"]),
                "SUBJECT": "Soggetto",
                "BODY": "Corpo messaggio"}
    message="From: <$FROM>\nTo: <$TO>\n"
    message+="Subject: $SUBJECT\n\n$BODY"
    print ("Test ReplaceDict, prima sostituzione: " + str(message))
    message=ntSys.NF_StrReplaceDict(message,dictFields)
    print ("Test ReplaceDict, dopo sostituzione: " + str(message))
        
def TEST_DictKeys():
    sProc="TEST_DictKeys"
    dictTest="NonDict"
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test DictLen 1. Stringa. Deve essere -1:" + str(ntSys.NF_DictLen(dictTest)), sProc)
    dictTest=None
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test DictLen 2. None. Deve essere -1 :" + str(ntSys.NF_DictLen(dictTest)), sProc)
    dictTest=dict()
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test DictLen 3. Vuoto. Deve essere 0 :" + str(ntSys.NF_DictLen(dictTest)), sProc)
    dictTest={'x':1, 'y':2, 's':3}
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test DictLen 4. Len deve essere 3:" + str(ntSys.NF_DictLen(dictTest)), sProc)
    asKeys=list(dictTest.keys())
    sTemp = "Test dictKeys deve essere list e x,y,s: " + str(asKeys) + ", Type: " + str(type(asKeys))
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, sTemp, sProc)
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test ArrayFindKeys deve essere 1:" + str(ntSys.NF_ArrayFind(asKeys,"y")), sProc)
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test NF_DictExistKeys. Deve tornare Errore non trovata c: " + ntSys.NF_DictExistKeys(dictTest,["y","c"]), sProc)
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test NF_DictExistKey. Deve tornare Errore non trovata c: " + str(ntSys.NF_DictExistKey(dictTest,"c")), sProc)
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test NF_DictExistKey. Deve tornare True trovata y: " + str(ntSys.NF_DictExistKey(dictTest,"y")), sProc)
    
# Test DictFromKeys
    dictTest={'x':1, 'y':2, 's':(2,3), 2:99}
    dictNew=ntSys.NF_DictFromKeys(dictTest,("y","s",2))
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Test NF_DictFromKeys. Deve tornare dict di 3: " + str(dictNew), sProc)

def TEST_DictFromArr():
    sProc="TEST_DictFromArr"
    asHeader=("X1","X2","X3")
    avData=(1,"D1",False)
    lResult=[]
    lResult=ntSys.NF_DictFromArr(lResult, asHeader, avData)
    sResult=lResult[0]    
    sResult=""
    
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Start",sProc)    
    try:
# Open database connection
        db = MySQLdb.connect("localhost","testuser","test123","TESTDB" )
# prepare a cursor object using cursor() method
        cursor = db.cursor()
# execute SQL query using execute() method.
        cursor.execute("SELECT VERSION()")
# Fetch a single row using fetchone() method.
        data = cursor.fetchone()
        print("Database version : %s " % data)
        db.close()
    except:
        sResult="Apertura DB MySql"
        
# disconnect from server
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, ntSys.NF_StrTestResult(sResult,sProc),sProc)    

# def TEST_CSV_Header():
    sProc="TEST_CSV_Header"
# Normalizzazione nome file
    print (sProc + " Fase: Normalizzazione")
    lResult=ntSys.NF_PathNormal("Temp/Test_ntMail2.csv")
    sResult=ntSys.NF_ErrorProc(lResult[0],sProc)
    
    if ntSys.NF_StrTest(sResult) == False:
        sFileCSV=lResult[5]
        print (sProc + " Fase: Lettura CSV HEADER" + sFileCSV)
        dictParams={"FILE.IN": sFileCSV, "FIELDS": ntDataFiles.asFMT_MAIL_HDR}
        lResult=ntDataFiles.NF_CSV_Header(dictParams)
        sResult=ntSys.NF_ErrorProc(lResult[0],sProc)
# Fine
    if sResult=="":
        print("Lettura CSV HEADER completa. Risultato: " + str(lResult[1]))
    else:
        ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, ntSys.NF_StrTestResult(sResult,sProc), sProc)
        
def TEST_ArrayT2L:
    
        
def TEST_CSV_Read():
    sProc="TEST_CSV_Read"
    
# Normalizzazione nome file
    print (sProc + " Fase: Normalizzazione")
    lResult=ntSys.NF_PathNormal("Temp/Test_ntMail2.csv")
    sResult=ntSys.NF_ErrorProc(lResult[0],sProc)
    
# Lettura CSV
    if ntSys.NF_StrTest(sResult) == False:
        sFileCSV=lResult[5]
        print (sProc + " Fase: Lettura CSV " + sFileCSV)
        dictParams={"FILE.IN": sFileCSV, "FIELDS": ntDataFiles.asFMT_MAIL_HDR}
        lResult=ntDataFiles.NF_CSV_Read(dictParams)
        sResult=ntSys.NF_ErrorProc(lResult[0],sProc)        
# Fine
    if sResult=="":
        print("Lettura CSV completa. Risultato: " + str(lResult[1]))
    else:
        ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, ntSys.NF_StrTestResult(sResult,sProc), sProc)

def TEST_StripNoAsc():
    sProc="TEST_StripNoAsc"
    sRiga="1à\naA"
    print(sProc + ": " + ntSys.NF_StrStrip(sRiga,"SX"))
    asTemp=["àp"," s s", " x"]
    print(sProc + ": Test Strip Array: " + str(ntSys.NF_ArrayStrNorm(asTemp,"LRCSX")))

def TEST_INI_Read():
    sProc="TEST_INI_Read"
    
# Normalizzazione nome file
    print (sProc + " Fase: Normalizzazione")
    lResult=ntSys.NF_PathNormal("Temp/Test_ntMail.ini")
    sResult=ntSys.NF_ErrorProc(lResult[0],sProc)
    
# Lettura INI. Recupero dict Letto
    if sResult=="":
        sFileINI=lResult[5]
        print (sProc + " Fase: Lettura INI " + sFileINI)
        lResult=ntDataFiles.NF_INI_Read(sFileINI)
        sResult=ntSys.NF_ErrorProc(lResult[0],sProc)
        dictINI=lResult[1]["CONFIG"]
        
# Conversioni da str a numero/bool
    if sResult=="":
        dictConvert={"WAIT":"I", "SMTP.PORT":"I", "SMTP.SSL":"B"}
        dictINI=ntSys.NF_DictConvert(dictINI,dictConvert)
        print("Dict.INI Letto: " + str(dictINI))
    
# Fine
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, ntSys.NF_StrTestResult(sResult, sProc),sProc)
    
# Vari test invio mail
def TEST_Mail(sTest):
    sProc="TEST_MAIL"
    sResult=""

# TEST SINGOLA MAIL DI TESTO
# Porta viene controllata,  SSL deve essere boolena                                 
    if sTest=="SIMPLE":
        dictMail = {'TO': "ntgcorp@gmail.com",
                    'CC': "stefano.petrone@falcricrv.org",
                    'FROM': "stefano.petrone@falcricrv.org",
                    'CHANNEL': "SMTP",
                    'FORMAT': "TXT",
                    'BODY': "Testo",
                    'SUBJECT': "Soggetto",
                    'SMTP.SERVER': "smtp.falcricrv.org",
                    'SMTP.USER': "stefano.petrone@falcricrv.org",
                    'SMTP.PASSWORD': "sp",
                    'SMTP.PORT': 25,
                    'SMTP.SSL': False,
                    }
# Invio Mail        
        objMail=NC_MailClass(dictMail)        
        sResult = objMail.sResult
        #objMail.test1()
        if (sResult==""): sResult=objMail.MAIL_MailSend()

# Ritorno
    print (ntSys.NF_StrTestResult(sResult,sProc))
    
def TEST_PathNormal(sFile):
    sProc="TEST_PathNormal"
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "File da normalizzare: " + sFile, sProc)
    lResult=ntSys.NF_PathNormal(sFile)
    print(ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Risultato: " + str(lResult), sProc))
    
def TEST_CSV_Header():
    sProc="TEST_CSV_Header"
    sFile="Temp/Test_ntMail2.csv"
    lResult=ntSys.NF_PathNormal(sFile)
    sFile=lResult[5]
    print(ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "File CSV da leggere formato ntjobs.ntMail: " + sFile, sProc))    
    dictParams={"FILE.IN": sFile, "FIELDS": ntDataFiles.asFMT_MAIL_HDR}
    lResult=ntDataFiles.NF_CSV_Header(dictParams)
    ntSys.NF_DebugFase(NT_ENV_TEST_TBASE, "Risultato: " + str(lResult), sProc)
    
def main():
# ntLib
    #TEST_PathNormal("Temp/Test_ntMail.csv")
    #TEST_CSV_Header()
    #TEST_CSV_Read()
    #TEST_DictFromArr()
    TEST_NF_ArrayCompare()
    #TEST_StripNoAsc()
    #TEST_DictKeys()
    #TEST_NF_StrDictReplace()
    #TEST_Mail("SIMPLE")
    
# Fine
    print("Fine dei test")
    sys.exit()
    
# Start Default Python code
if __name__=="__main__":
    main()    
    