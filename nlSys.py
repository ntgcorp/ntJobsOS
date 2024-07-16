# ntJobsPy Framework
# CORE LIBRARY - DataTypes - OS - Basic Files - Process - Date
# --------------------------------------------------------------------
# Lib per gestione path e files
from pathlib import Path
# For NF_File*
import os
# For NF_FileDelete (rmdir)
import shutil
# For NF_PathFind + NF_FileCopy
import glob
# For Exec
import subprocess
# Per Ambiente
from sys import platform
# Lib per gestione Replace
from string import Template
# Per Wait e Date
import time
from datetime import datetime
# Per File Temporanei
import tempfile
# Per Argomenti (NF_Args)
import sys,argparse

# Setup: TEST o NO
NT_ENV_TEST_SYS=True
# ENCODING
NT_ENV_ENCODING="utf-8"
# YYYYMMDD.HHMMSS.MSEC
NT_ENV_DATE_DIV="."

# ----------------------- DA ARG A DICT ---------------------------
# Ritorna Array
# Optional Arguments. Array "-argLight", "-arg", "help", required_true, default
# Result lResult. 0=sResult, 1=dictArgs o vuoto dict
def NF_Args(axArgs):
    sProc="NF_Args"
    bParse=False
    sResult=""
    dictArgs={}

# Facolativi
    NF_DebugFase(True,"Parametri per parsing Argomnenti:"  + str(axArgs), sProc)
    for xArg in axArgs:
        print("Argument " + xArg[0] + ": " + len(xArg))
        if len(xArg)==3:
# Caso 1: Nome parametro, help, required, default
            parser.add_argument(xArg[0],help=xArg[1],required=xArg[2],default=xArg[3])
            bParse=True
        elif len(xArg)==5:
        # Caso 2: light, No-à-me parametro, help, required, default
            parser.add_argument(xArg[0],xArg[1],help=xArg[2],required=xArg[3],default=xArg[4])
            bParse=True
        else:
            pass

# Converte in Array
    NF_DebugFase(True,"Parsing Argomenti " + str(bParse), sProc)

    if bParse==True:
        parser=argparse.ArgumentParser()
        dictArgs=vars(parser.parse_args())
    else:
        #   lResult[0]: Diagnostica di ritorno. ""=NoError,
        #   lResult[1]: Dict,
        #   Altri: 2=LenHdr, 3=LenData, 4=TypeHDR(se non Array), 5=TypeData(se non Array)
        lResult=NF_DictFromArr([],sys.argv[1:])
        sResult=lResult[0]
        if sResult=="":
            dictArgs=lResult[1]

# Ritorno
#    NF_DebugFase(True,"End",sProc)
    lResult=[sResult, dictArgs]
    return lResult

# ----------------------- FUNZIONI DI BASE ---------------------------

# IIF che in python non c'è
def iif (bExpr, trueResult, falseResult):
    if bExpr: return trueResult
    else: return falseResult

# Execute External program
def NF_Exec(**kwargs):
    sProc="NF_Exec"
    sResult=""

    # Iterating over the Python kwargs dictionary
    for key, value in kwargs.items():
        if key=="cmd": sExec_cmd=value
        if key=="args": sExec_args=value

    # Test CMD
        if sExec_cmd=="":
            sResult="command line empty"

    # Esecuzione
    if sResult=="":
        try:
            retcode=subprocess.call(sExec_cmd,sExec_args,capture_output=True)
            if retcode<0: sResult="Errore in esecuzione: " + str(retcode)
        except OSError as e:
            sResult="Errore Esecuzione " + str(e)

    # Ritorno
    return NF_ErrorProc(sResult, sProc)

# Return String on Condition
def NF_Assert(bCondition=False,sResultTrue="",sResultFalse="",sProc=""):
    sPrefix=iif(sProc!="", sProc+": ", "")
    if bCondition:
        return sPrefix + sResultTrue
    else:
        return sPrefix + sResultFalse

# Return String on Condition
def NF_AssertPrint(bCondition=False,sResultTrue="",sResultFalse="",sProc=""):
    sAssert=NF_Assert(bCondition,sResultTrue,sResultFalse,sProc)
    if sAssert != "": print(sAssert)
    return sAssert

