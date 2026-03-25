import time
from collections import defaultdict, deque
from starlette.requests import Request
from starlette.responses import Response
from functools import wraps
import asyncio

class FixedWindowRateLimit():
    def __init__(self, max_hits=100, time_period=60, cloudflare=False):
        self.ips = defaultdict(int)
        self.max_hits = max_hits
        self.time_period = time_period
        self.cloudflare = cloudflare
        self.resettime = int(time.time()) + self.time_period

def fixed_window(fixed: FixedWindowRateLimit):
    def worker(func):
        @wraps(func)
        async def wrapper(request : Request, *args, **kwargs):
            if fixed.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.client.host
            else:
                remote_ip = request.client.host

            curtime = int(time.time())
            if fixed.resettime <= curtime:
                fixed.resettime = curtime + fixed.time_period
                fixed.ips.clear()

            fixed.ips[remote_ip] += 1
            if fixed.ips[remote_ip] > fixed.max_hits:
                return Response(status_code=429, headers={'Retry-After': str(fixed.resettime - curtime),
                                                          "Connection": "close"})
            
            return await func(request, *args, **kwargs)
        return wrapper
    return worker

class SlidingWindowRateLimit():
    def __init__(self, max_hits=100, time_period=60, cloudflare=False, old_ip_remove=300):
        self.ips = defaultdict(deque)
        self.max_hits = max_hits
        self.time_period = time_period
        self.cloudflare = cloudflare
        self.old_ip_remove = old_ip_remove
        self.last_ip_remove = int(time.time())

def sliding_window(slide: SlidingWindowRateLimit):
    def worker(func):
        @wraps(func)
        async def wrapper(request : Request, *args, **kwargs):

            if slide.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.client.host
            else:
                remote_ip = request.client.host

            curtime = int(time.time())
            tracklist = slide.ips[remote_ip]

            while tracklist and (tracklist[0] + slide.time_period) < curtime:
                tracklist.popleft()

            if len(tracklist) >= slide.max_hits:
                tryafter = (tracklist[0] + slide.time_period) - curtime
                return Response(status_code=429, headers={'Retry-After': str(tryafter),
                                                            "Connection": "close"})

            tracklist.append(curtime)
            if slide.last_ip_remove + slide.old_ip_remove < curtime:
                slide.last_ip_remove = curtime
                for ip in list(slide.ips.keys()):
                    if slide.ips[ip][-1] + slide.time_period < curtime:
                        del slide.ips[ip]

            return await func(request, *args, **kwargs)
        return wrapper
    return worker

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
    def worker(func):# -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Cor...:
        @wraps(func)
        async def wrapper(request : Request, *args, **kwargs):
            if bucket.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.client.host
            else:
                remote_ip = request.client.host

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
                return Response(status_code=429, headers={'Retry-After': str(retry_in),
                                                          "Connection": "close"})
            count -= 1
            ip_data['count'] = count

            if bucket.last_ip_remove + bucket.old_ip_remove < curtime:
                bucket.last_ip_remove = curtime
                remove_older = curtime - bucket.old_ip_remove
                for ip in list(bucket.ips):
                    if bucket.ips[ip]['lastfill'] < remove_older:
                        del bucket.ips[ip]

            return await func(request, *args, **kwargs)
        return wrapper
    return worker

class LeakyBucketRateLimit():
    def __init__(self, empty_amout = 1, empty_speed = 1, queue_limit=10, cloudflare=False,burst = 0):
        self.empty_amout = empty_amout
        self.empty_speed = empty_speed
        self.queue_limit = queue_limit + burst
        self.cloudflare = cloudflare
        self.burst = burst
        # self.ips = defaultdict(int)
        self.ips = defaultdict(lambda: None)

def leaky_bucket_limit(leaky_bucket: LeakyBucketRateLimit):
    def worker(func):
        @wraps(func)
        async def wrapper(request : Request, *args, **kwargs):

            async def remove_one():
                await asyncio.sleep(leaky_bucket.ips[remote_ip] * leaky_bucket.empty_speed)
                leaky_bucket.ips[remote_ip] -= leaky_bucket.empty_amout
                print('after',leaky_bucket.ips[remote_ip])

            if leaky_bucket.cloudflare:
                remote_ip = request.headers.get(
                    'CF-Connecting-IP', None) or request.client.host
            else:
                remote_ip = request.client.host
            
            count = leaky_bucket.ips[remote_ip]

            async def remove_ip():
                while True:
                    await asyncio.sleep(10)
                    if leaky_bucket.ips[remote_ip] - leaky_bucket.burst <= 0:
                        print('deleting',remote_ip)
                        leaky_bucket.ips.pop(remote_ip)
                        break

            if count is None:
                asyncio.create_task(remove_ip())
                count = 0

            if count > leaky_bucket.queue_limit:
                return Response(status_code=429, headers={'Retry-After': str(leaky_bucket.empty_speed * count),
                                                            "Connection": "close"})
            count += 1
            leaky_bucket.ips[remote_ip] = count
            if count >= leaky_bucket.burst:
                print('before sleep',leaky_bucket.ips[remote_ip])
                asyncio.create_task(remove_one())
                await asyncio.sleep((count - leaky_bucket.burst) * leaky_bucket.empty_speed)
            else:
                print('what?')

            return await func(request, *args, **kwargs)
        return wrapper
    return worker


# def leaky_bucket_limit(leaky_bucket: LeakyBucketRateLimit):
#     def worker(func):
#         @wraps(func)
#         async def wrapper(request : Request, *args, **kwargs):

#             async def remove_one():
#                 await asyncio.sleep(leaky_bucket.empty_speed)
#                 count = leaky_bucket.ips[remote_ip]
#                 count -= leaky_bucket.empty_amout
#                 if count - leaky_bucket.burst == 0:
#                      print('delete')
#                      await asyncio.sleep(10)
#                      if leaky_bucket.ips[remote_ip] - leaky_bucket.burst <= 0:
#                         print('deleting', leaky_bucket.ips[remote_ip])
#                         leaky_bucket.ips.pop(remote_ip,None)
#                      else:
#                         print('failed to delete')
#                 else:
#                     leaky_bucket.ips[remote_ip] = count
#                 print('after',leaky_bucket.ips[remote_ip])

#             if leaky_bucket.cloudflare:
#                 remote_ip = request.headers.get(
#                     'CF-Connecting-IP', None) or request.client.host
#             else:
#                 remote_ip = request.client.host
            
#             count = leaky_bucket.ips[remote_ip]
#             if count > leaky_bucket.queue_limit:
#                 return Response(status_code=429, headers={'Retry-After': str("retry_in"),
#                                                             "Connection": "close"})
#             count += 1
#             leaky_bucket.ips[remote_ip] = count
#             if count > leaky_bucket.burst:
#                 print('before sleep',leaky_bucket.ips[remote_ip])
#                 asyncio.create_task(remove_one())
#                 await asyncio.sleep((count - leaky_bucket.burst -1) * leaky_bucket.empty_speed)
            
#             return await func(request, *args, **kwargs)
#         return wrapper
#     return worker
