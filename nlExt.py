# ntJobsPy Framework
# CORE EXTENSION LIBRARY - DataTypes - OS - Basic Files - Process - Date
# --------------------------------------------------------------------
# Lib per gestione path e files
from pathlib import Path
# For NF_File*
import os
# For NF_FileDelete (rmdir)
import shutil
# For NF_PathFind + NF_FileCopy
from sys import platform
# Lib per gestione Replace
from string import Template
# Per File Temporanei
import tempfile
# Per Argomenti (NF_Args)
import sys
import nlSys

# ----------------------- FUNZIONI DI BASE ---------------------------

# ---------------------- FILES & PATH  -----------------------

def NF_PathScan(patho, mode): # list file(s) & folder(s)
    paths = []
    files = []
    pathx = ""
    for i in patho:
        if i in ("\\","/"):
            pathx += os.sep
        else:
            pathx += i
    if os.sep != pathx[-1:]:
        target_path = pathx + os.sep
    else:
        target_path = pathx
    if mode == "top":
        res = os.listdir(target_path)
        for i in res:
            if os.path.isfile(target_path + i):
                files.append(target_path + i)
            else:
                paths.append(target_path + i)
    elif mode == "all":
        res = os.walk(target_path)
        for path,d,filelist in res:
            if path[-1] != os.sep:
                paths.append(path + os.sep)
            else:
                paths.append(path)
            for filename in filelist:
                files.append(os.path.join(path,filename))
    return paths, files

# File Attributi
# sResult,dictAttr
# N=Nome, DC=DataCreazione, DU=DataAggiornamento, AAAAMMHH.HHMMSS, T=F/D, S=Size
class NC_File:
    N=""        # Nome
    DC=""       # DataCreazione
    DU=""       # DataUpdate
    T=""        # Type F/D
    S=0         # Dimensione

    def __init():
        pass
# Empty
    def Empty(self):
        return self.N==""
# Get Attr
    def Get(self, sPath, **kwargs):
        sResult=""
        sProc="File.Attr"

# Estrazione Principale
        try:
            self.S=os.path.getsize()
        except Exception as e:
            sResult=getattr(e, 'attr.size', repr(e)) + "get " + sPath

# Altri dati Aggiornamento
        if sResult=="":
            try:
                self.DC=os.path.getctime(sPath)
                self.DU=os.path.getmtime(sPath)
                self.S=os.path.getsize(sPath)
                bDir=os.path.isdir(sPath)
                self.T=nlSys.iif(bDir,"D","F")
            except Exception as e:
                sResult=getattr(e, 'attr.size', repr(e)) + "get " + sPath

# Conversione Date
        if sResult=="":
                sResult,self.DC=nlSys.NF_DateTime_DTHH(self.DC)
        if sResult=="":
                sResult,self.DU=nlSys.NF_DateTime_DTHH((self.DU))

# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Remapping sFileIn, sFileOut
# Return 3 parameters. sResult, New FileIn, New FileOut
# Change FileOut only if ""
def NF_FileChangeExt(sFileIn, sFileOut, sExtOut):
    sResult=""
    sProc="FileChangeExt"

# Check FileIn Exist
    sResult,sFileIn=nlSys.NF_FileExistMap(sFileIn)

# FileOut create
    if sResult=="":
        if sFileOut=="" or sFileOut=="#":
            sPath,sFile,sExt=nlSys.NF_PathScompose(sFileIn)
            nlSys.NF_DebugFase(True, "FileIn. Path: " + sPath + ", File: " + sFile + ", Ext: " + sExt, sProc)
            sFileOut=sPath + sFile + "." + sExtOut
            nlSys.NF_DebugFase(True, "FileOut " + sFileOut, sProc)

# Fine
    sResult=nlSys.NF_ErrorProc(sResult, sProc)
    return sResult,sFileIn,sFileOut

# Path.Rename
def NF_PathMove(sFileIn, sPathOut, **kwargs):
    sProc="NF_PathMove"
    sResult=""

# Delete Old
    bReplace=nlSys.NF_DictGet(kwargs, "replace", False)
    bFolder=nlSys.NF_PathType(sFileIn)

