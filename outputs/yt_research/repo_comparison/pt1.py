import time, sys, threading, faulthandler
faulthandler.dump_traceback_later(60, exit=True)
from pytubefix import Search
t = time.time()
s = Search("Model Context Protocol architecture")
r = s.videos
print("videos", len(r), round(time.time() - t, 1))
print([(v.video_id, v.title[:40]) for v in r[:3]])
