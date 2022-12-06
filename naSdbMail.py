# ntJobs.Mail.SDB.py
# Conversione da formato CSV ntJobs.Mail.SDB a ntJobs.Mail
# Sintax: ntJobsSDB inputFileCSV.py outputFileCSV.py

# Setup
import nlSys, nlDataFiles
import argparse, os, csv
from datetime import date

# Setup - Costanti & Template
sSDB_T_SUBJECT='Buon compleanno $F1 da Unisin NordEst.'
sSDB_T_BODY="Ciao $F1. Il tuo sindacato Unisin Nordest ti augura buon compleanno."
# ntJobs.Mail.SDB: ID;DAY;MONTH;LASTNAME;FIRSTNAME;SEX;EMAIL;F1;F2;F3
# ntJobs.Mail: ID;TO;CC;BCC;SUBJECT;ATTACH;FORMAT;BODY;F1;F2;F3
#global asFMT_MAIL_SDB_HDR
#global asFMT_MAIL_HDR
asFMT_MAIL_SDB_HDR=["ID","DAY","MONTH","LASTNAME","FIRSTNAME","SEX","EMAIL","F1","F2"]
#asFMT_MAIL_HDR=["ID","TO","CC","BCC","SUBJECT","ATTACH","FORMAT","BODY","F1","F2","F3","ATTR"]
#sCSV_DELIMITER=";"

# Variabili GLOBALI
nTodayD=0
nTodayM=0
inFileCSV=""
outFileCSV=""
dictSDB=dict()
lResult=[]

# Test Mode
#global NT_ENV_TEST_SDB
NT_ENV_TEST_SDB=True
 
# ------------------------ FUNZIONI -------------------------------------

# Arguments
def SDB_Args():
    sProc="SDB_ARGS"
    sResult=""
    global inFileCSV, outFileCSV
    
# inFile, outFile
    if NT_ENV_TEST_SDB == True:
        print(sProc + ": TEST_MODE")
        print("Current dir: " + os.getcwd()) 
        print(sProc + ": Default in/out csv file") 
        inFileCSV="Temp/Test_ntMailSDB.csv"
        outFileCSV="Temp/Test_ntMail.csv"
    else:
        print (sProc + " Parsing Args")  
        parser = argparse.ArgumentParser()
        parser.add_argument("inFileCSV", help="Input File CSV, ntJobs.Mail format")
        parser.add_argument("outFileCSV", help="Output File CSV, ntJobs.Mail filtered with current date")
        args = parser.parse_args()
        inFileCSV=parser.args("inFileCSV")
        outFileCSV=parser.args("outFileCSV")
       
    return sResult

# Read CSV Input & Filter
def SDB_CSV_Read():
    sProc="SDB_CSV_READ"
    sResult=""
    nDay=0
    nMonth=0
    nLineaRead=0
    global dictSDB, inFileCSV
   
# Apertura   
#    csv_file_in=pd.read_csv(inFileCSV)
#    print(type(csv_file_in))
#    print(csv_file_in.head)    
#    csv_arr_in=csv_file.to_numpy()
#    print(arr)

    with open(inFileCSV, newline='') as csv_file_in:
        nLineaRead=0
        csv_reader = csv.reader(csv_file_in, delimiter=ntDataFiles.sCSV_DELIMITER)
        for row in csv_reader:
            print (sProc + ", Riga: " + str(nLineaRead))
            if (nLineaRead == 0):
                aHeader=row
                print(f'Column names are {", ".join(aHeader)}')
            else:
        # Get Day & MONTH & FILTER
                nDay=int(row[aHeader.index('DAY')])
                nMonth=int(row[aHeader.index('MONTH')])
                sEmail=row[aHeader.index('EMAIL')]
                if NT_ENV_TEST_SDB==True:
                    print("Record: " + str(nLineaRead) + ", " + str(row) + "DM: "+ str(nDay) + "/" + str(nMonth))        
        # Filter Record
                print ("Test: " + str(nDay==nTodayD) + "/" + str(nMonth==nTodayM))
                if ((nDay==nTodayD) and (nMonth==nTodayM)):                
                    dictSDB[nLineaRead]=row
                    if NT_ENV_TEST_SDB==True: print ('Aggiunto Record SDB: ' + sEmail)
                else:
                    if NT_ENV_TEST_SDB==True: print ('Non Aggiunto Record :' + sEmail)
        # Prossima Riga
            nLineaRead = nLineaRead + 1
            
    # Chiue file e fine
        csv_file_in.close()
        print(sProc + " Righe filtrate: " + str(len(dictSDB)))
        
    #print(f'Fine Lettura ntMail.SDB. Record IN: {nLineaRead} linee.')
        return sResult