# Attesa
def NF_Wait(nSecondi):
    time.sleep(nSecondi)

# ---------------------- FILES & PATH  -----------------------

# Ritorna Errore Standard NF_FileExist o "" come stringa.
def NF_FileExistErr(sFilename):
    sResult=iif(NF_FileExist(sFilename),"","Non Esistenza file " + sFilename)
    return sResult

# Alias File Exist
def NF_FileExist(sFilename):
    return os.path.exists(sFilename)

# Ritorna doppio risultato.
# - sResult. "" o Errore
# - sFilename originale o rimappato con currentdirscript se esiste
def NF_FileExistMap(sFilename):
    sProc="File.Exist.Map"
    sResult=""

    if NF_FileExist(sFilename):
        sFileNew=os.path.abspath(sFilename)
    else:
        sFileNew=NF_PathAddSlash(os.getcwd()) + sFilename
        sResult=NF_FileExistErr(sFileNew)
        if sResult=="":
            print("File Rimappato in " + sFileNew)

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult,sFileNew

# String o Binary to File o viceversa
# sResult=Tipo di errore
def NF_FileWrite(sFilename, sText, sAttr):
    sResult=""
    sProc="File.Write"
    bOpen=False

# Verifica parametri
    if NF_ArrayFind(("w","a"), sAttr)<0: sResult="parametro: " + sAttr

# Apertura File
    lResult=NF_FileOpen(sFilename,sAttr)
    sResult=lResult[0]

# Write string to file
    if sResult=="":
        hFile=lResult[1]
        bOpen=True
        try:
            hFile.write(sText)
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + "scrittura su file aperto " + sAttr + ", " + sFilename

# Close file if Open
        if bOpen: hFile.close()

# Uscita
    return NF_ErrorProc(sResult,sProc)

# String o Binary to File o viceversa
# sResult=Tipo di errore
# Ritorna lResult. 0=sResult, 1=Text
def NF_FileRead(sText, sFilename, sAttr):
    sResult=""
    sProc="File.Read"
    bOpen=False

# Verifica parametri
    if NF_ArrayFind(("r", "rb"),sAttr)<0: sResult="parametro: " + sAttr

# Open Text File
    if (sResult==""):
        try:
            hFile = open(sFilename, mode=sAttr, encoding=NT_ENV_ENCODING)
        except:
            sResult="apertura file con attributo " + sAttr + ", " + sFilename
# Read string from file
        bOpen=True
        if sResult=="":
            try:
                hFile.read(sText)
            except:
                sResult="lettura file con attributo " + sAttr + ", " + sFilename
# Close file
        if bOpen: hFile.close()
        lResult=NF_Result(sResult,sProc,sText)

# Uscita
    return lResult

# Path.Rename
# F=File, D=Directory, T=Directory e Contenuto
def	NF_FileDelete(sFile,sType="FN"):
    sProc="NF_FileDelete"
    sResult=""

# Cancellazione
    try:
        if (sType=="F") :
            os.remove(sFile)
        elif (sType=="D"):
            os.rmdir(sFile)
        elif (sType=="T"):
            shutil.rmtree(sFile)
        else:
            sResult="Tipo non supportato in FileDelete " + sType
    except Exception as e:
        sResult=getattr(e, 'message', repr(e)) + "cancellazione file " + sFilename

# Uscita
    return NF_ErrorProc(sResult,sProc)

# Open File
# Attr: w=Write, a=Append, r=readonly, x=Create if not exist
# Return lResult. 0=sResult, 1=Handle/None
def NF_FileOpen(sFilename,sAttr):
    sResult=""
    sProc="File.Open"

# Apertura
    try:
        hFile = open(sFilename, mode=sAttr, encoding=NT_ENV_ENCODING)
    except Exception as e:
        sResult=getattr(e, 'message', repr(e)) + "Apertura file modo " + sAttr + ", " + sFilename
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    if sResult=="":
        lResult=[sResult,hFile]
    else:
        lResult=[sResult,None]
