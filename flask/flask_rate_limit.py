
import time
from flask import request, Response
from collections import defaultdict

#@fixed_window(FixedWindowRateLimit(80000,60,True))
#from flask_rate_limit import FixedWindowRateLimit, fixed_window

class FixedWindowRateLimit():
    def __init__(self, max_hits=100, time_period=60, cloudflare=False):
        self.ips = defaultdict(int)
        self.max_hits = max_hits
        self.time_period = time_period
        self.cloudflare = cloudflare
        self.resettime = int(time.time()) + self.time_period


def fixed_window(fixed: FixedWindowRateLimit):
    def decorator(func):
        def worker(*args, **kwargs):
            if fixed.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.remote_addr
            else:
                remote_ip = request.remote_addr

            curtime = int(time.time())
            if fixed.resettime <= curtime:
                fixed.resettime = curtime + fixed.time_period
                fixed.ips.clear()

            fixed.ips[remote_ip] += 1
            if fixed.ips[remote_ip] > fixed.max_hits:
                return Response(
                    f'Rate limit hit for {remote_ip}, try again in {fixed.resettime - curtime} seconds.', 429)

            return func(*args, **kwargs)
        return worker
    return decorator
