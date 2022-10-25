# Class ntMmail. Send Only One mail with features
# -----------------------------------------------------------
#
# Supporto multicanale (SMTP e WS=WebService da implementare, GMAIL da implementare),
# formato TXT/HTML, multiattach
# Reference: ntSys

import smtplib, ssl
import yagmail
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ntSys
NT_ENV_TEST_MAILC=True
asFMT_MAIL_HDR=("ID","TO","CC","BCC","SUBJECT","ATTACH","FORMAT","BODY","F1","F2","F3","ATTR")
asFMT_MAIL_SMTP=("SMTP.USER","SMTP.PASSWORD","SMTP.SERVER", "SMTP.PORT", "SMTP.SSL")
    
class NC_Mail: 
# sAttach, sResult, dictREC, dictREC2, sChannel
# MailParams: Parametri per invio Email. Richiamata da MailSend per ogni messaggio
# MailParamsLogin: Parametri solo per il login
# MailLogin_Smtp, MailLogin_WS: Funzione di Login a vari servizi
# MailSend: Invio singolo messaggio usando dictMail (lo stesso di inizializzazione)
# MailSendCSV: Invio Massivo da formato ntMail
# MailMessageCreate: Richiamato da MailSend per preparare il messaggio
# MailAttachSingle: Lettura Attach "singolo" - Richiamato da MessageCreate
# MailAttachMulti: Lettura tutti gli attach - Richiamato da MessageCreate

# Campi Classe
    dictREC={"TO":"","CC":"","BCC":""} # TO,CC,BCC string
    dictREC2={"TO":[""],"CC":[""],"BCC":[""]} # TO, CC, BCC splitted/trimmed/verifiedEC=dict()
    dictSMTP=dict()
    sResult=""
    sChannel=""
    sMessageTxt=""
    sFrom=""
    sID=""
    nWait=1
    sSubject=""
    sAttach=""
    sBody=""
    sBodyFile=""
    sFormat=""
# Della Sessione
    bSSL=False
    bLogin=False
# Inizio Fine Sessione Mail - Per Logs - Per Mail Massive
    bMassive=False       # Massiva. altrimenti logoff server alla fine
    nEmailSent=0
    nEmailToSend=0
    dictCSV=dict()
    dtMailStart=None
    dtMailEnd=None
        
# Parametri MAIL - IL LOGIN VIENE FATO SOLO IN FASE INIZIALIZZAZIONE, NON AD OGNI MAIL
# ---------------------------------------------------------------------------------------
    def MailParams(self, dictMail):
        sProc="MAIL_PARAMS"
        sResult=""
        self.sResult=""
        
    # Verifica dictMail
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Recupero Params da dictMail. Chiavi: Dict:" + str(type(dictMail)) + ", " + str(ntSys.NF_DictLen(dictMail)) + "," + str(dictMail), sProc)        
        if ntSys.NF_DictLen(dictMail)<0: sResult=("Assente parametro dictMail o vuoto")
        
    # Parametri - Assegnazione solo per quelli passati via dictMail, NON TUTTI (in caso di chiamata per cambiamento)
        if (sResult==""):
            asKeys=("CC","BCC","TO","BODY","ID", 
                    "BODY.FILE", "SUBJECT", "CHANNEL", 
                    "FROM","ATTACH","FORMAT")        
            for sKey in asKeys:
                if ntSys.NF_DictExistKey(dictMail, sKey):
                    ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Recupero parametro da dictParams: " + sKey,sProc)
                    # Per CC, TO, BCC
                    for sKey2 in ("CC","TO","BCC"):
                        if (sKey==sKey2): self.dictREC[sKey]=ntSys.NF_DictGet(dictMail,sKey,"")
                    # Per gli altri campi
                    if sKey=="BODY": self.sBody=ntSys.NF_DictGet(dictMail,sKey,"")
                    if sKey=="BODY.FILE": self.sBodyFile=ntSys.NF_DictGet(dictMail,sKey,"")
                    if sKey=="FROM": self.sFrom=ntSys.NF_DictGet(dictMail,sKey,"")                        
                    if sKey=="SUBJECT": self.sSubject=ntSys.NF_DictGet(dictMail,sKey,"")
                    if sKey=="FORMAT": self.sFormat=ntSys.NF_DictGet(dictMail,sKey,"TXT")
                    if sKey=="WAIT": self.nWait=ntSys.NF_DictGet(dictMail,sKey,1)
                    if sKey=="ATTACH": self.sAttach=ntSys.NF_DictGet(dictMail,sKey,"")
                    if sKey=="ID": self.sID=ntSys.NF_DictGet(dictMail,sKey,"")
                    if sKey=="CHANNEL": self.sChannel=ntSys.NF_DictGet(dictMail,sKey,"SMTP")
                         
            # Output Estrazione
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "dictMail: " + str(dictMail), sProc)
        