# Ritorno
    return lResult

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
    return NF_ErrorProc(sResult,sProc)

# Path Temporaneo. Parametri: sPathBase, sPrefix, Type="FD"
# Ritorno: lResult 0=sResult, 1=PathCreato
def NF_PathTemp(sPathBase="", sPrefix="", sType="F"):
    sProc="NF_PathTemp"
    sResult=""
    sPath=""

# Test
    if (sType!="F") and (sType!="D"): return NF_ErrorProc("Tipo invalido " + sType,sProc)

# Creazione
    if sType=="D":
        try:
            sPath=tempfile.mkdtemp(prefix=sPrefix, dir=sPathBase)
        except:
            sResult="Creazione directory da " + sPathBase
    elif sType=="F":
        try:
            outfile=tempfile.NamedTemporaryFile(delete=False, dir='/tmp/myfolder')
            sPath=outfile.name
            outfile.close
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + "Creazione Temp Path tipo " + sType

# Uscita
    return [NF_ErrorProc(sResult,sProc),sPath]

# Path.Copy/XCopy
# F=Singolo File P=Path, (F=File), D=Dir
def NF_PathCopy(sPathIn, sPathOut, sType="F"):
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
    return NF_ErrorProc(sResult,sProc)

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
    lResult=[NF_ErrorProc(sResult,sProc), asPath]
    return lResult

def NF_PathScript(sType):
    sResult=""

    if sType=="SCRIPT":
        sResult=__file__
    elif sType=="ID.NE":
        sResult=os.path.splitext(os.path.basename(__file__))[0]
    elif sType=="PATH":
        sResult=NF_PathAddSlash(os.path.dirname(os.path.abspath(__file__)))
    else:
        sResult="NO TYPE"
# Ritorno
    return sResult

# Path Rimappato con Dir Corrente
def NF_PathCurDir(*args):
    sResult=""
    sCurDir=os.getcwd()
    sPath=""

# Path da Agganciare
    if len(args)>0: sPath=str(args[0])

# Ritorno
    sResult=NF_PathAddSlash(sCurDir) + sPath
    return sResult

# Add Slash
def NF_PathAddSlash(sPath):

# Slash per OS
    sSlash=iif(NF_IsWindows(),"\\","/")
# Check Add
    bAdd=NF_StrRight(sPath,1) != sSlash
# Ritorno
    sResult=sPath+iif(bAdd,sSlash,"")
    return sResult

# PathMake File e Cartella. Non aggiunge "\" alla fine
def NF_PathMake(sPath, sFile, sExt):
    sResult=""
# Setup
    sResult=sPath
# Aggiunge File, prima eventuale slash
    if sFile != "": sResult = NF_PathAddSlash(sResult) + sFile
# Aggiunge Ext
    if sExt != "": sResult = sResult + "." + sExt
# Ritorno
    return sResult

# Split Path in Path,File,Ext
def NF_PathScompose(sFilePath):
    sPath = NF_PathAddSlash(os.path.dirname(sFilePath))
    sExt = os.path.splitext(sFilePath)[1][1:]
    sFileName=os.path.basename(sFilePath)
    sName= sFileName.rsplit('.', 1)[0]
    #print("Path: " + sPath + ", Name: " + sName + ", Ext: " + sExt)
# Ritorno
    return sPath,sName,sExt

# Normalizza Path con verifiche ed estraendo componenti
# Ritorno lResult
# 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
# Result=Eventuale errore
def NF_PathNormal(sFileIn):
    sProc="NF_PathNormal"
    sPath=""
    sExt=""
    sFile=""
    sFileExt=""
    aExt=[""]
    lResult=[]
    sResult=""

# Null
    if (sFileIn==""):
        sResult="No Input file"
        return NF_Result(sResult, sProc, [])

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

# Test code
#   if NT_ENV_TEST_SYS == True:
#        print ("TEST TYPES P: " + type(sPath).__name__ + ", F: " + type(sFile).__name__ + ", E: " + type(sExt).__name__)
#        print(sProc + ": " + "File.IN: " + sFileIn)
#        print(sProc + ": " + "Path,File,Ext. P:" + sPath + ", F:" + sFile + ", E:" + sExt)

