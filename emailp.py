a = """From root@a1.local.tld Thu Jul 25 19:28:59 2013
Received: from a1.local.tld (localhost [127.0.0.1])
    by a1.local.tld (8.14.4/8.14.4) with ESMTP id r6Q2SxeQ003866
    for <ooo@a1.local.tld>; Thu, 25 Jul 2013 19:28:59 -0700
Received: (from root@localhost)
    by a1.local.tld (8.14.4/8.14.4/Submit) id r6Q2Sxbh003865;
    Thu, 25 Jul 2013 19:28:59 -0700
From: root@a1.local.tld
Subject: oooooooooooooooo
To: ooo@a1.local.tld
Cc: 
X-Originating-IP: 192.168.15.127
X-Mailer: Webmin 1.420
Message-Id: <1374805739.3861@a1>
Date: Thu, 25 Jul 2013 19:28:59 -0700 (PDT)
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="bound1374805739"

This is a multi-part message in MIME format.

--bound1374805739
Content-Type: text/plain
Content-Transfer-Encoding: 7bit

ooooooooooooooooooooooooooooooooooooooooooooooo
ooooooooooooooooooooooooooooooooooooooooooooooo
ooooooooooooooooooooooooooooooooooooooooooooooo

--bound1374805739--"""

# a = """From example@email.com Thu Jul 25 19:28:59 2013
# Received: from email.com (localhost [XXX.X.X.X])
#     by email.com (X.XX.X/X.XX.X) with ESMTP id r6Q2SxeQ003866
#     for <send_example@gmail.com>;  Day, DD MM YYYY HH:MM:SS -TTTT
# From: example@email.com
# Subject: Subject Title
# To: send_example@email.com
# Cc: 
# X-Originating-IP: XXX.XXX.XX.XXX
# Message-Id: <id@email>
# Date: Day, DD MM YYYY HH:MM:SS -TTTT (PDT)
# MIME-Version: 1.0
# Content-Type: multipart/mixed; boundary="bound1374805739"

# This is a multi-part message in MIME format.

# --bound1374805739
# Content-Type: text/plain
# Content-Transfer-Encoding: 7bit

# I am the body of an email. 

# --bound1374805739--"""


import email

b = email.message_from_string(a)
# body = b.get_payload(decode=True)
print(b.__dict__)
print(b.get_all('from'))
print(b.get('from'))
print(b.get('to'))
print(b.get('subject'))
# print(b.get('payload'))
# print(b.is_multipart())
# print(b.get_payload())
# b = email.message_from_string(email)
for payload in b.get_payload():
    print(payload.get_payload().strip())

# body = ''
# print(body)
# if b.is_multipart():
#    for part in b.walk():
#        ctype = part.get_content_type()
#        cdispo = str(part.get('Content-Disposition'))

#        # skip any text/plain (txt) attachments
#        if ctype == 'text/plain' and 'attachment' not in cdispo:
#            body = part.get_payload(decode=True)  # decode
#            break
# # not multipart - i.e. plain text, no attachments
# else:
#     body = b.get_payload(decode=True)

# print(body.decode())