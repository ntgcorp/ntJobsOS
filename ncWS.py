#-------------------------------------------------------------------------------
# Name:        ncWS
#-------------------------------------------------------------------------------
# IN PREPARAZIONE. MODULO DI INTERFACCIA VARI SERVIZI WEB SERVICE
# Init
# Action
# Post,Get,Delete,Path,Put
# -----------------------------------------------------------------------
import nlSys,requests

# Engine caricate
NT_ENV_WSENG_REQ=False

NT_ENV_WS_RES={
    "200":["OK","The requested action was successful"],
    "201":["Created"  "A new resource was created"],
    "202":["Accepted","The request was received, but no modification has been made yet."],
    "204":["No Content","The request was successful, but the response has no content."],
    "400":["Bad Request","The request was malformed."],
    "401":["Unauthorized","The client is not authorized to perform the requested action."],
    "404":["Not Found","The requested resource was not found."],
    "415":["Unsupported Media Type","The request data format is not supported by the server."],
    "422":["Unprocessable Entity","The request data was properly formatted but contained invalid or missing data."],
    "500":["Internal Server Error","The server threw an error when processing the request."]}

# ----------------------- CLASSI ---------------------------
# WEB SERIVCE CLASS
# sType(type): req(requests)
class NC_WS():
    sType=""                
    objWS=None
    bOpen=False
    sUrl=""
    sUser=""
    sPwd=""
    vResponse=None
    dictResponse=None
    nStatusCode=0
    dictParams=None

# -------------- METODI --------------
    def __init__(self):
        pass

# Inizializzazione con ritono
# Parametri
#   sType(type)=rest, ....
#   sURL(url)
    def Init(self, **kwargs):
        sResult=""
        sProc="WS.INIT"

# Parametri
        sResult=self.Params(self, kwargs)
        

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Chiude Connessione
# ------------------------------------------------------------------------------
    def End(self):
        sProc="WS.END"
        sResult=""

# Uscita
        sResult=nlSys.NF_ErrorProc(sResult,sProc)

# Set Params
    def Params(self, **kwargs):
        sResult=""
        sProc="WS.PARAMS"

        for key, value in kwargs.items():
            if key=="type":
                self.sType=value
            elif key=="url":
                self.sUrl=value
            elif key=="user":
                self.sUser=value
            elif key=="pwd":
                self.sPwd=value
            elif key=="params":
                self.dictParams=value
            else:
                sResult="key invalid: " + key

# Verifiche
        if sResult=="":
            if self.sType=="" or (self.sType != "req"): sResult="not engine"
            if self.sURL=="": sResult="not url"

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ------------------- GET --------------------
    def Get(self, **kwargs):
        sProc="WS.GET"
        sResult=""

# Parametri
        sResult=self.Params(self, kwargs)

# Esecuzione
        if sResult=="":
            try:
                self.vResponse = requests.get(self.sUrl)
                self.vResponse.json()
                self.nStatusCode=self.vResponse.status_code
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore WS "
# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ------------------- PAYCH --------------------
    def Patch(self, **kwargs):
        sProc="WS.PATCH"
        sResult=""
        
# Esecuzione
        sResult=self.Action("patch",kwargs)

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ------------------- DELETE --------------------
    def Delete(self, **kwargs):
        sProc="WS.DELETE"
        sResult=""

# Esecuzione
        sResult=self.Action("delete",kwargs)

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# ------------------- PUT --------------------
    def Put(self, **kwargs):
        sProc="WS.PUT"
        sResult=""

# Esecuzione
        sResult=self.Action("put",kwargs)

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)

# Esegue POST
# ------------------------------------------------------------------------------
    def Post(self, **kwargs):
        sProc="WS.POST"
        sResult=""

# Esecuzione
        sResult=self.Action("post",kwargs)

# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)
    
    # Esegue Action riutilizzata da Post, Put, Patch
# ------------------------------------------------------------------------------
    def Action(self, sAction, **kwargs):
        sProc="WS.ACTION"
        sResult=""

# Parametri
        sResult=self.Params(self, kwargs)
        if sResult=="": 
            sResult=nlSys.NF_ParamVerify({"arg":sAction},inlist={"arg": ("post","put","patch")})

# Esecuzione
        if sResult=="":
        # Chiamata
            try:
                if sAction=="post":
                    if nlSys.NF_DictLen(self.dictParams)>0:
                        self.vResponse = requests.post(self.sUrl,json=self.dictParams)
                    else:
                        self.vResponse = requests.post(self.sUrl)
                elif sAction=="patch":
                    if nlSys.NF_DictLen(self.dictParams)>0:
                        self.vResponse = requests.patch(self.sUrl,json=self.dictParams)
                    else:
                        self.vResponse = requests.patch(self.sUrl)
                elif sAction=="put":
                    if nlSys.NF_DictLen(self.dictParams)>0:
                        self.vResponse = requests.put(self.sUrl,json=self.dictParams)
                    else:
                        self.vResponse = requests.put(self.sUrl)
                elif sAction=="delete":
                    if nlSys.NF_DictLen(self.dictParams)>0:
                        self.vResponse = requests.delete(self.sUrl,json=self.dictParams)
                    else:
                        self.vResponse = requests.delete(self.sUrl,json=self.dictParams)
        # Post Chiamata        
                self.vResponse.json()
                self.nStatusCode=self.vResponse.status_code
            except Exception as e:
                sResult=getattr(e, 'message', repr(e)) + "Errore WS "
# Uscita
        return nlSys.NF_ErrorProc(sResult,sProc)