# SPLIT TO,BCC,CC in array - TRIM+UCASE - very valid mail and
        if (sResult==""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Recupero Array TO, CC, BCC",sProc)
            asKeys=ntSys.NF_DictKeys(self.dictREC)
            for sREC_key in asKeys:
                sREC_value=self.dictREC[sREC_key]
                if ntSys.NF_StrTest(sREC_value):
                    asTemp=sREC_value.split(",")
                    #asTemp=ntSys.NF_ArrayStrNorm(asTemp,"LRUS")        
                    self.dictREC2[sREC_key]=asTemp
                    #print (sProc + " gruppo: " + sREC_key + " " + str(self.dictREC2[sREC_key]))                
                                        
# ------------- Verify Parameters --------------

# CAMPI OBBLIGATORI
        if (sResult==""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Verifica esistenza, CHANNEL, FROM: " + self.sChannel + ", " + self.sFrom, sProc)
            if (self.sChannel == ""): sResult = "channel assente"
            if (self.sFrom == ""): sResult = ntSys.NF_StrAppendExt(sResult, "from assente")
                        
# ATTACH
        if (sResult!="") and (self.MailAttachExists()):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Recupero File(s) Attach",sProc)
            asAttach=self.sAttach.split(",")
            asAttach=ntSys.NF_ArrayStrNorm(asAttach,"LR")
            for sFile in asAttach:
                sResult=ntSys.NF_StrAppendExt(ntSys.NF_FileExistErr(sResult),sFile) 
            if ntSys.NF_StrTest(sResult): sResult="File Attachment: " + sResult

# TO, CC, BCC, FROM
        if (sResult==""): sResult=self.MailAddressVerify()
                    
# BODY, BODY.FILE(priority)
        if (sResult==""):    
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Fase: Recupero BODY, BODY.FILE",sProc)
            if self.sBodyFile != "": 
                ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Fase: Recupero BODY.FILE",sProc)
            # Normalize
                lResult=ntSys.NF_PathNormal(self.sBodyFile)
                sResult=lResult[0]
                # Read Body File
                if sResult=="":
                    self.sBodyFile=lResult[5]            
                    lResult=ntSys.NF_StrFileRead(self.sBodyFile)
                    sResult=lResult[0]
                    if (sResult==""): self.sBodyFile=lResult[1]
                    
# CHANNEL PARAMS (se LOGIN=False)        
        if (sResult=="") and (self.bLogin==False): sResult=self.MailParamsLogin(dictMail)                                            

        # Fine
        sResult=ntSys.NF_ErrorProc(sResult, sProc)                                    
        self.sResult=sResult
        return sResult
    
# Check there are attachments
    def MailAttachExists(self):
        return (len(self.sAttach) != 0)
    
# SMTP - SSL - LOGIN
# ---------------------------------------------------------------------------------------
    def MailSmtpLogin(self):        
        sProc="MAIL_Login_SMTP"
        sResult=""
        
    # Test Stato attuale
        if (self.sResult!=""): return self.sResult
        if (self.bLogin): sResult = "login già effettuato."
        
    # Login Per Canale e Tipologia
        if (sResult == ""): 
            if (self.sChannel=="SMTP") and (self.bSSL): sResult=self.MailSmtpLoginSSL()
            elif (self.sChannel=="SMTP") and (self.bSSL==False): sResult=self.MailSmtpLoginTTLS()        
        # ERRORE LOGIN
            else:
                sResult="Canale non gestito: " + str(self.sChannel)
    # Fine    
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return self.sResult
    
# Login STMP: SSL
    def MailSmtpLoginTTLS(self):        
    # Start
        sProc="MAIL_SmtpLoginTTLS"
        sResult=""
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.TTLS Login, Server/Port" + str(self.dictSMTP["SMTP.SERVER"])+ "/" + str(self.dictSMTP["SMTP.PORT"]), sProc)                                                            
    
    # Crezione Oggetto SMTP SERVER
        try:
            self.SMTP_Server=smtplib.SMTP(self.dictSMTP["SMTP.SERVER"],self.dictSMTP["SMTP.PORT"])
        except:
            sResult="Logim SMTP TTLS"
    # TTLS
        if (sResult==""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.TTLS Start TTLS", sProc)  
            try:
                self.SMTP_Server.starttls()
            except:
                sResult="Login SMTP Start TTLS"
    # LOGIN SMTP                                    
        if (sResult==""):            
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.TTLS Login", sProc)  
            try:
                self.SMTP_Server.login(self.dictSMTP["SMTP.USER"],self.dictSMTP["SMTP.PASSWORD"])
            except:
                sResult="Login SMTP TTLS Login"
    # Fine OK FLAG LOGIN 
        if (sResult==""): self.bLogin=True               
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.TTLS Login: " + ntSys.iif(sResult=="","Ok",sResult), sProc)
        return sResult

# Login STMP: SSL
    def MailSmtpLoginSSL(self):
    # Start
        sProc="MAIL_SmtpLoginSSL"
        sResult=""        
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SSL Login: Start, Context", sProc)
    # Context
        try:
            self.context = ssl.create_default_context()
        except:
            sResult="Creazione context"
    # Crea Oggetto
        if (sResult==""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SSL Login: Crea Oggetto", sProc)     
            try:                    
                self.SMTP_Server = smtplib.SMTP_SSL(self.dictSMTP["SMTP.SERVER"],self.dictSMTP["SMTP.PORT"], context=self.context)
            except:
                sResult=ntSys.NF_ErrorProc("Creazione oggetto smtp ssl", sProc)
    # Server Login
        if (sResult==""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SSL Server Login", sProc)
            try:                           
                self.SMTP_Server.login(self.dictSMTP["SMTP.USER"],self.dictSMTP["SMTP.PASSWORD"])
            except:
                sResult="Login Server"                                          
    # Fine
        if (sResult==""): 
            self.bLogin=True
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.SSL Login: Ok", sProc)  
        return sResult
    
# SMTP - QUIT
# ---------------------------------------------------------------------------------------
    def MailSmtpQuit(self):        
        sProc="MAIL_Quit_SMTP"
        sResult=""
        try:
            self.SMTP_Server.quit()
        except:
            sResult="SMTP Quit"
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "SMTP.Quit: " + ntSys.iif(sResult=="","Ok",sResult), sProc)
        return ntSys.NF_ErrorProc(sResult,sProc)
            
# Verifica di tutte le mail
# Ritorno: sResult tutte le mail sbaglite
# ---------------------------------------------------------------------------------------
    def MailAddressVerify(self):
        sProc="MAIL_VERIFY_ADDR"
        sResult=""    
        
        # Verifica PROM
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Verifica indirizzi mail, FROM", sProc)        
        sTemp=ntSys.iif(ntSys.NF_StrIsEmail(self.sFrom),"","FROM: " + self.sFrom)
        sResult=ntSys.NF_StrAppendExt(sResult, sTemp)
        
        # Verifica TO, CC, BCC
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Verifica indirizzi mail, TO, CC, BCC", sProc)
        for sType in ("TO","CC","BCC"):
            if ntSys.NF_DictExistKey(self.dictREC2, sType):
                for sMail in self.dictREC2[sType]:
                    if ntSys.NF_NullToStr(sMail) != "":
                        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, ": Verifica " + sType + " " + sMail, sProc)
                        sTemp=ntSys.iif(ntSys.NF_StrIsEmail(sMail),"", sType + ": " + str(sMail) + ", " + str(len(sMail)))
                        sResult=ntSys.NF_StrAppendExt(sResult, sTemp)
        
        #  Completamento se sResult != ""
        if ntSys.NF_StrTest(sResult): sResult = "Mail non valide: " + sResult
        
        # Fine
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        return sResult
    
# Parametri LOGIN
# Viene eseguito da fuori ***SOLO*** se NON NON C'E' STATO LOGIN AL CANALE
# ---------------------------------------------------------------------------------------
    def MailParamsLogin(self, dictMail):
        sProc="MAIL_PARAMS_LOGIN"
        sResult=""                

# Verifica Canale        
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Params Login", sProc)
        if ntSys.NF_ArrayFind(("SMTP","GMAIL", "WS"), self.sChannel) < 0: sResult = self.sChannel + " channel non trovato"

# CHANNEL SMTP
        if (self.sChannel=="SMTP") and (self.sResult==""):
            sResult=ntSys.NF_DictExistKeys(dictMail, asFMT_MAIL_SMTP)        
            # SMTP - GET in dictSMTP - Reset default to "", Port=465 default
            # Prende dati SMTP e Default
            if sResult=="":
                ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Params Login SMTP channel", sProc)
                # Prende Dati da dictMail
                self.dictSMTP=ntSys.NF_DictFromKeys(dictMail, asFMT_MAIL_SMTP)                
                for sKey in ntSys.NF_DictKeys(self.dictSMTP):
                    print ("SMTP.PARAM: " + sKey + ", " + str(self.dictSMTP[sKey]))
                    if (sKey=="SMTP.PORT"):
                        self.dictSMTP[sKey]=ntSys.NF_NullTo0(self.dictSMTP[sKey])                        
                    else:
                        if self.dictSMTP[sKey]==None: self.dictSMTP[sKey]=""
                        
            # Verifica Porta - Stinga convertita in numero e deve essere porta supportata
                vPort=self.dictSMTP["SMTP.PORT"]
                print ("smtp porta str: " + str(vPort))
                anPorts=(587,465,25)
                if ntSys.NF_IsString(vPort):
                    if vPort.isnumeric():                    
                        vPort=int(vPort)
                        print ("smtp porta int: " + str(vPort))
                    else:
                        sResult="Errore porta non specificata come numero"
                if (sResult == ""):
                    print ("smtp porta: " + str(vPort))
                    if (ntSys.NF_ArrayFind(anPorts,vPort)<0):
                        sResult="Porta smtp non supportata: " + str(vPort) + "(" + str(anPorts) + ")"
                self.dictSMTP["SMTP.PORT"]=vPort
                ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Params Login, porta SMTP" + str(self.dictSMTP["SMTP.PORT"]), sProc)
                
# CHANNEL WS
        if (self.sChannel=="WS") and (sResult==""):
            pass

# RITORNO
        self.sResult=sResult
        return sResult
    
# Create Object Message To Send
# ---------------------------------------------------------------------------------------
    def MailMessageCreate(self):
        sProc="MAIL_MESSAGE"
        sResult=""
        NT_ENV_TEST_MAILC_MSG=True
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "creazione corpo mail", sProc)
        
        try:
    # Header
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC_MSG, "mime.multipart", sProc)
            self.message = MIMEMultipart()
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC_MSG, "aggiunta Subject,From", sProc)
            self.message["Subject"] = self.sSubject
            self.message["From"] = self.sFrom        
            for sKey in ("To","Cc","Bcc"):
                sKey2=sKey.upper()
                ntSys.NF_DebugFase(NT_ENV_TEST_MAILC_MSG, "aggiunta " + sKey, sProc)
                self.message[sKey]=self.dictREC[sKey2]
    # Body HTML/TXT
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC_MSG, "mimetext body attach", sProc)
            if self.sFormat=="HTML":
                objBody=MIMEText(self.sBody, "html")
            else:
                objBody=MIMEText(self.sBody, "plain")
    # Attach Body
            self.message.attach(objBody)
        except:
            sResult=ntSys.NF_ErrorProc("creazione corpo mail", sProc)
            
    # Attach
        sAttach=""
        if (sResult != "") and self.MailAttachExists():            
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "aggiunta attach a corpo mail", sProc)
            for sAttach in self.sAttach:
                sResult=ntSys.NF_StrAppendExt(sResult, self.MailAttachRead(sAttach))
                            
    # End
        return sResult

