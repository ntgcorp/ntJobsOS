# 
# Test Send Mail with attachment
#
import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "test_falcricrv@falcricrv.org"
APP_PASSWORD = "Test1,"

def send_mail_with_attach(recipient_email, subject, content, typefile, attach_file):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(content)

    with open(attach_file, 'rb') as f:
        file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype=typefile, filename=excel_file)

    with smtplib.SMTP_SSL('smtp.aruba.it', 25) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
        
send_mail_with_attach("ntgcorp@gmail.com","Subject Text","Body Text","xlsx","ntSys.py")        