# LResult
# 0=Ritorno, 1=Dir, 2=File, 3=Ext 4=FileConExt, 5=FileNormalizzato
    lResult=["",sPath,sFile,sExt,sFileExt,sFileIn]
    #if NT_ENV_TEST_SYS == True: print (sProc + ": " + str(lResult))
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
def NF_TS_ToStr(sType="L", sOld=""):
    sResult=""
    sProc="NF_TS_ToStr"

# TimeStamp
    now=datetime.today()
    #print(sProc, sResult, sOld, sType)

# Conversione
    if sType=="X":
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now) + "." + str(now.microsecond)
    else:
        sResult=NF_DateStrYYYYMMDD(now) + "." + NF_TimeStrHHMMSS(now)

# Loop deve essere diverso dal vecchio se specificato
    while sResult==sOld:
        sResult=NF_TS_ToStr(sType, sOld)

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
    lResult=[NF_ErrorProc(sResult,sProc), dtDate, tmTime, nMsec]
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

#  ------------- OS.INTERFACE ---------------------

def NF_IsWindows():
    if  platform=="win32":
        return True
    else:
        return False

def NF_IsLinux():
    if  platform=="linux":
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

# TypeCasting
def NF_TypeCast(vDato,sType=None):
# Selezione
    if sType=="T":
        vDato=str(vDato)
    elif sType=="B":
        vDato=bool(vDato)
    elif sType=="N":
        vDato=float(vDato)
    elif sType=="I":
        vDato=int(vDato)
    else:
        pass
# Uscita
    return vDato

# Crea lResult con Errore e Result per return diretto - NON DEVE ESISTERE LRESULT
def NF_Result(sResult, sProc, vResult):
    sResult=NF_ErrorProc(sResult, sProc)
    lResult=[sResult,vResult]
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

# Join text con parametri vari
# delim=Delimitoatore (o ","). prefix=Prefisso prima di ogni stringa, postfix=dopo ogni stringa, node=NoDelimitatorOnE. nofixe=no suffix/prefix on empty
# fast=True, usa la join python
def NF_StrJoin(**kwargs):
    sResult=""
    sPrefix=""
    sSuffix=""
    sDelim=","
    vResult=[]
    avResult=[]
    bNofixe=False
    bNode=False

# Parametri
    for key,value in kwargs.items():
        if key=="delim":
            sDelim=value
        elif key=="start":
            sPrefix=value
        elif key=="end":
            sSuffix=value
        elif key=="node":
            bNode=bool(value)
        elif key=="nofixe":
            bNofixe=bool(value)
        elif key=="text":
            avResult=value
        elif key=="fast":
            bFast=bool(value)

# Ciclo Standard
    if bFast:
        sResult=sDelim.join(avResult)
    else:
        for vResult in avResult:
            vResult=str(vResult)
            vResult=iif(bNofixe,"",sPrefix) + vResult + iif(bNofixe,"",sSuffix)
            if sResult != "": sResult = sResult + iif(bNode, "", sDelim)
            sResult=sResult + str(vResult)

# Ritorno
    return sResult

# Da Oggetto a Stringa
def NF_StrObj(objX):
    sResult=""
    sProc="NF_ObjStr"
    nIndex=0

# Verifica Tipo Dict
    if type(objX) != dict:
        sResult="Not dict"
    elif  NF_DictLen(objX)<1:
        sResult="Dict Empty"
    else:
# Inizio: Ciclo Key->Value
        asKeys=NF_DictKeys(objX)
        print("Keys: " + str(asKeys))
        for sKey in asKeys:
            sKeyType=type(sKey)
            if sKeyType != str:
                sResult="Key invalid " + str(nIndex) + ": " + str(sKeyType)
            else:
            # Key
                print(sProc + ": NF_DictExistKey.Key: " + str(nIndex) + ", " + sKey )
                sValue=""
                vValue=None
                if sKey != "": vValue=objX[sKey]
            # Value: Lista
                if type(vValue)==list:
                    sValue=NF_StrObj(vValue)
            # Value: Dictionary
                elif type(vValue)==dict:
                    sValue=NF_StrObj(vValue)
            # Value: Altri casi
                else:
                    sValue=sKey + "=" + str(vValue)
        # Append Key+Value
            sResult=NF_StrAppendExt(sResult, sValue)

