# ntJobs BASE LIBRARY
# -----------------------------------------------------------
# Lib per gestione path e files
from pathlib import Path
# For NF_File*
import os
# For NF_FileDelete (rmdir)
import shutil
# For NF_PathFind
import glob
from sys import platform
# Lib per gestione Replace
from string import Template

# Per Wait ed altro
import time, locale
from datetime import datetime

# Setup: TEST o NO
NT_ENV_TEST_SYS=True
# ENCODING
NT_ENV_ENCODING="utf-8"
# YYYYMMDD.HHMMSS.MSEC
NT_ENV_DATE_DIV="."
# Da inizializzare in caso di App se si vogliono usare i servizi NC_Sys
ntSysApp=None

# ----------------------- FUNZIONI ---------------------------

# IIF che in python non c'è
def iif (bExpr, trueResult, falseResult):
    if bExpr: return trueResult
    else: return falseResult

# ---------------------- FILES & PATH  -----------------------

# Ritorna Errore Standard NF_FileExist o "" come stringa.
def NF_FileExistErr(sFilename):
    sResult=iif(NF_FileExist(sFilename),"","Esistenza file " + sFilename)
    return sResult

# Alias File Exist
def NF_FileExist(sFilename):
    return os.path.exists(sFilename)

# String o Binary to File o viceversa
# sResult=Tipo di errore
def NF_FileToStr(sText, sFilename, sAttr):
    sResult=""
    sProc="FileToStr"
    
# Verifica parametri
    if NF_ArrayFind(("w","a"), sAttr)<0: sResult="parametro: " + sAttr

# Open Text File
    try:
        hFile = open(sFilename, mode=sAttr, encoding=NT_ENV_ENCODING)
    except:
        sResult="apertura file con attributo " + sAttr + ", " + sFilename

# Write string to file
    try:
        hFile.write(sText)
    except:
        sResult="scrittura su file aperto " + sAttr + ", " + sFilename
# Close file
        hFile.close()
# Uscita
    return NF_StrTestResult(sResult,sProc)

# String o Binary to File o viceversa
# sResult=Tipo di errore
# Ritorna lResult. 0=sResult, 1=Text
def NF_FileFromStr(sText, sFilename, sAttr):
    sResult=""
    sProc="FileFromStr"

# Verifica parametri
    if NF_ArrayFind(("r", "rb"),sAttr)<0: sResult="parametro: " + sAttr

# Open Text File
    if (sResult==""):
        try:
            hFile = open(sFilename, mode=sAttr, encoding=NT_ENV_ENCODING)
        except:
            sResult="apertura file con attributo " + sAttr + ", " + sFilename
# Read string from file
        try:
            hFile.read(sText)
        except:
            sResult="lettura file con attributo " + sAttr + ", " + sFilename
# Close file
        hFile.close()
        lResult=[NF_StrTestResult(sResult,sProc),sText]
# Uscita
    return lResult

# Path.Rename
# N=NonRecursive, R=Recursive, F=File, D=Directory
def	NF_FileDelete(sFile,sType="FN"):
    sProc="NF_FileDelete"
    sResult=""
    
# Flags
    bDir=NF_StrFind(0,sType,"D") != -1
    bRic=NF_StrFind(0,sType,"R") != -1
    
# Delete
    sResult="Delete file " + sFile + " with error type: " + sType
    try:
        if bDir and bRic:
            shutil.rmtree(sFile)
            sResult=""
        if bDir and bRic==False:
            os.rmdir(sFile)
            sResult=""
        if bDir==False:
            os.remove(sFile)
            sResult=""                
    except:
        sResult="Cancellazione path " + sFile + ", Type: " + sType
    
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    return sResult
    
# Path.Rename
def	NF_FileRename(sPathIn, sPathOut):
    sProc="NF_FileRename"
    sResult=""
    
# Rename   
    try:
        os.rename(sPathIn, sPathOut)
    except:
        sResult="Rinomina path " + sPathIn + " in " + sPathOut
    
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    return sResult
    
