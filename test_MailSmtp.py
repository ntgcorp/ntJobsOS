
# Test 1..3
import smtplib, ssl



# Test 4..7
from ntMailClass import NC_Mail
import ntDataFiles, ntSys

# Per Test UrlLib
import urllib.request

# Per Test 4
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def Test_urllib_get_2018():
    # Using a protected member like this is not any more fragile
    # than extending the class and using it. I would use it.
    url = 'https://localhost:6667/my-endpoint'
    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen(url = url) as f:
        print(f.read().decode('utf-8'))

def Test_urllib_get_2022():
    # Finally! Able to use the publice API. Happy happy!
    url = 'https://localhost:6667/my-endpoint'
    scontext = ssl.SSLContext(ssl.PROTOCOL_TLS)
    scontext.verify_mode = ssl.VerifyMode.CERT_NONE
    with urllib.request.urlopen(url = url, context=scontext) as f:
        print(f.read().decode('utf-8'))

# ----------------------- LOGIN

def test1():
    # TEST o 

    server_user = "stefano.petrone@falcricrv.org"
    server_password = "sp"
    server_address="smtp.falcricrv.org"
    server_port=25

#context = ssl.create_default_context()
    #print("fase1")
    #ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL
    #context = ssl._create_unverified_context()
    #print("fase2")
    #context = ssl.create_default_context()
    print("fase3")
    #server=smtplib.SMTP_SSL(server_address, server_port, context=context)
    #server=smtplib.SMTP(server_address, server_port, context=context)
    server=smtplib.SMTP(server_address, server_port)
    #print("fase4")
    #server=smtplib.ehlo()
    print("fase5.1")
    server.starttls()
    print("fase5.2")
    server.login(server_user, server_password)

# ------------------------ MESSAGE
    print("fase6")
    sender_email="stefano.petrone@falcricrv.org"
    receiver_email="ntgcorp@gmail.com"
#server.sendmail(sender_email, receiver_email, message)
    
    message="""From: FromPerson <stefano.petrone@falcricrv.org>
    To: ntgcorp@gmail.com
    MIME-Version: 1.0
    Content-type: text/html    
    Subject: e-mail test    
    Body
    """    
    
    message = """From: FromPerson <stefano.petrone@falcricrv.org>
    SMTP HTML e-mail test    
    Bodydcdscdscsdcsdcdscsdcdscsdcsdcdscsdcsdcdscsd
    """
    message="From: <stefano.petrone@falcricrv.org>\nTo: <ntgcorp@gmail.com>\nSubject: e-mail test\n\ncorpo test"
    
    
    print("fase7")
    server.sendmail(sender_email, receiver_email, message)
    print("fase8")
    server.quit()
    print ("Successfully sent email")

    
def test2():
    
    # Import smtplib for the actual sending function
    import smtplib

# Import the email modules we'll need
    from email.message import EmailMessage

    msg = EmailMessage()
    msg.set_content("test")

# me == the sender's email address
# you == the recipient's email address
    msg['Subject'] = f'The contents of file'
    msg['From'] = "stefano.petrone@falcricrv.org"
    msg['To'] = "ntgcorp@gmail.com"

# Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    

def test3():

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "ntgcorp@gmail.com"
    password = input("Type your password and press enter: ")

# Create a secure SSL context
    context = ssl.create_default_context()

# Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
    # TODO: Send email here
    except Exception as e:
    # Print any error messages to stdout
        print("Except:" + str(e))

    receiver_email="ntgcorp@gmail.com"
    message="test"
    server.sendmail(sender_email, receiver_email, message)
    server.quit
    
def test4():    
    server_user = "stefano.petrone@falcricrv.org"
    server_password = "sp"
    server_address="smtp.falcricrv.org"
    server_port=25
    
    print("Fase1")
    msg = MIMEMultipart()
    print("Fase2")
    msg["Subject"] = "MIME Example"
    msg["From"] = "stefano.petrone@falcricrv.org"
    msg["To"] = "ntgcorp@gmail.com,ntgeshop@gmail.com,stefano.petrone@intesasanpaolo.com"
    msg["Cc"] = "reciter2@hotmail.com"
    print("Fase3")
    body = MIMEText("example email body")
    print("Fase4")
    msg.attach(body)
    print("fase5.1")
    server=smtplib.SMTP(server_address, server_port)
    #print("fase4")
    #server=smtplib.ehlo()
    print("fase5.2")
    server.starttls()
    print("fase5.3")
    server.login(server_user, server_password)
    print("Fase6")
    server.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    print("Fase7")
    server.quit()
    print("Test concluso")
    