# Uscita (così è giusto)
    return sResult

# Strip Evoluto. X=NoASC, S=NoSpazi
def NF_StrStrip(sText,sType):
    sText=str(sText)
    if sType.find("X") != -1:
        sText = ''.join(cChar for cChar in sText if ( ((ord(cChar)<128) and (ord(cChar)>31))) )
    if sType.find("S") != -1:
        sText = ''.join(cChar for cChar in sText if ( ord(cChar)!=32 )  )
    return sText

def NF_StrSplitKeys(sKeys, sDelimiter=","):
    asFieldsCSV=sKeys.split(sDelimiter)
    asFieldsCSV=NF_ArrayStrNorm(asFieldsCSV,"LRUS")
    return asFieldsCSV

# Return lResult, 0=Result, 1=StringRead
def NF_StrFileRead(sFile):
    sProc="StrFileRead"
    sResult=""

# Apertura + Lettura
    sResult=NF_ErrorProc("Apertura file " + sFile, sProc)
    with open(sFile, "r", encoding=NT_ENV_ENCODING) as txt_file:
        try:
            lines = txt_file.readlines()
        except:
            sResult="Lettura file " + sFile

# Chiusura
    txt_file.close()
    return NF_Result(sResult,sProc,lines)

# Ritorno stringa Test
def NF_StrTestResult(sResult, sProc):
    if (sResult != ""):
        return "Test " + sProc + ": " + str(sResult)
    else:
        return "Test " + sProc + ": OK"

# Test in serie con stringa di ritorno. Nulla tutto ok
# 0=Test, 1=StringaPerErrore, 2=FacoltativoIdTest
def NF_StrTests(avTests):
    sResult=""
# Ciclo
    for vTest in avTests:
        nLen=len(vTest)
        if nLen>1:
            bResult=vTest[0]
            sErrorText=vTest[1]
            sTestID=iif(nLen>2,vTest[2]+": ","")
            if bResult==True: sResult=NF_StrAppendExt(sResult, sTestID + sErrorText)
# Uscita
    return sResult

# --------------------------- ARRAY ---------------------------

# Array Append (somma di due Array MONODIMENSIONALI. Ritorna av1+av2
def NF_ArrayAppend(av1, av2):
# Len to Start
    nLen_av1=len(av1)-1
# Append
    for row in av2:
        nLen_av1=nLen_av1+1
        av1[nLen_av1]=row
# Ritorno
    return av1

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
    return NF_ErrorProc(sResult, sProc)

# ArrayCountValues
# Ritorna Array dove ci sono chiavi duplicate
# Ritorna lResult 0=Status, 1=Dict con VALORE=CONTATORE (senza doppi)
# DA VERIFICARE
def NF_ArrayCountValues(avArray):
    sProc="ArrayCountValues"
    sResult=""
    dictCount={}

    # Verifica Array
    if NF_IsArray(avArray)<0: sResult="Array Empty"

    # Ciclo di conteggio
    if sResult=="":

        # Ciclo per tutti i VALORI (DOPPI E NON DOPPI)
        for vValue in avArray:
        # Verifica se esiste gia' - Incrementa INDICE solo SE NON ESISTE
            if NF_DictExistKey(dictCount, vValue) == False:
        # Ricerca quanti valori ce ne sono e lo aggiunge a dictCount
                nCount=NF_ArrayCountValue(avArray, vValue)
                dictCount.append(vValue,nCount)
    # Uscita
    return NF_Result(NF_ErrorProc(sResult), sProc, dictCount)

