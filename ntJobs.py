# Lancio naJobs Componenti per eseguire una APP ntJobsOS o singoli comandi senza necessità
# di una App ntJobs controllata da ntJobsOs
# Mentre NJOS va in LOOP in questo script, ogni altro comando viene eseguito RILANCIANDO un'altra istanza dello script
# 20250420: Aggiunto XLSIMP e Sistemazioni Varie per gestire ocomandi già presenti
# 20250130: Sistemazioni varie
# 20240927: Diventa ntJobs.py ed è hub di lancio sia di ntJobsOS sia di singoli comandi tramite file .ini come parametro
# e file di supporto nella stessa cartella del file .ini
# 20240808: Piccola sistemazione - Eliminazione nlJobCmd - Tutto in questo file
# 20240616: Conversione totale
# 20240607: Aggiunge xls2csv e csv2xls da completare

# ------------------------------------------------------------------------------
import nlSys, nlExt, os, sys
from ncJobsApp import NC_Sys
import configparser

# Application Object
jData=NC_Sys()                                  

# Test Mode
NT_ENV_TEST=True

# Start App
# -----------------------------------------------------------------------------
def Start():
    sProc="JOBS.START"
    sResult=""   

# Setup e Argomenti CMDLINE
# -----------------------------------------------------------------------------
    
# DA COMPLETAE CON GESTIONE PARAMETRI OBBLIGATORI
# DICTIONART ACTION->Dictionary PARAM CON POSSIBILI VALORI con verifica. 
# Format [Simbolo]Lettera:ListaDivisaDa"
# Se inizia per  *=Facoltativo, !=Trim&Maiuscoli, @=Deve essere uno di quelli previsti in asList
# N=Numero, B=Boolean, A=AlfanumericoSenzaCaratteriParticolari, S=SimboliAscSeparator, C=A+Simboli, X=Tutto. D=SoloAlfabeticiMaiuscolo,
# M=MAIL, H=HOST,F=FileCheDeveEsistere, Z:FormatoFileAncheNonEsistente, S=SimboliAsc, C=CaratteriAscII. H=IndirizzoHost
# # JOBS.INI VIRTUALE (CREATO LIVE DA COMMAND LINE)
    dictParams={
        "CSV2XLS": {"IN.FILE":"", "OUT.FILE":"", "SHEET":""},
        "MAIL": {"CHANNEL":"*@D:SMTP",
                      "SMTP.SERVER":"H",
                      "SMTP.USER":"C",
                      "SMTP.PASSWORD":"C",
                      "SMTP.PORT":"*N",
                      "SMTP.SSL":"*B",
                      "FROM":"M", 
                      "FORMAT":"@A:HTML,TXT",
                      "MASSIVE":"*B",
                      "TO":"*C","CC":"C","BCC":"C",
                      "BODY":"*X",
                      "BODY.FILE":"*F",
                      "ATTACH":"*F",
                      "F1":"*X", "F2:":"*X","F3":"*X","ATTR":"*X"},
        "ADMIN.TEST": {"G": ["admin"], "TEXT1":"T", "NUM1":"N", "B1":"F","FILE.TEST":"Z"},        
        "USER.TEST": {},                
        "PC.RELOAD": {"G": ["admin"]},                
        "PC.QUIT": {"G": ["admin"]},                        
        "NJOS.START": {"G": ["admin"]},                                
        "NJOS.END": {"G": ["admin"]},
        "EXEC.WIN": {"G": ["admin"],"CDMLINE": ""},
        "EXEC.LINUX": {"G": ["admin"],"CDMLINE": ""},
        "NJOS.RESTART": {"G": ["admin"]},        
        "XLSIMP": {"XLS.TEMPLATE":"F", "XLS.DAT":"F", "SHEET":"A"},
        "XLS2CSV": {"IN.FILE":"F", "OUT.FILE":"Z", "SHEET":"A"},
        "CSV2XLS": {"IN.FILE":"F", "OUT.FILE":"Z", "SHEET":"*A"},                
        "XLS2ICS": {"XLS.IN":"*F", "ICS.OUT":"*Z"},
        "PDF.FILL": {"TRIM":"*B", "DELIMITER":"*S", "FIELDS":"X", 
                     "IN.FILE":"F", "FIELD.KEY":"C","FILE.PDF":"*Z",
                     "FILE.CSV":"F","FIELDS.CSV":"*A","FILE.PDF.PREFIX":"*F"}
    }
    