# Path.Copy/XCopy
# F=Singolo File P=Path, (F=File), D=Dir
def	NF_PathCopy(sPathIn, sPathOut, sType="F"):
    sProc="NF_PathCopy"
    sResult=""
    
# Flags
    bDir=NF_StrFind(0,sType,"D") != -1
    bPath=NF_StrFind(0,sType,"P") != -1
    bFile=(NF_StrFind(0,sType,"F") != -1) or (sType=="F")

# Rename   
    try:
        if bDir: shutil.copytree(sPathIn, sPathOut)
        if bPath: shutil.copyfile(sPathIn, sPathOut)
        if bFile: shutil.copy(sPathIn, sPathOut)
    except:
        sResult="Copia " + sPathIn + " in " + sPathOut + ", Type: " + sType
    
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    return sResult
    
# Cerca un Path, anche ricorsivo con jolly e crea un array
# R=Recursivo
# Ritorna lResult, 0=Risultato, 1=Lista
def NF_PathFind(sPath, sType=""):
    sProc="NF_PathFind"
    sResult=""
    asPath=[]
    
# Flag
    bRec=NF_StrFind(0,sType,"R") != -1
    
# Ricerca
    for f in glob.glob(sPath, recursive=bRec): asPath.append(f)
    
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    lResult=[sResult, asPath]
    return lResult
    
# PathMake File e Cartella. Non aggiunge "\" alla fine
def NF_PathMake(sPath, sFile, sExt):
    sResult=""
# Slash per OS
    sSlash=iif(NF_IsWindows(),"\\","/")
# Setup
    sResult=sPath
# Aggiunge File, prima eventuale slash
    bAdd=NF_StrRight(sPath,1) != sSlash
    if sFile != "": sResult = sResult + iif(bAdd,sSlash, "") + sFile
# Aggiunge Ext
    if sExt != "": sResult = sResult + "." + sExt    
# Ritorno
    return sResult

# Normalizza Path con verifiche ed estraendo componenti
# 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
# Result=Eventuale errore
def NF_PathNormal(sFileIn):
    sProc="NF_PathNormal"
    sPath=""
    sExt=""
    sFile=""
    sFileExt=""
    aExt=[""]
    lResult=[""]

# Null
    if (sFileIn==""): return NF_Result(lResult, sProc, "Filename null")

# Setup: CurDir, gestisce slash di default e su file passato come parametro
    sCurdir=os.getcwd()
    sFileIn=str(sFileIn)
    sSlash=iif(NF_IsWindows(), "\\","/")
    sFileIn=sFileIn.replace(iif(NF_IsWindows(),"/","\\"),sSlash)

# Aggiunge directory corrente se path relativo o nullo
    sPath=os.path.dirname(sFileIn)
    if os.path.isabs(sPath) == False:
        sPath=sCurdir + sSlash + sPath
        sFileIn=sCurdir + sSlash + sFileIn

# Split in array 2 (almeno uno ci sarà anche se vuoto)
    sFileExt=os.path.basename(sFileIn)
    aExt=sFileExt.split(".")
    sFile=aExt[0]
    if len(aExt)>1: sExt=aExt[1]

#   if NT_ENV_TEST_SYS == True:
#        print ("TEST TYPES P: " + type(sPath).__name__ + ", F: " + type(sFile).__name__ + ", E: " + type(sExt).__name__)
#        print(sProc + ": " + "File.IN: " + sFileIn)
#        print(sProc + ": " + "Path,File,Ext. P:" + sPath + ", F:" + sFile + ", E:" + sExt)

# LResult
# 0=Ritorno, 1=Dir, 2=File, 3=Ext 4=FileConExt, 5=FileNormalizzato
    lResult=["",sPath,sFile,sExt,sFileExt,sFileIn]
    if NT_ENV_TEST_SYS == True: print (sProc + ": " + str(lResult))
    return lResult

# Tipo di PATH. N=Non Esiste, F=File, D=Dir
def NF_PathType(sFile):
    sResult=""

# Calcolo
    path=Path(sFile)
    if os.path.exists(sFile)==False: sResult="N"
    if path.is_file(): sResult="F"
    if path.is_dir(): sResult="D"