# -------------------------------- TEST NC_MAIL -------------------------------------

def test5():
    
    dictMail={
        "SMTP.SERVER": "smtp.falcricrv.org", 
        "SMTP.USER": "stefano.petrone@falcricrv.org",
        "SMTP.PASSWORD": "sp",
        "CHANNEL": "SMTP",
        "SMTP.PORT": 25,
        "SMTP.SSL":False,
        "FROM": "stefano.petrone@falcricrv.org",
        "FORMAT":"TXT",
        "FILE.IN": "Temp/Test_ntMail.csv",
        "TO":"",
        "SUBJECT":"",
        "CC":"",
        "BCC":"",
        "ATTACH":"",
        "BODY":"",
        "BODY.FILE":"Temp/Body_demo.txt",
        "F1":"",
        "F2":"",
        "F3":"",
        "ATTR":""        
    }
    
    # Test Smtp Mail
    print("Test SMTP MAIL")
    objMail=NC_Mail(dictMail)
    
    # Test TXT->NO_ATTACH->
    sResult=objMail.sResult
 
    # Parameter
    if sResult=="": objMail.MailParams(dictMail)
    
    # Legge CSV
    if sResult=="":
        sFileCSV=dictMail["FILE.IN"]
        lResult=ntSys.NF_PathNormal(sFileCSV)
        if sResult=="":
            sFileCSV=lResult[5]
            sResult=CSV_Read(sFileCSV)
    
    # Send CSV
    if sResult=="": sResult=objMail.MailSendCSV()
    print("Test TXT->NO_ATTACH->CSV: " + sResult)
    
    # Test HTML->NO_ATTACH->CSV
    dictMail["FORMAT"]="HTML"
    sResult=objMail.MailParams(dictMail)
    if sResult=="": sResult=objMail.MailSendCSV()
    print("Test HTM->NO_ATTACH->CSV: " + sResult)
    
    # End Session
    if objMail.bLogin: objMail.MailSmtpQuit()
    
# ----------------------------------------- MAIN ------------------------------------

#test1()

# ------------- NC_MAIL -------------------

# Legge CSV e ritorna lResult(sResult,dictCSV)
def CSV_Read(sFileCSV):
    sProc="CSV_Read"
# Estrae File CSV di spedizione
# Ritorno lResult 0=sResult, 1=dictCSV
    sResult=""
    
# Legge CSV Mail da spedire
# Params: FILE.IN=CSV, FIELDS=Array che ci deve essere, CSV.DELIMITER=Delimiter campi, CSV.TRIM=Trim Prima e dopo. CSV.QUOTE=Campo delimitatore testi
    if (sResult=="") and (sFileCSV!=""):
        dictParams={'FILE.IN': sFileCSV,
                    'FIELDS': asFMT_MAIL_HDR,
                    'DELIMITER': NTM_dictINI.get("CSV.DELIMITER",ntDataFiles.sCSV_DELIMITER),
                    'TRIM': NTM_dictINI.get("CSV.TRIM",True),
                    'QUOTE': NTM_dictINI.get("CSV.QUOTE", ntDataFiles.sCSV_QUOTE)}
        lResult=ntDataFiles.NF_CSV_Read(dictParams)
        sResult=lResult[0]
        nRecords=lResult[3]
        ntSys.NF_DebugFase(NT_ENV_TEST_MAIL, "Lettura CSV. File=" + dictParams["FILE.IN"] + ", Righelette=" + str(nRecords) + ", Status=" + sResult, sProc)        
    else:
        lResult=[sResult,[]]
        
# Ritorno
    return lResult

test5()    
    