# Conta Occorrenze di un Valore in Array
# DA VERIFICARE
# Parametri:
#   avArray=Da Controllare
#   vValue=Da cercare
#   sMode ""=Normale, C=StringWithoutCase, L.PathLike=Cerca con PathLike (DA IMPLEMENTARE ALLA PRIMA OCCASIONE)
# Ritorno:
#   nResult -1,0 o Numero Occorrenze
def NF_ArrayCountValue(avArray, vValue, sMode=""):
    nResult=0

# Verrà usata
    sMode=""

# Ciclo di Conteggio
    nLen=NF_ArrayLen(avArray)

# Solo se Len>0 altrimenti Count=Len
    if nLen>0:
        for nF1 in range(0, nLen):
            if vValue==avArray(nF1): nResult=nResult+1
    else:
        nResult=nLen

# Uscita
    return nResult

# Rimuove Elementi da Array, Restituendo nuovo Array. avRemove contiene indici numerici nel range
# Ritorna lResult 0=Status, 1=Array
def NF_ArrayRemoveRows(avArray, avRemove):
    sProc="ArrayRemoveRows"
    avRemove=[]
    avArrayOut=[]

# Verifica Array
    nLenInput=NF_ArrayLen(avArray)
    if (nLenInput<1):
        sResult="Array Error Input"
    else:
        nLenRemove=NF_ArrayLen(avRemove)
        if (nLenRemove<1): sResult="Array Error ToRemove"

# Ciclo costruzione nuovo Array
    if sResult=="":
        for nF1 in range(0, nLenRemove-1):
            if NF_ArrayFind(avRemove,nF1) == False:
                avArrayOut.append(avArray[nF1])

# Ritorno
    return NF_Result(sResult,sProc,avArrayOut)

# ArrayTrim  & CASE
# LR=Trim Space Left/Right, U=UCase, LCase, Capitalize, S=StripSpaces, X=StripNoAsc, F=ForzaStr
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

# Caso Array problema
    if NF_ArrayLen(avKeys)==-1: return -1

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

# Array Sort with checks
# Parameters:
#	avArray (array_to_sort)
#   sMode=""/"A"= Ascendent, "D"=Discendent
# Return
# 	lResult. 0=Status= 1=New Array
def	NF_ArraySort(avArray, sMode="A"):
    sResult=""
    sProc="NF_ArraySort"
    avResult=[]

# Check
    if NF_IsArray(avArray)==False: sResult="Not Array"
    if sMode=="A" or sMode=="":
        sMode=""
        bReverse=False
    elif sMode=="D":
        bReverse=True
    else:
        sResult="Mode invalid " + str(sMode)

# Sort
    if sResult=="":
        avResult=sorted(avArray,reverse=bReverse)
# Return
    return NF_Result(sResult,sProc,avResult)

# Param is Array
def NF_IsArray(aParams):
    t=type(aParams)
    return (t==type(list())) or (t==type(tuple()))

# True=Dictionary
def NF_IsDict(dictParams):
    return (type(dictParams)==type(dict()))

def NF_IsString(vParam):
    return (type(vParam)==type("x"))

# ----------------------------------- DICTIONARY ----------------------------------

# Conversione di tipi in dict
# In: DictParams da verificare, dictConvert Key=Tipo B=Bool, I=Int, N=Float
def NF_DictConvert(dictParams,dictConvert):
    sType=""
    sProc="DictConvert"
# Verifiche
    if (NF_DictLen(dictParams)<1) or (NF_DictLen(dictConvert)<1): return dictParams
# Setup
    lResult=NF_DictKeys(dictParams)
    avKeys=iif(lResult[0],lResult[1],list())
    lResult=NF_DictKeys(dictConvert)
    avConvert=iif(lResult[0],lResult[1],list())
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
def NF_DictGet(dictParams,sKey,vDefault=""):
    vResult=dictParams.get(sKey)
    if vResult==None: vResult=vDefault
    return vResult

# FROM KEYS PIU' SEMPLICE. Nuovo Dictionary solo delle key scelte "se esistono"
# VUOTO COMUNQUE SE NESSUNO
def NF_DictFromKeys(dictParams, avKeys):
    dictResult=dict()
    for vKey in avKeys:
        dictResult[vKey]=dictParams[vKey]
    return dictResult