# Ritorno
    return sResult

#  ------------- OS.INTERFACE ---------------------

def NF_IsWindows():
    if  platform=="win32":
        return True
    else:
        return False

#  ------------- DIAGNOTICA E GESTIONE ERRORI ---------------------

# NullTo0/nullToStr
def NF_NullTo0(vValue):
    if vValue==None:
        return 0
    else:
        return int(vValue)

def NF_NullToStr(vValue):
    if vValue==None:
        return ""
    else:
        return str(vValue)

# Range
def NF_Range(vValue, vMin, vMax):
    return (vValue>=vMin) and (vValue<=vMax)

# Errore Ritorno in lResult - DEVE GIA' ESISTERE lResult come dict
def NF_Result(lResult, sProc, sResult):
    lResult=[]
    sReturn=""
    if (sResult != ""):
        lResult.append("Errore in " + sProc + ":" + sResult)
        sReturn=lResult[0]
    return sReturn

# Come NF_Result ma considera lResult già creata come dict e non la cancella solo aggiornando l'item 0
# Ritorna sempre lResult
def NF_Result2(lResult, sProc, sResult):
    sReturn=""
    if (sResult != ""):
        sReturn = sProc + ": Errore " + sResult
        if len(lResult)>0:
            lResult[0]=sReturn
        else:
            lResult=[sReturn]
# Fine
    return lResult

# Ritorno con Errore sProc aggiunto
def NF_ErrorProc(sResult, sProc):
    #print ("NF_ErrorProc: " + str(type(sResult)))
    if (sResult != ""):
        return sProc + ": Errore " + str(sResult)
    else:
        return sResult

# Ritorno stringa Test
def NF_DebugFase(bDebug, sText, sProc):
    if bDebug:
        if (sText == ""): sText="Start"
        print (sProc + ", Fase: " + sText)

# ------------------------------ STRINGHE -------------------------------

# String Test + ", " Append se non è la prima
def NF_StrAppendExt(sSource, sAppend, sDelimiter=","):

    if str(type(sSource)) != "<class 'str'>":
        return sSource
    if sSource == "":
        return sAppend
    else:
        return sSource + sDelimiter + str(sAppend)

# Template String Replace from Dict, using template library
# %Campo
def NF_StrReplaceDict(sTemplate, dictData):
    #print ("TEST NF_StrDictReplace: " + sTemplate +" , " + str(dictData))
    objTemplate=Template(sTemplate)
    return objTemplate.substitute(dictData)

# Conversione da STR a BOOL - La bool() non funziona bene
def NF_StrBool(sText):
    sText=str(sText).upper()
    bResult=iif(sText=="TRUE",True,False)
    return bResult


# Cerca substr i String, -1=Left, 0=Internal, 1=Right
def NF_StrFind(nPos, sString, sFind):
    nResult=-1

# Verifiche
    if sString=="" or sFind=="": return -1
    
# Casi
    nFind=len(sFind)
    if nPos==-1:
        sString2=NF_StrLeft(sString,nFind)
        if sString2==sFind: nResult=1
    if nPos==1:
        sString2=NF_StrRight(sString,nFind)
        if sString2==sFind: nResult=len(sString)-nFind
    elif nPos==0:
        nResult=sString.find(sFind)
        if nResult != -1: nResult=nResult+1
    
# Uscita
    return nResult
    

# convertoto in STr + Trim + UCase +
def NF_StrNorm(sText):
    sText=str(sText)
    return ((sText.lstrip()).rstrip()).upper()

# Strings per lettura
def NF_StrLeft(s, amount):
    return s[:amount]
def NF_StrRight(s, amount):
    return s[-amount:]
def NF_StrMid(s, offset, amount):
    return s[offset:offset+amount]

# Strip Evoluto. X=NoASC, S=NoSpazi
def NF_StrStrip(sText,sType):
    sText=str(sText)
    if sType.find("X") != -1:
        sText = ''.join(cChar for cChar in sText if ( ((ord(cChar)<128) and (ord(cChar)>31))) )
    if sType.find("S") != -1:
        sText = ''.join(cChar for cChar in sText if ( ord(cChar)!=32 )  )
    return sText

