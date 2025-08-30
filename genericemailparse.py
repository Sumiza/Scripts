
import imaplib
from email.message import MIMEPart
from email.parser import Parser
from email.policy import default

def getemail(username:str,password:str,domain:str): 

    M = imaplib.IMAP4_SSL(host=domain)
    M.login(username, password)
    M.select()
    _, data = M.fetch('1', '(RFC822)')

    email:MIMEPart = Parser(policy=default).parsestr(data[0][1].decode('utf8', errors='replace'))

    def payload(part):
        body = email.get_body(preferencelist=(part))
        if body:
            return str(body.get_payload(decode=False))
        return None

    builddict = {}

    builddict['to'] = email.get('to')
    builddict['from'] = email.get('from')
    builddict['bodyplain'] = payload('plain')
    builddict['bodyhtml'] = payload('html')
    builddict['subject'] = email.get('subject')
    builddict['date'] = email.get('date')

    M.store('1', '+FLAGS', '\\Deleted')

    M.close()
    M.logout()

    return builddict