# Test Args - NoParametri=Test
    bTest=nlSys.iif(len(sys.argv)==1,NT_ENV_TEST,False)    
    asArgs=nlSys.iif(bTest,[sys.argv[0],"test\\test_test.ini"],sys.argv)
    nlSys.NF_DebugFase(NT_ENV_TEST, "Test.: " + str(bTest) + ", Args: " + str(asArgs),sProc)    
    
# Init Params - Versione 20250222                         
    sResult=jData.Init("NTJOBS", asArgs,
        params=dictParams,                       # Parametri associati ai comandi
        log=True,                                # Prevedi il Log
        test=bTest,                              # Test Mode
        live=0,                                  # Secondi di check di LiveApp 0=No
        cb=cbActions)                            # CallBack Azioni    
        #args=asArgs.copy(),                      # Argomenti
# Run (All in One)
# ---------------------------------------------------------------------------
    nlSys.NF_DebugFase(NT_ENV_TEST, "Start.Post.Init: " + str(jData.sID) + ", TimeStamp: " + str(jData.sTS_Start),sProc)
    if sResult=="":
        sResult=jData.Run()
# Fine
    return nlSys.NF_ErrorProc(sResult,sProc)

 # CallBack Azioni
def cbActions(dictParams):
    sProc="NTJOBS.CB.ACTIONS"
    sResult=""       

# Setup per Ritorno
# self.sResult=lResult[0]
# if len(lResult) > 1: self.dictReturnFiles=lResult[1]
# if len(lResult) > 2: self.dictReturnVars=lResult[2]
# if len(lResult) > 3: self.sResultNotes=""
    lResult=["",{},{},""]
    sAction=nlSys.NF_DictGet(dictParams,"ACTION","")
    jData.sAction=sAction
    nlSys.NF_DebugFase(NT_ENV_TEST, "Start Azione: " + sAction, sProc)    
# --------------- Azioni NJOS --------------------------
    if sAction=="NJOS.START":
        sResult=actNJOS_Start(dictParams)
    elif sAction=="NJOS.END":
        sResult=actNJOS_End()
    elif sAction=="NJOS.RESTART":        
        sResult=actNJOS_End()
        if sResult=="":
            sResult=actNJOS_Restart()
# ---------------- AZIONI ADMIN --------------------
    elif sAction=="PC.RELOAD": 
        sResult=actAdmin_Reload()
    elif sAction=="PC.QUIT": 
        sResult=actAdmin_Quit()
    elif sAction=="EXEC.WIN": 
        sResult=actAdmin_Exec_Win()
    elif sAction=="EXEC.LINUX": 
        sResult=actAdmin_Exec_Linux()

# -------------- Azioni FILE XLS/ICS ------------------------
    elif sAction=="CSV2XLS":
        sResult=actCSV2XLS(dictParams)
    elif sAction=="XLS2CSV":
        sResult=actXLS2CSV(dictParams)        
    elif sAction=="XLS2ICS":
        sResult=actXLS2ICS(dictParams)
    elif sAction=="XLSIMP":
        sResult=actXLSIMP(dictParams)    
# ---------- Azioni Applicative: PDF / MAIL -----------------------------
    elif sAction=="PDF.FILL":
        sResult=actPDF_Fill(dictParams)(dictParams)
    elif sAction=="MAIL":
        sResult=actMail(dictParams)

# ---------- Azioni VARIE -------------------------------
    elif sAction=="PATH.MIRROR":
        sResult=actPATH_Mirror(dictParams)
    elif sAction=="MAIL":
        sResult=actMail(dictParams)        
    elif sAction=="JOS.TEST.ADMIN":
        sResult=actTest(dictParams)        
    elif sAction=="JOBS.TEST.USER":
        sResult=actTest(dictParams)        
    else:
        nlSys.NF_DebugFase(NT_ENV_TEST, "Azione non valida: " + sAction, sProc)    
        sResult=f"ACTION non valida: [{sAction}]"
# Ritorno
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    lResult=[sResult]
    return lResult
# --------------------------------- AZIONI NTJOBS -------------------------------------

# NJOS Start
def actNJOS_Start():
# CMD.NJOS
    sProc="CMD.NJOS.START"
    import ncJobsOS as objNJOS
    nlSys.NF_DebugFase(NT_ENV_TEST,"NJOS Start",sProc)
    sResult=objNJOS.Init()