# lResult. sResult
# ---------------------------------------------------------------------------------------
    def MailAttachRead(self, filename):
        sProc="MAIL_ATTACH_READ:"
        sResult=""
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Aggiunta Attach singolo: " + str(filename), sProc)
            
    # Verifica esistenza
        if ntSys.NF_FileExist(filename): return ntSys.NF_ErrorProc("Non Esistente: " + filename, sProc)
        sResult="apertura file attach: " + filename
        with open(filename, "rb", encoding=ntSys.NT_ENV_ENCODING) as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            sResult=""

    # Encode file in ASCII characters to send by email
        if (sResult==""):
            try:
                encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
                part.add_header("Content-Disposition", f"attachment; filename= {filename}",)
    # Add attachment to message and convert message to string
                self.message.attach(part)
            except:
                sResult="add header attach: " + filename
    # End
        return ntSys.NF_ErrorProc(sResult, sProc)
    
    def MailMessageCreateTxt(self):
        dictFields= {"FROM": self.sFrom,
                     "TO": ",".join(self.dictREC2["TO"]),
                     "CC": ",".join(self.dictREC2["CC"]),
                     "BCC": ",".join(self.dictREC2["BCC"]),
                     "SUBJECT": self.sSubject,
                     "BODY": self.sBody}
        self.sMessageTxt="From: <$FROM>\nTo: <$TO>\n"
        #if ntSys.NF_DictExistKey(self.dictREC2,"CC"): self.sMessageTxt += "Cc: $CC\n"
        #if ntSys.NF_DictExistKey(self.dictREC2,"BCC"): self.sMessageTxt += "Bcc: $BCC\n"    
        self.sMessageTxt += "Subject: $SUBJECT\n\n$BODY"
        self.sMessageTxt = ntSys.NF_StrReplaceDict(self.sMessageTxt,dictFields)
        #ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Messaggio creato: " + str(self.sMessageTxt), sProc)                             
        return ""
        
