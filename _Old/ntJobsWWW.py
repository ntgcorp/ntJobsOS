#ntJobsPy: FrontEnd WWW
#Librerie esterne richieste: bottle, 
import bottle
import os, datetime
import ntJ_Lib

# Variabili interne
sCharset="iso"

# Test
@route('/sys_test')
def sys_test():
    return "ntJobs Web Server FrontEnd: Test"  

# Riceve un  e lo salva come file jobs_id.ini
@route('/job_send/<api.kei>/<cmd>/')
def job_send():
    return "ntJobs Web Server: Send Job"

@error(404)
def error404(error):
    return 'ntJobsPy Web Server - Errore comando sconosciuto'

@route('/restricted')
def restricted():
    abort(401, "ntJobsPy: Sorry, access denied.")
    
# System info
@route('/sys_info')
def sysinfo():
    print ("CURDIR: " & os.getcwd())
    @route('/my_ip')
def show_ip():
    ip = request.environ.get('REMOTE_ADDR')
    # or ip = request.get('REMOTE_ADDR')
    # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)

# ---------------- Charset -------------------
@route('/iso')
def get_iso():
    response.charset = 'ISO-8859-15'
    sCharset="iso"
    return u'This will be sent with ISO-8859-15 encoding.'

@route('/latin9')
def get_latin():
    sCharset="latin"
    response.content_type = 'text/html; charset=latin9'
    return u'ISO-8859-15 is also known as latin9.'
   
# --------------------- Start Web Server -------------------------
run(host='localhost', port=8080, debug=True)
    