# Write Output
def SDB_CSV_Write():
    sProc="SDB_CSV_WRITE"
    
# Setup    
    sResult=""
    nLinea=0
    dictRow=dict()    
    global dictSDB, outFileCSV
    anKeys=dictSDB.keys()
    lResult=[]
    
# TEST    
    print(sProc + " Righe da esportare: " + str(len(dictSDB)) + " Dati: " + str(dictSDB))
    
# Scrive File CSV. Lo scrive comunque anche se vuoto    
    with open(outFileCSV, mode='w+', newline='') as csv_file_out:        
    # Scrive Header
        csv_writer = csv.DictWriter(csv_file_out,fieldnames=ntDataFiles.asFMT_MAIL_HDR,delimiter=ntDataFiles.sCSV_DELIMITER)    
        csv_writer.writeheader()                
    # Scrive Linee        
        for nKey in anKeys:
        # Prende riga da dictionary (la riga è un array str asFMT_MAIL_SDB_HDR)
            asRow=dictSDB.get(nKey)
            # Conversione da Array a Dictionary del record MAIL_SDB corrente
            # Alla fine prende stato conversione o Errore da riportare
            lResult=ntSys.NF_DictFromArr(lResult,asFMT_MAIL_SDB_HDR, asRow)
            sResult=lResult[0]
            if ntSys.NF_StrTest(sResult) == False: 
                dictRow=lResult[1]
            else:
                sResult=ntSys.NF_ErrorProc(sResult,sProc)
                print(sResult)
            
            nLinea = nLinea + 1
            #print(f'Scrive su CSV. Record OUT: {nLinea} linee.')
            
        # Conversione record
            if ntSys.NF_StrTest(sResult) == False:
                sID=dictRow.get('ID')
                sTo=dictRow.get('EMAIL')
                sF1=dictRow.get('FIRSTNAME')
                sF2=dictRow.get('SEX')
                sF3="NON_USATO"
                sSubject=ntSys.NF_StrReplaceDict(sSDB_T_SUBJECT,dictRow)
                sBody=ntSys.NF_StrReplaceDict(sSDB_T_BODY,dictRow)
        # Scrive Record            
                dictCSV={'ID': sID, 'TO': sTo, 'SUBJECT': sSubject, 'BODY': sBody, 'FORMAT': "HTML", 'F1': sF1, 'F2': sF2, 'F3': sF3}
                print("Scrive Riga " + str(nLinea) + " su file CSV: " + str(dictCSV))                      
                csv_writer.writerow(dictCSV)
    # Close
        csv_file_out.close()
        print(f'Fine Scrittura file ntMail. Record OUT: {nLinea} linee.')
        
    return sResult
 
# -------------------- MAIN -------------------------

def main():
    sProc="MAIN"
    global inFileCSV, outFileCSV
    global nTodayM, nTodayD
        
# Current Day & Month
    dtToday=date.today()
    nTodayD=dtToday.day
    nTodayM=dtToday.month
    print('Fase: Start. Calc Today Date and Time. D:' + str(nTodayD) + ", M: " + str(nTodayM))
    
# Argomenti
    sResult=SDB_Args()
    print('Fase: Arguments Result:' + sResult)
   
# --------------- Normalize FILES NAME --------------------    
# INFILECSV    
    lResult=ntSys.NF_PathNormal(inFileCSV)
    #print("LResult:TEST.IN.CSV LResult: " + str(lResult))
    inFileCSV=lResult[5]    
    print ("NORMAL.IN.CSV: " + sResult)

# OUTFILECSV
    if (sResult==""):
        lResult=ntSys.NF_PathNormal(outFileCSV)
        #print("LResult:TEST.OUT.CSV " + str(len(lResult)))   
        if (sResult == ""):
            outFileCSV=lResult[5]
            #print ("NORMAL.OUT.CSV: " + sResult)        

# Test Zone
    if NT_ENV_TEST_SDB==True: print ("IN.CSV: " + inFileCSV + ", OUT: " + outFileCSV)
          
# ----------------- Read CSV & Filter --------------------
    print ("Fase: READ.CSV + FILTER")
    if (sResult == ''):
       print('Read SDB CSV file')                                
       sResult=SDB_CSV_Read()

# Write CSV
    print ("Fase: WRITE.CSV")
    if (sResult == ''):
       print('Write MAIL CSV file')                                
       sResult=SDB_CSV_Write()

# End
    if (sResult == ''):
       print("End: OK")
    else:
       print("End: Errore " + sResult)

# Start Default Python code
if __name__=="__main__":
    main()