# String Test in Boolean
def NF_StrTest(sResult):
    if sResult != "":
        return True
    else:
        return False
    
# Return lResult, 0=Result, 1=StringRead
def NF_StrFileRead(sFile):
    sProc="StrFileRead"
# Apertura + Lettura
    sResult=NF_ErrorProc("Apertura file " + sFile, sProc)
    with open(sFile, "r", encoding=NT_ENV_ENCODING) as txt_file:
        try:
            lines = txt_file.readlines()
        except:
            sResult=NF_ErrorProc("Lettura file " + sFile, sProc)
        sResult=""

# Chiusura
    txt_file.close()
    lResult=[sResult,lines]
    return lResult

# Ritorno stringa Test
def NF_StrTestResult(sResult, sProc):
    if (sResult != ""):
        return "Test " + sProc + ": " + str(sResult)
    else:
        return "Test " + sProc + ": OK"

def NF_IsString(vParam):
    return (type(vParam)==type("x"))

# --------------------------- ARRAY ---------------------------

# Comparazione Array TUPLE
def NF_ArrayCompare(av1, av2):
    sProc="ARR_COMPARE"
    sResult=""
    
# Confronto Tipo
    if not (NF_IsArray(av1) and NF_IsArray(av2)): sResult="Var non di tipo array tutti e 2: " + str(type(av1)) + ", " + str(type(av2))
    
# Confronto Len    
    if sResult=="":
        nLen1=len(av1)
        nLen2=len(av2)
        if nLen1!=nLen2: sResult="Array len diverse, av1: " + str(nLen1) + ", av2: " + str(nLen2)
    
# Confronto elementi
    if sResult=="":
        for nF1 in range(0,nLen1):
            if av1[nF1] != av2[nF1]:
                sResult=NF_StrAppendExt(sResult, "i: " + str(nF1))
        if sResult != "": sResult = "Elementi diversi: " + sResult

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult
    
# ArrayTrim  & CASE
# LR=Trim Space Left/Right, UCZ=UCase, LCase, Capitalize, S=StripSpaces, X=StripNoAsc, F=ForzaStr
def NF_ArrayStrNorm(asArray, sActions):
    nIndex=0
# Setup + Verify
    if asArray==None: return asArray
    nIndex=0
# Ciclo
    for sArray in asArray:
        # Forza Str
        if sActions.find("F")!=-1: sArray=str(sArray)
        if str(type(sArray))=="<class 'str'>":
            #print (str(type(sArray)) + " " + sArray)
        # LTRIM, RTRIM, TRIM
            if sActions.find("L")!=-1: sArray=sArray.lstrip()
            if sActions.find("R")!=-1: sArray=sArray.rstrip()
            if sActions.find("S")!=-1: sArray=NF_StrStrip(sArray,"S")
        # UCASE
            if sActions.find("U")!=-1: sArray=sArray.upper()
            elif sActions.find("C")!=-1: sArray=sArray.lower()
            elif sActions.find("Z")!=-1: sArray=sArray.capitalize()
        # NOASC
            if sActions.find("X")!=-1: sArray=NF_StrStrip(sArray,"X")
        # END + NEXT
        asArray[nIndex]=sArray
        nIndex+=1
# Ritorno
    return asArray

# Ritorna -1 se non esiste, 0=Empty, >0 c'è qualcosa
def NF_ArrayLen(avArray):
    nResult=0
    #print("DictLen.0: " + str(nResult))
    if NF_IsArray(avArray)==False: nResult=-1
    #print("DictLen.1: " + str(nResult))
    if nResult==0: nResult=len(avArray)
    #print("DictLen.2: " + str(nResult))
    return nResult

# Ritorna <0 o posizione in ArrayList
def NF_ArrayFind(avKeys, vKey):
    nResult=0
    #sProc="NF_ArrayFind"

# Caso No Elementi
    #NF_DebugFase(NT_ENV_TEST_SYS, "Type avKeys: " + str(type(avKeys)),sProc)
    if (avKeys==None):
        nResult=-2
    else:
        try:
            nResult=avKeys.index(vKey)
        except:
            nResult=-1