# Ritorna una lista VERA delle Keys di un dictionary perché .keys ritorna una cosa diversa. una view ref.
# Ritorna lResult 0=Status, 1=Array
def NF_DictKeys(dictData):
    avResult=[]
    sResult=""
    sProc="NF_DictKeys"

# Ciclo
    if (NF_IsDict(dictData)):
        for vKey in dictData.keys():
            avResult.append(vKey)
    else:
        sResult="No dict " + str(type(dictData))

# Debug
    #print("NF_DictKeys: " + str(asResult))
# Ritorno
    return NF_Result(sResult,sProc,avResult)

# Ritorna una lista VERA dei valori di un dictionary perché .values ritorna una cosa diversa. una view ref.
# Ritorna lResult 0=Status, 1=Array Valori
def NF_DictValues(dictData):
    avResult=[]
    sProc="NF_DictValues"
    if (NF_IsDict(dictData)):
        for vKey in dictData.keys():
            avResult.append(dictData[vKey])
    else:
        sResult="No dict " + str(type(dictData)) + ": " + sProc

# Debug
    #print("NF_DictValues: " + str(asResult))
    return NF_Result(sResult,sProc,avResult)

# Ritorno -1=NoDict, 0=Empty. Oppure>0
def NF_DictLen(dictParams):
    nResult=0
    #print("DictLen.0: " + str(nResult))
    if NF_IsDict(dictParams)==False: nResult=-1
    #print("DictLen.1: " + str(nResult))
    if nResult==0: nResult=len(dictParams)
    #print("DictLen.2: " + str(nResult))
    return nResult

# Dictionary. Esiste singola key
# Ritorno. True=Esiste, False=No
def NF_DictExistKey(dictData,vKeyFind):
    lResult=NF_DictKeys(dictData)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
            #Debug
            #print("NF_DictExistKey.Key: " + str(vKey))
# Trovata Key in dictData
            if (vKey==vKeyFind): return True
    else:
# Diagnostica per probabile errore
        print("DictExistKey.dict: NONE")
# Non Trovata Key in dictData
    return False

# Dictionary. Esiste singolo Valore in Dictionary
def NF_DictExistValue(dictData,vValueFind):
    lResult=NF_DictKeys(dictData)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
# Trovato Value in dictData
            if (dictData[vKey]==vValueFind): return True
    else:
# Diagnostica per probabile errore
        print("DictExistKey.dict: NONE")
# Non Trovata Key in dictData
    return False

# Verifica esistenza Keys in Dictionary
def NF_DictExistKeys(dictData, avKeys):
    sProc="NF_DictExistKeys"
    sResult=""

# Check Dic NotEmptyWithValues and avKeys not empty
    nResult=NF_DictLen(dictData)
    if (nResult<1):
        sResult="Dict.Test Exist+Values: " + str(nResult)
    if (NF_ArrayLen(avKeys)<1):
        sResult="Array Keys to find empty"
# Verifica Keys
    if (sResult==""):
        lResult=NF_DictKeys(dictData)
        avKeys
        sResult=lResult[0]
        if sResult=="":
            for vKey in avKeys:
                if NF_ArrayFind(avDataKeys, vKey) < 0:
                    sResult=NF_StrAppendExt(sResult, str(vKey))
            if (sResult != ""): sResult="Dict.Test.Keys.Not.Found: " + sResult

# Ritorno
    return NF_ErrorProc(sResult, sProc)

# Return dictionary from Array Header/Data
def NF_DictFromArr(asHeader, avData):
# Input: asHeader(array keys), avData(array valori).
# Se asHeader=[], allora viene riempito di numeri pari a avData oppure i 2 array devono avere stessa lunghezza
# Ritorno:
#   lResult[0]: Diagnostica di ritorno. ""=NoError,
#   lResult[1]: Dict,
#   Altri: 2=LenHdr, 3=LenData, 4=TypeHDR(se non Array), 5=TypeData(se non Array)
    sProc="NF_DictFromArr"
    sResult=""
    dictResult={}

