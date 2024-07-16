# Interface to Panda with debug & errors management
# -----------------------------------------------------------------------
import pandas as pd
import nlSys
import openpyxl

# ----------------------- CLASSI ---------------------------
# PANDA_XLS Class
# For Excel Object
class NC_PANDA_XLS:
    objExcel=""
    bOpen=False
    df=[]
    bFilled=False
    sFilePathXLS=""
    sDelimiter=";"

# -------------- METODI --------------
    def __init__(self):
        pass

    def read_from_xls(self,sFileXLS,sSheetName):
        sProc="PANDA.XLS.FROM"
        sResult=""

# SheetName
        if sSheetName=="":
            sSheetName="Sheet1"

# Richiamo Funzione Panda
        if sResult=="":
            nlSys.NF_DebugFase(True, "Read file XLS to DF: " + sFileXLS + ", Sheet " + sSheetName, sProc)
            try:
                self.df=[]
                self.bFilled=False
                self.df = pd.read_excel(sFileXLS, sheet_name=sSheetName, engine="openpyxl")
                self.bFilled=True
                self.sFileXLS=sFileXLS
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore lettura XLS  " + sFileXLS + ", Sheet: " + sSheetName
# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Scrive su CSV. Ritorno: sResult
    def write_to_csv(self, sFileCSV):
        sProc="PANDA.CSV.TO"
        sResult=""

# Richiamo funzione panda
        if self.bFilled==True:
            nlSys.NF_DebugFase(True, "Write file CSV from DF " + sFileCSV, sProc)
            try:
                self.df.to_csv(sFileCSV, index=False, header=True)
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore scrittura CSV " + sFileCSV
        else:
            sResult="Dataframe empty"

# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        nlSys.NF_DebugFase(True, "End write to csv: " + sResult, sProc)
        return sResult

# Legge da CSV. Ritorno: sResult e self.df
    def read_from_csv(self, sFileCSV):
        sProc="PANDA.CSV.FROM"
        sResult=""

# Richiamo funzione panda
        nlSys.NF_DebugFase(True, "Read file CSV " + sFileCSV, sProc)
        try:
            self.df=[]
            self.bFilled=False
            self.df = pd.read_csv(sFileCSV,sep=self.sDelimiter,header=0)
            self.bFilled=True
        except:
            sResult="Errore lettura file " + sFileCSV

# Debug print
        print(self.df)

# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Scrive su XLS. Ritorno: sResult
# Facoltativi
#   append=True/false
#   NoOpen=True (file già aperto in scrittura per aggiunte, objExcel)
#   NoClose=True (non chiudere il file per ulteriori aggiunte
#   df deve essere filled
    def write_to_xls(self, sFileXLS, sSheetName, **kwargs):
        sProc="PANDA.XLS.TO"
        sResult=""
        bAppend=False
        bNoOpen=False
        bNoClose=False

# Argomenti opzionali
        for key, value in kwargs.items():
            if key=='append':
                bAppend=value
            elif key=='NoOpen':
                bNoOpen=value
            elif key=='NoClose':
                bNoClose=value
            else:
                sResult="Parameter invalid " + key

# Verifiche
        if sSheetName=="":
            sSheetName="Sheet1"
        if sFileXLS=="":
            sResult="file name invalid " + sFileXLS

# Conversione SheetName "*" in None per scriverli tutti
#        if sSheetName=="*":
#            sSheetName=None

# Casistica Append. Occorre usare openpyxl
        if sResult=="":
            if bAppend==True:
                nlSys.NF_DebugFase(True, "Open XLS file for Append " + sFileXLS, sProc)
                try:
                    self.ObjExcel.book=openpyxl.load_workbook(sFileXLS)
                    self.bOpen=True
                    self.sFilePathXLS=sFileXLS
                except Exception as e:
                    sResult=getattr(e, 'message', repr(e)) + "Errore apertura XLS per append " + sFileXLS
# Creazione ExcelWriter
        if (sResult=="") and (bNoOpen==False):
# Cancellazione Preventiva
            if nlSys.NF_FileExist(sFileXLS):
                nlSys.NF_DebugFase(True, "Delete first XLS " + sFileXLS, sProc)
                sResult=nlSys.NF_FileDelete(sFileXLS,"F")
# Create New empty XLS File
            if sResult=="":
                nlSys.NF_DebugFase(True, "Open XLS file for Writing " + sFileXLS, sProc)
                try:
                    self.objExcel=pd.ExcelWriter(sFileXLS, engine="xlsxwriter")
                    self.bOpen=True
                    self.sFilePathXLS=sFileXLS
                except Exception as e:
                    sResult=getattr(e, 'message', repr(e)) + " scrittura per file " + sFileXLS

# Verifiche
        nlSys.NF_DebugFase(True, "Verifica XLS Open and DF empty", sProc)
        if (sResult=="") and (self.bOpen==False):
            sResult="File XLS non aperto " + sFileXLS
        if self.bFilled==False:
            sResult="Dataframe empty"

# Scrive df to sheet
        if sResult=="":
# Debug code
            nlSys.NF_DebugFase(True, "Write XLS file with DF " + sFileXLS + ", SheetName " + sSheetName, sProc)
            sResult,nRows,nCols=self.df_size()
            nlSys.NF_DebugFase(True, "df size" + sResult + ", nRows " + str(nRows) + ", Cols: " + str(nCols), sProc)
            try:
                #self.df.to_excel(self.objExcel, sheet_name=sSheetName,  engine='xlsxwriter', index=False)
                #self.df.to_excel(self.objExcel, sheet_name=sSheetName,  engine='xlwt', index=False)
                self.df.to_excel(self.objExcel, index=False)
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + " salvataggio per file " + sFileXLS + ", sheet: " + sSheetName
# Chiude File
        if (sResult=="") and (bNoClose==False):
            sResult=self.close_xls()

# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        nlSys.NF_DebugFase(True, "End write to xls: " + sResult, sProc)
        return sResult

# Chiude File - Deve essere già Aperto
    def close_xls(self):
        sProc="PANDA_XLS_CLOSE"
        sResult=""
# Verifiche
        if self.bOpen==False:
            sResult="File non aperto"
# Chiusura
        if sResult=="":
            try:
                self.objExcel.close()
                self.bOpen=False
                self.sFilePathXLS=""
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + " chiusura file " + self.sFilePathXLS
# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult

# Rows, Cols Dataframe
    def df_size(self):
        sProc="DF_SIZE"
        nRows=0
        nCols=0
        sResult=""
        try:
            anSize=self.df.shape
            print(sProc + str(anSize))
            nRows=anSize[1]
            nCols=anSize[0]
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + " df size get"
# Fine
        sResult=nlSys.NF_ErrorProc(sResult, sProc)
        return sResult,nRows,nCols