# Fine
    return nResult

# Conversione da lista a tupla per modificarlo
def NF_ArrayT2L(avTuple):
    avList=[]
    for x in avTuple:
        avList.append(x)
    return avList

def NF_IsArray(aParams):
    t=type(aParams)
    return (t==type(list())) or (t==type(tuple()))

# ----------------------------------- DICTIONARY ----------------------------------

# Conversione di tipi in dict
# In: DictParams da verificare, dictConvert Key=Tipo B=Bool, I=Int, N=Float
def NF_DictConvert(dictParams,dictConvert):
    sType=""
    sProc="DictConvert"
# Verifiche
    if (NF_DictLen(dictParams)<1) or (NF_DictLen(dictConvert)<1): return dictParams
# Setup
    avKeys=NF_DictKeys(dictParams)
    avConvert=NF_DictKeys(dictConvert)
# Ciclo Conversione
    for vKey in avKeys:
        if NF_ArrayFind(avConvert,vKey)>=0:
            print(sProc + ": " + str(vKey))
            vValue=dictParams[vKey]
            vValue=str(vValue)
            sType=dictConvert[vKey]
            if (sType=="B"): vValue=NF_StrBool(vValue)
            if (sType=="I"): vValue=int(vValue)
            if (sType=="N"): vValue=float(vValue)
            dictParams[vKey]=vValue
# Ritorno
    return dictParams

# GET ESTESA, con Valore di defaultt
def NF_DictGet(dictParams,sKey,vDefault):
    vResult=dictParams.get(sKey)
    if vResult==None: vResult=vDefault
    return vResult

# Da Dictionary a Stringa
def NF_DictStr(dictParams):
    sResult=""
# Scomposizione    
    if NF_DictLen(dictParams)>0:
        asKeys=NF_DictKeys(dictParams)
        for sKey in asKeys:            
            sResult=NF_StrAppendExt(sResult, str(sKey) + "=" + str(dictParams[sKey]) + "\n")
    else:
        sResult="Dict not valid or Empty"        
# Uscita
    return sResult
    
# FROM KEYS PIU' SEMPLICE. Nuovo Dictionary solo delle key scelte "se esistono"
# VUOTO COMUNQUE SE NESSUNO
def NF_DictFromKeys(dictParams, avKeys):
    dictResult=dict()
    for vKey in avKeys:
        dictResult[vKey]=dictParams[vKey]
    return dictResult

# Ritorna una lista VERA delle Keys di un dictionary perché .keys ritorna una cosa diversa. una view ref.
def NF_DictKeys(dictData):
    asResult=[]
    sProc="NF_DictKeys"
    if (NF_IsDict(dictData)):
        for vKey in dictData.keys():
            asResult.append(vKey)
    else:
        sType=str(type(dictData))
        print("Attenzione, Passata dictData non dict " + sType + ": " + sProc)
# Debug
    #print("NF_DictKeys: " + str(asResult))
    return asResult

# Ritorno -1=NoDict, 0=Empty. Oppure>0
def NF_DictLen(dictParams):
    nResult=0
    #print("DictLen.0: " + str(nResult))
    if NF_IsDict(dictParams)==False: nResult=-1
    #print("DictLen.1: " + str(nResult))
    if nResult==0: nResult=len(dictParams)
    #print("DictLen.2: " + str(nResult))
    return nResult

# Esiste singola key
def NF_DictExistKey(dictData,vKeyFind):
    if (dictData != None):
        for vKey in NF_DictKeys(dictData):
            #Debug
            #print("NF_DictExistKey.Key: " + str(vKey))
# Trovata Key in dictData
            if (vKey==vKeyFind): return True
    else:
# Diagnostica per probabile errore
        print("DictExistKey.dict: NONE")
# Non Trovata Key in dictData
    return False

# Verifica esistenza chiavi in Dictionary
def NF_DictExistKeys(dictData, avKeys):
    sProc="NF_DictExistKeys"
    sResult=""