# LOOP
    if sResult=="":
        while objNJOS.bExitFull==False:
            nlSys.NF_DebugFase(NT_ENV_TEST,"NJOS Loop",sProc)
            sResult=objNJOS.Loop()
# EXIT PER Errore
    if sResult != "":
        objNJOS.bExitFull=True
# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Crea il file "jobs.end" per indicare nel loop di sistema che deve finire - Deve essere cancellato dallo script cmd esterno
def actNJOS_End():
    sProc="CMD.NJOS.END"
    sResult=""

# Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
# Create the .ini file in the current directory
    config_file_path = os.path.join(current_dir, 'jobs.end')
# Write 
    sResult=nlSys.NF_FileWrite(config_file_path)
# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Crea il file "jobs.restart" per indicare nel loop di sistema che deve ripartire dopo .end - Deve essere cancellato dallo script cmd esterno
def actNJOS_Restart():
    sProc="CMD.NJOS.RESTART"
    sResult=""

# Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
# Create the .ini file in the current directory
    config_file_path = os.path.join(current_dir, 'jobs.restart')
# Write 
    sResult=nlSys.NF_FileWrite(config_file_path)
# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# -------------------------------- AZIONI PDF --------------------------------

 # Azione ntJobs: PDF.FILL - Stessa cartella del file INI
# ------------------------------------------------------------------------------
# Parametri: da jData
# Ritorno: lResult 0=sResult, 1=Files di ritorno (ID=PATH)
# dictParams solo per compatibilità Interfaccia ntJobs ma non usato
# Settings Action PDF.FILL
#  FIELD.KEY:      = Campo chiave
#  FILE.PDF        = Template PDF
#  FILE.CSV        = File CSV
#  FIELDS.CSV      = Campi del file csv divisi da ","
#  FILE.PDF.PREFIX = Prefisso a nome file di output. PREFIX_KEY.PDF (SENZA PATH)
#
def actPDF_Fill(dictParams):
    sProc="CMD.PDF.Fill"
    dictReturnFiles={}
    
# Librerie
    import ncPdf
    import nlDataFiles 
    objCSV=nlDataFiles.NC_CSV()  
    objPdf=ncPdf.NC_Pdf
    
# Setup, Parametri, Verifica
    sResult_v=[""] * 5
    sResult_v[0],sFieldKey=jData.GetParam("FIELD.KEY", "Campo Key del file csv non dichiarato")
    sResult_v[1],sPDF_Template=jData.GetParam("FILE.PDF", "Template PDF non dichiarato")
    sResult_v[2],sCSV_File=jData.GetParam("FILE.CSV", "File Dati CSV non dichiarato")
    sResult_v[3],sFields=jData.GetParamKeys("FIELDS.CSV", "Campi valori non dichiarati divisi da virgola")
    sResult_v[4],sPDF_Prefix=jData.GetParam("FILE.PDF.PREFIX", "Prefisso file PDF di output non dichiarato")
    sResult_v[5],bTrim=nlSys.NF_StrBool(jData.GetParam("FILE.PDF.PREFIX", "Trim True o False"))
    sResult=nlSys.NF_StrJoin(text=sResult_v)
    nlSys.NF_DebugFase(NT_ENV_TEST, "Start PDF FILL. Check Parameters: " + sResult, sProc)

# Lettura CSV
    if (sResult==""):
# Prende Parametri
        asFields=nlSys.NF_StrSplitKeys(sFields)
        dictParams={
            "TRIM": bTrim,
            "DELIMITER": nlDataFiles.sCSV_DELIMITER,
            "FIELDS": asFields,
            "IN.FILE": sCSV_File,
            "FIELD.KEY": sFieldKey}
        sResult=objCSV.Read()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Load CSV: " + sResult, sProc)

# Lettura File PDF Template con Normalizzazione
    if (sResult==""):
        lResult=nlSys.NF_PathNormal(sPDF_Template)
        sPDF_Template=lResult[5]
        sResult=objPdf.FileRead(sPDF_Template)# Verifica Tabella CSV che ci siano record

    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST, "Read PDF Template: " + sPDF_Template, sProc)
        asKeys=jData.objCSV.Keys()
        if nlSys.NF_ArrayLen(asKeys)<1: sResult="Tabella dati CSV per PDF.FILL vuota"

# Ciclo Riempimento da Tabella CSV + Template
# ----------------------------------------------------------------------------------------------
    if sResult=="":
