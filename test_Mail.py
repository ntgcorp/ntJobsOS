#
# TEST LIBRARY
# ntJob Framework
#
import nlSys, nlDataFiles
import ssl, smtplib
import sys
from ntMailClass import NC_Mail

NT_ENV_TEST_TBASE=True
    
# Vari test invio mail
def TEST_Mail(sTest):
    sProc="TEST_MAIL"
    sResult=""

# TEST SINGOLA MAIL DI TESTO
# Porta viene controllata,  SSL deve essere boolena                                 
    if sTest=="SIMPLE":
        dictMail = {'TO': "ntgcorp@gmail.com",
                    'CC': "stefano.petrone@falcricrv.org",
                    'FROM': "stefano.petrone@falcricrv.org",
                    'CHANNEL': "SMTP",
                    'FORMAT': "TXT",
                    'BODY': "Testo",
                    'SUBJECT': "Soggetto",
                    'SMTP.SERVER': "smtp.falcricrv.org",
                    'SMTP.USER': "stefano.petrone@falcricrv.org",
                    'SMTP.PASSWORD': "sp",
                    'SMTP.PORT': 25,
                    'SMTP.SSL': False,
                    }
# Invio Mail        
        objMail=NC_MailClass(dictMail)        
        sResult = objMail.sResult
        #objMail.test1()
        if (sResult==""): sResult=objMail.MAIL_MailSend()

# Ritorno
    print (nlSys.NF_StrTestResult(sResult,sProc))
    
    
def main():

    TEST_Mail("SIMPLE")
    
# Fine
    print("Fine dei test")
    sys.exit()
    
# Start Default Python code
if __name__=="__main__":
    main()    
    