# Check Dic NotEmptyWithValues
    nResult=NF_DictLen(dictData)
    if (nResult<1): sResult="Dict.Test Exist+Values: " + str(nResult)
    if (sResult==""):
# Keys
        avDataKeys=NF_DictKeys(dictData)
# Verifica Keys
        for vKey in avKeys:
            if NF_ArrayFind(avDataKeys, vKey) < 0:
                sResult=NF_StrAppendExt(sResult, str(vKey))
        if (sResult!=""): sResult="Dict.Test.Keys.Not.Found: " + sResult
# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult

# Return dictionary from Array Header/Data
def NF_DictFromArr(asHeader, avData):
# Input: asHeader(array keys), avData(array valori). i 2 array devono avere stessa lunghezza
# Ritorno:
#   lResult[0]: Diagnostica di ritorno. ""=NoError,
#   lResult[1]: Dict,
#   Altri: 2=LenHdr, 3=LenData, 4=TypeHDR(se non Array), 5=TypeData(se non Array)
    sProc="NF_DictFromArr"
    sResult=""
    dictResult={}
    
# Verifica Componenti
    lHType=0
    lHData=0
    bVerify = NF_IsArray(asHeader) and NF_IsArray(avData)    
    if bVerify:
        lHType=len(asHeader)
        lHData=len(avData)
        bVerify = (lHType == lHData)
        sResult=iif(bVerify, "", "lunghezze diverse: H=" + str(lHType) + ", D=" + str(lHData))
    else:
        sResult="Tipi diversi header/data, non array"

# Ritorno componenti operazioni
    lResult=[sResult,dictResult,len(asHeader),lHType,lHData,str(type(asHeader)), str(type(avData))]

# Esecuzione
    if bVerify:
        nIndex=0
        for sID in asHeader:
            vDato=avData[nIndex]
            dictResult.update({sID: vDato})
            nIndex=nIndex+1
        #print ("TEST dictFromArray: " + str(dictResult))        
        lResult=NF_Result2(lResult,sProc,sResult)
    else:
        lResult=NF_Result2(lResult,sProc,sResult)

# Merge 2 Dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge(dictSource, dictAdd):
    
# Copia
    dictEnd=dictSource.copy()
# Per ogni elemento in dictAdd
    for vKey in NF_DictKeys(dictAdd)
    # Attribuisce
        dictEnd[vKey]=dictAdd[vKey]

# Uscita
    return dictEnd

# Merge 2 Dict(2) dict di dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge2(dictSource, dictAdd):

# Copia
    dictEnd=dictSource.copy()

# Per ogni dict dentro dictAdd
    for vKey in NF_DictKeys(dictAdd)
        dictAdd2=dictAdd[vKey]
    # Cerca se esiste o attribuisce dictAdd
        if NF_DictExist(dictSource,vKey):
            dictSource2=dictSource[vKey]
        else:
            dictSource2=dictAdd
    # Merge
        dictMerge=NF_DictMerge(dictSource2, dictAdd2)
        dictEnd[vKey]=dictMerge
        
# Uscita
    return dictEnd
    
# Uscita
    lResult[1]=dictResult
    return lResult

def NF_IsDict(dictParams):
    return (type(dictParams)==type(dict()))

# ------------------------------- TEMPO E DATE -------------------------

# B=Base(def), N=Normal, X=Esteso
def NF_TS_ToDict(dtDate,sType="B"):

# Setup
    tt=dtDate.timetuple    
    dictTime=dict()
    nID=0
    dictID={0:"Y", 1:"M", 2:"D", 3:"HH", 4:"MM", 5:"SS", 6:"DW", 7:"DY", 8:"DY", 9:"IY", 10:"YW", 11:"YD"}
    
# Scomposizione
# Assegna e incrementa Indice
    for nValue in tt:
    # Conversione nID->sID
        sID=dictID[nValue]
        dictTime[sID]=nValue
        nID=nID+1

    # Aggiunge IC (Tipo N/X) 
    if (sType!="B") :
        ic=dtDate.isocalendar()
        for nValue in ic:
            sID=dictID[nValue]
            dictTime[sID]=nValue
            nID=nID+1
                   