# Oggetto PDF        
        nlSys.NF_DebugFase(NT_ENV_TEST, "Start PDF Merge con dati in CSV", sProc)
# Merge
        for sKey in asKeys:
        # Crea FileOut
            sFilename=nlSys.NF_PathMake(jData.sJob_Path, sPDF_Prefix + "_" + sKey,"pdf")
            objPdf.PDF_sFilename=sFilename
        # Estrae Record
            dictRecord=objCSV.Record(sKey)
        # Merge uscita anche se errore
            print(sProc + ", T:" + objPdf.PDF_sModel, "F:" + objPdf.PDF_sFilename)
            sResult=objPdf.FileFill(dictRecord)
            if sResult!="":
                break
        # Log OK
            nlSys.NF_DebugFase(NT_ENV_TEST, "Creato PDF: " + sFilename, sProc)
        # Update dictResultFiles
            jData.dictReturnFiles[sKey]=sFilename

# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Mail
# ----------------------------------------------------------------------------------------
def actMail(dictParams: dict): 
    sProc="CMD_MAIL"
    sResult=""

# DA FARE
    sResult="To Be Written"

# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# ------------------------------- AZIONI EXCEL/CSV/ICS ----------------------------------

# Command CSV2XLS
# ----------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di imput csv
# FILE.OUT  = Nome file di output xls
# SHEET     = Sheet Da Esportare
def actCSV2XLS(*args):
    sProc="CMD_CSV2XLS"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# Parameters
    sFileIn=jData.GetParam("IN.FILE", "File in non dichiarato")
    sFileOut=jData.GetParam("OUT.FILE", "File out non dichiarato")
    sSheetName=jData.GetParam("SHEET", "Sheet non dichiarato")
    nlSys.NF_DebugFase(NT_ENV_TEST, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=nlSys.NF_PathRemapInOut(sFileIn,sFileOut,"xlsx")

# Debug Message
    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_csv(sFileIn)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST, "Write XLS", sProc)
        sResult=objPanda.write_to_xls(sFileOut,sSheetName)

# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Command XLS2ICS
# ----------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di iNput XLS
# FILE.OUT  = Nome file di output ICS

def actXLS2ICS(*args):
    sProc="CMD_XLS2ICS"
    sResult=""
    sFileIn=""
    sFileOut=""
    nArgs=len(args)

# Parameters
    sResult,sFileIn=jData.GetParam("IN.FILE", "File in non dichiarato")
    if sResult=="":            
        sResult,sFileOut=jData.GetParam("OUT.FILE", "File out non dichiarato")
        if sResult != "": sFileOut=""        
    else:
        sFileIn=""    
# Remapping in e out (da non specificare o "#" se da remapping
    if sResult=="":
        sResult,sFileIn,sFileOut=nlSys.NF_PathRemapInOut(sFileIn,sFileOut,"ics")
        nlSys.NF_DebugFase(NT_ENV_TEST, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut, sProc)
# Debug Message
    if sResult=="":
# Create ncICS object
        import ncICS
        objICS=ncICS.NC_ICS()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut, sProc)
        sResult=objICS.CreateFromXLS(sFileIn,sFileOut)
# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Comando XLS2CSV
# ------------------------------------------------------------------------------------------------------------
# Parametri:
# FILE.IN   = Nome file di imput xls
# FILE.OUT  = Nome file di output csv
# SHEET     = Sheet Da Importare
def actXLS2CSV(dictParams):
    sProc="CMD_XLS2SCSV"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""

# Parameters
    sFileIn=jData.GetParam("IN.FILE", "File in non dichiarato")
    sFileOut=jData.GetParam("OUT.FILE", "File out non dichiarato")
    sSheetName=jData.GetParam("SHEET", "Sheet non dichiarato")
    nlSys.NF_DebugFase(NT_ENV_TEST, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=nlSys.NF_PathRemapInOut(sFileIn,sFileOut,"csv")

    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_xls(sFileIn, sSheetName)
    if sResult=="":
        sResult,nRows,nCols=objPanda.df_size()
        nlSys.NF_DebugFase(NT_ENV_TEST, "Size DF " + str(nRows) + ", Cols: " + str(nCols),sProc)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST, "Write CSV", sProc)
        sResult=objPanda.write_to_csv(sFileOut)
# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# Comando XLS2CSV
# ------------------------------------------------------------------------------------------------------------
# Parametri:
# IN.FILE   = Nome file di imput xls
# DAT.FILE  = Nome file di output csv
# SHEET     = Sheet dopo il quale importare
def actXLSIMP(dictParams):
    sProc="CMD_XLSIMP"
    sResult=""
    sFileIn=""
    sFileDat=""
    sSheetName=""
    objImport=None

# Parameters
    sFileIn=jData.GetParam("XLS.TEMPLATE", "File in non dichiarato")
    sFileDat=jData.GetParam("XLS.DAT", "File out non dichiarato")
    sSheetName=jData.GetParam("SHEET", "Sheet non dichiarato")
    nlSys.NF_DebugFase(NT_ENV_TEST, f"Parameters. XLS.TEMPLATE: {sFileIn},  XLS.DAT: {sFileDat}, Sheet: {sSheetName}", sProc)
# Library
    from ncImportXLS import XLSXImporter
    objImport=XLSXImporter
# Action
    objImport.Start(sFileDat, sFileIn, sSheetName)
    sResult=objImport.Import()
# Fine
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# ------------------------------ AZIONI ADMIN ---------------------------    

# Spegnimento PC
def actAdmin_Quit():
    import ncSystem
    objSys=ncSystem
    objSys.sys_shutdown()
    
# Reload PC    
def actAdmin_Reload():
    import ncSystem    
    objSys=ncSystem
    objSys.sys_reload()

# Exec CmdLine Windows    
def actAdmin_Exec_Linux(dictParams={}):
    sProc="CMD.EXEC.WIN"
    sResult=""
# Exec
    sCmdLine=nlSys.NF_DictGet("CMDLINE")
    sResult=nlSys.NF_Exec(cmdline=sCmdLine)
# Fine
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]
        
# Exec CmdLine Windows    
def actAdmin_Exec_Win(dictParams={}):
    sProc="CMD.EXEC.WIN"
    sResult=""
# Exec
    sCmdLine=nlSys.NF_DictGet("CMDLINE")
    sResult=nlSys.NF_Exec(cmdline=sCmdLine)
# Fine
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]


# ------------------------------ AZIONI VARIE ---------------------------

# Solo un TEST di ntJobs
def actTest(dictParams={}):
    sProc="CMD.TEST"
    sResult=""    

# Debug
    nlSys.NF_DebugFase(NT_ENV_TEST, "Test action. Params: " + str(dictParams), sProc)

# Ritorno        
    #jData.ReturnCalcAddExtra("FILES", {"FILE.1": "test\test_mail_single.ini"})
    #jData.ReturnCalcAddExtra("VARS", dictParams)
    jData.sResultNotes="Nota di Ritorno"

# FINE
    return nlSys.NF_ErrorProc(sResult,sProc)

# Copia di un path su destinzazione.
# DA VERIFICARE
# Parametri:
# IN.PATH (SENZA WILDWARGS), OUT.PATH
# FILES: Vari path da copiare
def actPATH_Mirror(dictParams):
    sProc="CMD.PATH.MIRROR"
    sResult=""

# Verifica Folder IN e Folder Out
    asFiles=nlSys.NF_DictGet(dictParams,"FILES",None)
    sResult=nlSys.NF_ParamVerify(dictParams, {"dexist": ("IN.PATH","OUT.PATH"),"fexist": asFiles})

# Mirror
    if sResult=="":
        nlSys.NF_DebugFase(NT_ENV_TEST, "Mirror", sProc)
        sPathIn=nlSys.NF_DictGet(dictParams,"IN.PATH","")
        sPathOut=nlSys.NF_DictGet(dictParams,"OUT.PATH","")
        for sFile in asFiles:
            sFileIn=nlSys.NF_PathMake(sPathIn,sFile,"")
            sTemp=nlSys.NF_FileCopy(sFile,sPathOut,replace=True, outpath=True)
            if sTemp != "": sResult=sResult + ": " + sTemp
            nlSys.NF_DebugFase(NT_ENV_TEST, f"Copy {sFileIn} to {sPathOut}", sProc)

# FINE
    sResult=nlSys.NF_ErrorProc(sResult,sProc)
    return [sResult]

# --------------------------------- MAIN -------------------------------------
def main():

    print("ntJobs.START:" + nlSys.NF_TS_ToStr2())
    sResult=Start()
    if sResult != "":
        sys.exit(sResult)
    else:
        print("ntJobs.END:" + nlSys.NF_TS_ToStr2())
        
# Python Start
if __name__ == '__main__': main()