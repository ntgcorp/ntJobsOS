#-------------------------------------------------------------------------------
# Comandi ntJobs module
#-------------------------------------------------------------------------------
import nlSys
import os

DA ELIMINARE

# -------------------------------- COMMANDS ----------------------------------

# Command CSV2XLS
def cmd_CSV2XLS(*args):
    sProc="CMD_CSV2XLS"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# Parameters
    if nArgs>0: sFileIn=args[0]
    if nArgs>1: sFileOut=args[1]
    if nArgs>2: sSheetName=args[2]
    nlSys.NF_DebugFase(True, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=NF_PathRemapInOut(sFileIn,sFileOut,"xlsx")

# Debug Message
    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(True, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_csv(sFileIn)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(True, "Write XLS", sProc)
        sResult=objPanda.write_to_xls(sFileOut,sSheetName)

# Fine
    sResult=nlSys.NF_ErrorProc(sResult, sProc)
    return sResult

# Comando XLS2CSV
def cmd_XLS2CSV(*args):
    sProc="CMD_XLS2SCSV"
    sResult=""
    sFileIn=""
    sFileOut=""
    sSheetName=""
    nArgs=len(args)

# Parameters
    if nArgs>0: sFileIn=args[0]
    if nArgs>1: sFileOut=args[1]
    if nArgs>2: sSheetName=args[2]
    nlSys.NF_DebugFase(True, "Parameters. Arg0: " + sFileIn + ",  Arg1: " + sFileOut + ", Arg2: " + sSheetName, sProc)

# Remapping in e out (da non specificare o "#" se da remapping
    sResult,sFileIn,sFileOut=NF_PathRemapInOut(sFileIn,sFileOut,"csv")

    if sResult=="":
# Create Panda objct + Read CSV
        import ncPanda
        objPanda=ncPanda.NC_PANDA_XLS()
        nlSys.NF_DebugFase(True, "Read & Write. IN " + sFileIn + ",  OUT " + sFileOut + ", Sheet: " + sSheetName, sProc)
        sResult=objPanda.read_from_xls(sFileIn, sSheetName)
    if sResult=="":
        sResult,nRows,nCols=objPanda.df_size()
        nlSys.NF_DebugFase(True, "Size DF " + str(nRows) + ", Cols: " + str(nCols),sProc)
# Save to XLS
    if sResult=="":
        nlSys.NF_DebugFase(True, "Write CSV", sProc)
        sResult=objPanda.write_to_csv(sFileOut)

# Fine
    sResult=nlSys.NF_ErrorProc(sResult, sProc)
    return sResult

# Remapping sFileIn, sFileOut
# Return 3 parameters. sResult, New FileIn, New FileOut
def NF_PathRemapInOut(sFileIn,sFileOut,sExtOut):
    sResult=""
    sProc="PathRemapInOut"

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