# Ritorno
    return dictTime
       
# TIMESTIME: ToStr
# L=Light, P(o altro)=Python
# L=YYYYMMDD.HHMMSS, P=YYYYMMDD.HHMMSS.MILLISEC
def NF_TS_ToStr(sType="L"):
    sResult=""

# TimeStamp
    now=datetime.today()  
# Conversione
    if sType=="X":
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now) + "." + str(now.microsecond)
    else:
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now)
# Uscita
    return sResult

# TIMESTIME: ToStr. Ritorna lresult, 0=sResult, 1=Date, 2=Time, 3=Msec
# sDateTime: DATE.TIME[.MSEC]
def NF_TS_FromStr(sDateTime):
    sResult=""
    sProc="TS_FromStr"
    nMsec=0
    
# Split
    if sDateTime=="": sResult="NoDateTime"
    if (sResult==""):
        asDate=sDateTime.split(NT_ENV_DATE_DIV)
        asDate=NF_ArrayStrNorm(asDate,"SLR")
        nLen=len(asDate)
        if nLen<2: sResult="NoValid sep"
    if (sResult==""):
        # Estrae
        sDate=asDate[0]
        sTime=asDate[1]
        if nLen==3: nMsec=int(asDate[3])
        # Converte da Str a dt/tm
        dtDate=NF_DateYYYYMMDD_fStr(sDate)
        tmTime=NF_TimeHHMMSS_fStr(sTime)
    
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    lResult=[sResult, dtDate, tmTime, nMsec]
    return lResult

# Ritorna microsecondi
def NF_DateMsec(dtDate):
    return int(dtDate.strftime("%f"))

# Da Data a AAAAAMMDD Str
def NF_DateStrYYYYMMDD(dtDate):
    sResult=str(dtDate)
    #print("D1:" + sResult)
    sResult=sResult.replace("-","")
    #print("D2:" + sResult)
    sResult=NF_StrLeft(sResult,8)
    #print("D3:" + sResult)
    return sResult

# Da YYYYMMDDStr a Data
def NF_DateYYYYMMDD_fStr(sDate):
    nYear=int(NF_StrLeft(sDate,4))
    nMonth=int(NF_StrMid(sDate,6,2))
    nDay=int(NF_StrMid(sDate,7,2))
    dtDate=datetime(nYear,nMonth,nDay)
    return dtDate

# Da HHMMSSStr a Time
def NF_TimeHHMMSS_fStr(sTime):
    tmTime=datetime.strptime(sTime, '%H%M%S')
    return tmTime

# Da Time a AAAAAMMDD Str
def NF_TimeStrHHMMSS(tmTime):
    sResult=str(tmTime)
    sResult=NF_StrMid(sResult,11,8)
    sResult=sResult.replace(":","")
    sResult=NF_StrLeft(sResult,6)
    return sResult

# Attesa
def NF_Wait(nSecondi):   
    time.sleep(nSecondi)            

# ----------------------- CLASSI ---------------------------
#
# ntJobs System Class APP + LOG
class NC_Sys:
# ID  APP  
    sID=""
# File di LOG Globale    
    sLogFile=""
    sLogTag=""
    sLogToFile=False
    sLogProc=""
    
# Init
    def __init__(self,sID_set):        
        self.sID=sID_set
        sTemp="Log\\" + self.sID + ".log"
        lResult=NF_PathNormal(sTemp)
        self.sLogFile=lResult[5]
        locale.setlocale(locale.LC_ALL, "it_IT.UTF8")
        
    def LogAttr(self, sAttr, vValue):
        if sAttr=="P": self.sLogProc=vValue
        elif sAttr=="T": self.sLogTag=vValue
        elif sAttr=="F": self.sLogToFile=vValue
        
    def Log(self, sLog):
        sText=f"{self.sID}.{self.sLogProc}.{self.sLogTag}"
        sText=sText + NF_TS_ToStr() + ": " + sLog
        if self.sLogFile!="":
            NF_FileFromStr(sLog, self.sLogFile,"a")
        else:
            print(sLog)