# Init 
# ---------------------------------------------------------------------------------------
    def __init__(self, dictMail):
        sProc="MailInit"
        print(sProc + ": Start")
        
    # Parameter con default values
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Params Get & Check", sProc)
        sResult=self.MailParams(dictMail)

    # LOGIN
        if self.sChannel=="SMTP":
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Login", sProc)    
            sResult=self.MailSmtpLogin()

    # Fine inizializzazione
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Fine inizializzazione: " + self.sResult, sProc)    
        self.sResult=sResult
            
# Invio Singola MAIL(dictMail) - con eventuale rinnovo di alcuni campi
# VIENE FATTO IL LOGIN SE NON E' ANCORA STATO FATTO
# VIENE FATTO WAIT DOPO IL SEND DI QUANTO STABILITO 
# Ritorna sResult
# ---------------------------------------------------------------------------------------
    def MailSend(self, dictParams=None):
        sProc="MailSend"
        sResult=""
        self.sResult=""
                
    # Rinnovo Parametri        
        if (sResult == "") and (dictParams != None):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Aggiunta parametri extra", sProc)
            sResult=self.MailParams(dictParams)
            
    # Invio MAIL per casistica
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Invio Mail tipologia: " + self.sChannel + ", " + self.sFormat + ", Attach: " + str(self.MailAttachExists()),sProc)
        # TXT, NO ATTACH, SMTP        
        if sResult=="":
            if self.sChannel=="SMTP":
                if (self.sFormat=="TXT") and (self.MailAttachExists()==False) :
                    sResult=self.MailSendSmtpTxtNoAttach()
        # HTM, NO ATTACH, SMTP
                if (self.sFormat=="HTML") and (self.MailAttachExists()==False):
                    sResult=self.MailSendSmtpHtmNoAttach()
        # HTM, ATTACH, SMTP
                if (self.sFormat=="HTML") and (self.MailAttachExists()):
                    sResult=self.MailSendSmtpHtmWithAttach()
    # Wait
        if self.nWait>0: ntSys.NF_Wait(self.nWait)

    # Server Quit
        if (self.bMassive==False): sResult=self.MailSmtpQuit()

    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult, sProc)
        self.sResult=sResult
        return sResult