# Rename
    try:
        os.move(sFileIn, sPathOut)
    except:
        sResult="Move file " + sFileIn + " in " + sPathOut

# Uscita
    return nlSys.NF_ErrorProc(sResult,sProc)

# Path Temporaneo. Parametri: sPathBase, sPrefix, Type="FD"
# Ritorno: lResult 0=sResult, 1=PathCreato
def NF_PathTemp(sPathBase="", sPrefix="", sType="F"):
    sProc="NF_PathTemp"
    sResult=""
    sPath=""

# Test
    if (sType!="F") and (sType!="D"): return nlSys.NF_ErrorProc("Tipo invalido " + sType,sProc)

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
    return [nlSys.NF_ErrorProc(sResult,sProc),sPath]

# Path.Copy/XCopy
# F=Singolo File P=Path, (F=File), D=Dir
def NF_PathCopy(sPathIn, sPathOut, sType="F"):
    sProc="NF_PathCopy"
    sResult=""

# Flags
    bDir=nlSys.NF_StrFind(0,sType,"D") != -1
    bPath=nlSys.NF_StrFind(0,sType,"P") != -1
    bFile=(nlSys.NF_StrFind(0,sType,"F") != -1) or (sType=="F")

# Rename
    try:
        if bDir: shutil.copytree(sPathIn, sPathOut)
        if bPath: shutil.copyfile(sPathIn, sPathOut)
        if bFile: shutil.copy(sPathIn, sPathOut)
    except:
        sResult="Copia " + sPathIn + " in " + sPathOut + ", Type: " + sType

# Uscita
    return nlSys.NF_ErrorProc(sResult,sProc)


# ----------------------------- PARAMETRI ------------------------------

def NF_ArgsGet():  # read command shell's argument(s)
    """
    read command shell's argument(s)

    :return: dict
    """
    opts = sys.argv[1:]
    argv = ""
    res = {}
    unlabeled = 0
    for i in opts:
        if len(argv) > 0 and "-" != i[0]:  # 获取标签
            res.update({argv: i})
            argv = ""
        elif "-" == i[0]:
            argv = i
            res.update({argv: ""})
        else:
            res.update({unlabeled: i})
            unlabeled += 1
    return res

# ------------------------------- TEMPO E DATE -------------------------

#  ------------- DIAGNOTICA E GESTIONE ERRORI ---------------------

# ------------------------------ STRINGHE -------------------------------

def NF_FileSha256(filename: str) -> str:
    ''' Calculate the SHA256 as string for the given file '''
    try:
        hashval = NF_StrSha256()
        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
               hashval.update(block)
        return hashval.hexdigest()
    except FileNotFoundError:
        return ''

def NF_Str2bytearray(inputstr: str) -> bytearray:
    ''' Convert string to bytearray '''
    barr = bytearray()
    # =bytearray(bytes.encode()) breaks the bytes sequence due to the encoding
    for c in inputstr:
        barr.append(ord(c))
    return barr

class NC_StringBig:
    ''' Class to concatenate long strings through a short buffer for better performances '''
    def __init__(self):
        self.buflen = 262144
        self.reset()

    def reset(self):
        ''' Reset the string buffer '''
        self.tmp = ''
        self.data = ''

    def push(self, buffer: str):
        ''' Add a string to the buffer '''
        self.tmp += buffer
        if len(self.tmp) >= self.buflen:
            self.data += self.tmp
            self.tmp = ''

    def pop(self) -> str:
        ''' Get the complete buffered string '''
        self.data += self.tmp
        self.tmp = ''
        return self.data

    def override(self, buffer: str):
        ''' Replace the current buffer by a new string '''
        self.tmp = ''
        self.data = buffer

    def length(self):
        ''' Get the length of the buffered string '''
        return len(self.tmp) + len(self.data)

    def rstrip(self):
        ''' Strip the buffer from the right '''
        self.data += self.tmp
        self.tmp = ''
        self.data = self.data.rstrip()

    def lastchar(self) -> str:
        ''' Get the last character of the buffered string '''
        return self.tmp[-1:] or self.data[-1:]

# --------------------------- ARRAY ---------------------------

# ----------------------------------- DICTIONARY ----------------------------------
