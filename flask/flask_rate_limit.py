import time
from flask import request, Response
from collections import defaultdict, deque

# @fixed_window(FixedWindowRateLimit(60,60,True))
# from flask_rate import FixedWindowRateLimit, fixed_window

class FixedWindowRateLimit():
    def __init__(self, max_hits=100, time_period=60, cloudflare=False):
        self.ips = defaultdict(int)
        self.max_hits = max_hits
        self.time_period = time_period
        self.cloudflare = cloudflare
        self.resettime = int(time.time()) + self.time_period


class SlidingWindowRateLimit():
    def __init__(self, max_hits=100, time_period=60, cloudflare=False, old_ip_remove=300):
        self.ips = defaultdict(deque)
        self.max_hits = max_hits
        self.time_period = time_period
        self.cloudflare = cloudflare
        self.old_ip_remove = old_ip_remove
        self.last_ip_remove = int(time.time())


class BucketRateLimit():
    def __init__(self, fill_amount=10, fill_time=10, bucket_limit=100, cloudflare=False, start_count=50, old_ip_remove=300):
        self.fill_amount = fill_amount
        self.fill_time = fill_time
        self.cloudflare = cloudflare
        self.start_count = start_count
        self.bucket_limit = bucket_limit
        self.old_ip_remove = old_ip_remove
        self.last_ip_remove = int(time.time())

        def ips_build():
            return {'lastfill': int(time.time()), 'count': self.start_count}
        self.ips = defaultdict(ips_build)


def bucket_limit(bucket: BucketRateLimit):
    def decorator(func):
        def bucket_worker(*args, **kwargs):
            if bucket.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.remote_addr
            else:
                remote_ip = request.remote_addr

            curtime = int(time.time())
            ip_data = bucket.ips[remote_ip]
            lastfill = ip_data['lastfill']
            count = ip_data['count']

            fill_times = (curtime - lastfill) // bucket.fill_time
            if fill_times > 0:

                count += bucket.fill_amount * fill_times
                if count > bucket.bucket_limit:
                    count = bucket.bucket_limit

                lastfill += bucket.fill_time * fill_times

            ip_data['lastfill'] = lastfill

            if count <= 0:
                retry_in = bucket.fill_time - (curtime - lastfill)
                if retry_in < 1:
                    retry_in = 1
                return Response(status=429, headers={'Retry-After': retry_in})

            count -= 1
            ip_data['count'] = count

            if bucket.last_ip_remove + bucket.old_ip_remove < curtime:
                bucket.last_ip_remove = curtime
                remove_older = curtime - bucket.old_ip_remove
                for ip in list(bucket.ips):
                    if bucket.ips[ip]['lastfill'] < remove_older:
                        del bucket.ips[ip]

            return func(*args, **kwargs)
        return bucket_worker
    return decorator


def sliding_window(slide: SlidingWindowRateLimit):
    def decorator(func):
        def sliding_worker(*args, **kwargs):

            if slide.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.remote_addr
            else:
                remote_ip = request.remote_addr

            curtime = int(time.time())
            tracklist = slide.ips[remote_ip]

            while tracklist and (tracklist[0] + slide.time_period) < curtime:
                tracklist.popleft()

            if len(tracklist) >= slide.max_hits:
                tryafter = (tracklist[0] + slide.time_period) - curtime
                return Response(status=429, headers={'Retry-After': tryafter})

            tracklist.append(curtime)
            if slide.last_ip_remove + slide.old_ip_remove < curtime:
                slide.last_ip_remove = curtime
                for ip in list(slide.ips.keys()):
                    if slide.ips[ip][-1] + slide.time_period < curtime:
                        del slide.ips[ip]

            return func(*args, **kwargs)
        return sliding_worker
    return decorator


def fixed_window(fixed: FixedWindowRateLimit):
    def decorator(func):
        def fixed_worker(*args, **kwargs):
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
                return Response(status=429, headers={'Retry-After': fixed.resettime - curtime})

            return func(*args, **kwargs)
        return fixed_worker
    return decorator
