

allowedhosts = ["test.example.com","other.example.com"]

def checkip():
    for hostname in allowedhosts:
        try:
            ip = socket.gethostbyname(hostname)
            if ip == flask.request.remote_addr or ip == flask.request.headers['X-Forwarded-For']:
                return True
        except:
            pass
    return False

  # @app.route("/", methods = ['GET'])
  if checkip() == False:
        return "Not Allowed", 403, {'Content-Type': 'text/plain; charset=utf-8'}