# Verifica Componenti
    lHType=len(asHeader)
    lHData=len(avData)
    bVerify = NF_IsArray(asHeader) and NF_IsArray(avData)

# Caso Header non passato, riempito di numeri 0..N
    if bVerify and lHType==0:
        asHeader=list(range(0,lHData))

# Verifica lunghezza uguale (salvo zero allora lista 0..n
    if bVerify:
        bVerify = (lHType != lHData)
        sResult=iif(bVerify, "", "lunghezze diverse: H=" + str(lHType) + ", D=" + str(lHData))
    else:
        sResult="Tipi diversi header/data, non array"

# Esecuzione
    if sResult=="":
        nIndex=0
        for sID in asHeader:
            vDato=avData[nIndex]
            dictResult.update({sID: vDato})
            nIndex=nIndex+1

# Ritorno
    sResult=NF_ErrorProc(sResult,sProc)
    lResult=[sResult,dictResult,len(asHeader),lHType,lHData,str(type(asHeader)), str(type(avData))]
    return lResult

# Get Param
# ---------------------------------------------------------------------
def NF_DictGetParam(dictParam, sKey, sError="", sType=None):
    sProc="DICT.GET.PARAM"
    sResult=""
    vDato=None

# Debug
#   print(sProc + ".DICT: " + str(dictParam))

# Estrazione
    if NF_DictExistKey(dictParam,sKey)==False:
        sResult=sError
        vDato=None
    else:
        vDato=dictParam[sKey]

# Tipizzazione
    if sType != None: vDato=NF_TypeCast(vDato,sType)

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult,vDato

# Merge 2 Dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge(dictSource, dictAdd):

# Copia
    dictEnd=dictSource.copy()

# Per ogni elemento in dictAdd
    lResult=NF_DictKeys(dictAdd)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
        # Aggiunge elementi secondo array
            dictEnd[vKey]=dictAdd[vKey]

# Uscita
    return dictEnd

# Merge 2 Dict(2) dict di dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge2(dictSource, dictAdd):

# Copia
    dictEnd=dictSource.copy()

# Per ogni dict dentro dictAdd
    lResult=NF_DictKeys(dictAdd)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
            dictAdd2=dictAdd[vKey]
    # Cerca se esiste o attribuisce dictAdd
            if NF_DictExistKey(dictSource,vKey):
                dictSource2=dictSource[vKey]
            else:
                dictSource2=dictAdd
    # Merge
            dictMerge=NF_DictMerge(dictSource2, dictAdd2)
            dictEnd[vKey]=dictMerge

# Uscita
    return dictEnd

# Sort Dictionary from Keys/Values
# lResult 0=Status, 1=DictResult
# Parametri:
# 	dictParams (Input), sMode (K o "": Keys, "V"=Values), "KR"=Key/Reverse, "VA"=Value/Reverse
# Result: lResult (0=Status, 1=NewDictionaryResultSorted)
# DA VERIFICARE
# -------------------------------------------------------------------------------------
def NF_DictSort(dictParams, sMode=""):
    dictResult=dict()
    sProc="NF_DictSort"
    sResult=""
    sModeReverse=""
    avKeys=list()

# Check Dictionary
    if NF_IsDict(dictParams)==False:
        sResult="Not Dictionary"
        return sResult

# Array Keys per maggior uso
    lResult=NF_DictKeys(dictParams)
    if sResult=="": avKeys=lResult[1]

# Keys for Sort
    if (sMode=="") or (sMode=="K"):
        pass
    elif sMode=="VR":
        sModeReverse="D"
    elif sMode=="KR":
        sModeReverse="D"
    elif sMode=="V":
        lResult=NF_DictValues(dictParams)
        if sResult=="": avKeys=lResult[1]
    else:
        sResult="Mode invalid " + str(sMode)

# Sort
    if sResult=="":
        lResult=NF_ArraySort(avKeys,sModeReverse)
        sResult=lResult[0]

# New Dictionary
    if sResult=="":
        avKeys=lResult[1]
        for vKey in avKeys:
            dictResult[vKey]=dictParams[vKey]

# Uscita
    return NF_Result(sResult,sProc,dictResult)
