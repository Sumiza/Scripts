import socket
def amionlinedns(hostlist:list = ["1.1.1.1","8.8.8.8","9.9.9.9"]):
    """
    Returns True if can connect to any of the dns server in hostlist.
    Returns False if cant connect.
    Args:
        hostlist:list default is cloudflare, google, quad9
    """
    for host in hostlist:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.settimeout(5)
            response = so.connect_ex((host,53))
            if response == 0:
                return True
    return False
