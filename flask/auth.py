
hashedpasslist = []

def hashtime():
    user = flask.request.authorization.username
    hasedpass =  hashlib.pbkdf2_hmac('sha512',flask.request.authorization.password.encode()*3, user.encode()*5,10000).hex()
    return user+':'+hasedpass

def checkusers():
    if flask.request.authorization:
        if hashtime() in hashedpasslist:
            return True
    return False

def loginrequired():
    return "Login Required",401,{'WWW-Authenticate' : 'Basic realm="passrequired"'}
 
# @app.route("/", methods = ['GET'])
if checkusers() == False:
        return loginrequired()
  
# @app.route("/genhash", methods = ['GET'])
def genhash():
    if flask.request.authorization:
        return hashtime()
    return loginrequired()