# MailSend SmtpTxtNoAttach
    def MailSendSmtpTxtNoAttach(self):
        sProc="MailSendSmtpTxtNoAttach"        

    # Creazione Message
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Creazione oggetto messaggio", sProc)
        sResult=self.MailMessageCreateTxt()
        #message="From: <stefano.petrone@falcricrv.org>\nTo: <ntgcorp@gmail.com>\nSubject: e-mail test\n\ncorpo test"
        #self.test1()
        #receiver_email="ntgcorp@gmail.com"
        message=self.sMessageTxt
        sender_email=self.sFrom
        receiver_email=",".join(self.dictREC2["TO"])
        
    # Invio Mail
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "invio messaggio: " + str(self.sMessageTxt), sProc)
        if (sResult == ""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Invio mail", sProc)        
            try:
            #self.SMTP_Server.sendmail(self.sFrom,",".join(self.dictREC2["TO"]),message)
                self.SMTP_Server.sendmail(sender_email,receiver_email,message)
            except: 
                sResult="Invio Email: From " + str(sender_email) + ", To: " + str(receiver_email)                 
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
    
# MailSend SmtpTxtWithAttach
    def MailSendSmtpTxtWithAttach(self):
# DA COMPLETARE CON ATTACH
        sProc="MailSendSmtpTxtWithAttach"
        
    # Creazione Message
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Attach da spedire: " + sAttach, sProc)
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Creazione oggetto messaggio", sProc)
        sResult=self.MailMessageCreate()                    
    
    # Invio Mail
        if (sResult == ""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Invio mail", sProc)        
            try:
                self.SMTP_Server.sendmail(self.sFrom,self.dictREC["TO"],self.sBody)
            except: 
                sResult="invio mail: " + self.sID + str(self.dictREC["TO"])                
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult
    
# MailSend SmtpHtmNoAttach
    def MailSendSmtpHtmNoAttach(self):
        sProc="MailSendSmtpHtmNoAttach"
        
    # Creazione Message
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Creazione oggetto messaggio", sProc)
        sResult=self.MailMessageCreate()                    
    
    # Invio Mail
        if (sResult == ""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Invio mail", sProc)
            print("MSG: " + self.sMessageTxt)
            self.SMTP_Server.sendmail(self.sFrom, ",".join(self.dictREC2["TO"]), self.sMessageTxt)
            #try:
                #self.SMTP_Server.sendmail(self.sFrom,self.dictREC2["TO"],self.sBody)
#            except: 
                #sResult="invio mail: " + self.sID + str(self.dictREC2["TO"])        
        
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# MailSend SmtpHtmWithAttach
    def MailSendSmtpHtmWithAttach(self):
        sProc="MailSendSmtpHtmWithAttach"
        
    # Creazione Message
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Creazione oggetto messaggio", sProc)
        sResult=self.MailMessageCreate()                    
    
    # Invio Mail
        if (sResult == ""):
            ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Invio mail", sProc)        
            try:
                self.SMTP_Server.sendmail(self.sFrom,self.dictREC["TO"],self.sBody)
            except: 
                sResult="invio mail: " + self.sID + str(self.dictREC["TO"])        
        
    # Ritorno
        sResult=ntSys.NF_ErrorProc(sResult,sProc)
        return sResult

# MailSendCSV: Massivo
# Ritorna sResult
# dictCSV: Format. dictCSV, dove Key=ID, Value=dictMail in formato ntJobs.ntMail
# Fasi precedenti alla chiamata:
# 1: Creazione istanza NC_Mail
# 2: Controllo Parametri MailParams
# 3: Avvaloramento dictCSV come da standard del tipo KEY 0..N=ARRAY, dove 0=Nome dei campi
# 4: if sResult=="" and objMail.bLogin: objMail.MailSmtpQuit()
# 5: Eventuale controllo dei dati di fine sessione, mail tosend, mailsent, objMail.sResult
# --------------------------------------------------------------------
    def MailSendCSV(self):
        sProc="MailSendCSV"
        sResult=""
        sResultTot=""
        
    # Test
        if ntSys.NF_DictLen(self.dictCSV)<1:
            sResult="Non caricato dictCSV con file csv esterno prima di chiamare " + sProc
            return sResult
    
    # Setup
        asHeader=self.dictCSV[0]
        self.bMassive=True
        self.nEmailSent=0
        self.dtMailStart=ntSys.NF_TS_ToStr()
        asID=ntSys.NF_DictKeys(self.dictCSV)
        self.nEmailToSend=len(self.dictCSV)-1
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Numero Mail da inviare: " + str(self.nEmailToSend), sProc)
        ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Mail.Da.Spedire.dictCSV: " + str(type(self.dictCSV)) + ", " + str(self.dictCSV), sProc)
        
    # Invio Mail CSV
        for vID in asID:            
        # Singola Mail: Setup
            asMail=self.dictCSV[vID]
        # Skip Header
            if vID != 0:
            # Conversione da Array a dict
                lResult=ntSys.NF_DictFromArr(asHeader, asMail)
                sResult=lResult[0]
            # Verifica Parametri
                if sResult=="":
                    dictMail=lResult[1]
                    sResult=lResult[0]                    
                    sResult=self.MailParams(dictMail)
                    ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Mail, Params. ID: " + str(vID) + ", Type: " + str(type(dictMail)) + ", R: " + sResult + ", Params: " + str(dictMail), sProc)
            # Singola Mail: Invio
                if (sResult==""):
                    sResult=self.MailSend(dictMail)
                    ntSys.NF_DebugFase(NT_ENV_TEST_MAILC, "Mail, Send, ID: " + str(vID) + ", R: " + sResult, sProc)
            # Aggiunge TimeStamp Elaborazione + Result anche se va male                
                dictMail["TS"]=ntSys.NF_TS_ToStr()
                dictMail["R"]=sResult
                
            # Update Record Mail
            # Da verificare se necessario o viene già fatto 
            
            # Prossima Mail                
                if  sResult!="" :
                    sResultTot = ntSys.NF_StrAppendExt(sResult, "MAIL: " + str(vID) + ": " + sResult + "\n")
                else:
                    self.nEmailSent+=1
    # Ritorno        
        sResult=ntSys.NF_ErrorProc(sResultTot,sProc)
        self.dtMailEnd=ntSys.NF_TS_ToStr()
        self.sResult=sResult
        return sResult
    
# -------------------------- INVIO TRAMITE GMAIL ---------------------
# DA COMPLETARE PIU'AVANTI
# Login Necessario
    def YagLogin(self):
#receiver = "your@gmail.com"
#body = "Hello there from Yagmail"
#filename = "document.pdf"        
        sResult=""    
        self.Yag=yagmail.SMTP(self.dictSMTP["SMTP.USER"])
        self.sResult=sResult

# Login Necessario
    def YagSend(self):        
        sResult=""
        
        yagmail.send(
            to=self.dictREC2['TO'],
            subject=self.sSubject,
            content=self.sBody,
            attachments=self.sAttach)
    
        self.sResult=sResult
        return sResult
    
    def test1(self):
    # TEST

        server_user = "stefano.petrone@falcricrv.org"
        server_password = "sp"
        server_address="smtp.falcricrv.org"
        server_port=25
        print("fase3")    
        SMTP_Server=smtplib.SMTP(server_address, server_port)    
        print("fase5.1")
        SMTP_Server.starttls()
        print("fase5.2")
        SMTP_Server.login(server_user, server_password)
        print("fase6")
        sender_email="stefano.petrone@falcricrv.org"
        receiver_email="ntgcorp@gmail.com"
        message="From: <stefano.petrone@falcricrv.org>\nTo: <ntgcorp@gmail.com>\nSubject: e-mail test\n\ncorpo test"
        print("fase7")
        SMTP_Server.sendmail(sender_email, receiver_email, message)
        print("fase8")
        SMTP_Server.quit()
        print ("Successfully sent email")
        
# ----------------------------- FUNZIONI -------------------------------------

# True=Valida Email
def NF_StrIsEmail(email):
# Make a regular expression
# for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# pass the regular expression and the string into the fullmatch() method
    return ntSys.iif(re.fullmatch(regex, email),True,False)
