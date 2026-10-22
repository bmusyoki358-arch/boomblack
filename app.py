import os, requests
from flask import Flask, request, send_from_directory, render_template_string, jsonify
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
download_status = {"status": "idle", "percent": "0%", "speed": "", "title": ""}

def progress_hook(d):
    global download_status
    if d['status'] == 'downloading':
        download_status['status']='downloading'
        download_status['percent']=d.get('_percent_str','0%').strip()
        download_status['speed']=d.get('_speed_str','')
        try: download_status['title']=d.get('info_dict',{}).get('title','')[:60]
        except: pass
    elif d['status']=='finished':
        download_status['status']='finished'
        download_status['percent']='100%'

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>BOOM BLACK</title><style>body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:15px}input{width:70%;padding:14px;border-radius:12px;border:none}button{padding:14px 20px;background:red;color:#fff;border:none;border-radius:12px;font-weight:bold}#barBg{width:100%;background:#333;height:22px;border-radius:10px;overflow:hidden}#bar{width:0%;height:100%;background:linear-gradient(90deg,red,orange)}.video{background:#111;margin:12px auto;padding:10px;border-radius:12px;max-width:400px}video{width:100%;border-radius:8px}</style></head><body><h1>BOOM BLACK V9 - BOT BYPASS</h1><form method="POST"><input name="url" placeholder="Paste YouTube link" required><button>DOWNLOAD</button></form><p style="color:#0f0">{{ msg }}</p><p style="color:orange;font-size:12px">Cookies found: {{ cookie_info }}</p><hr><h2>Gallery</h2>{% for f in files %}<div class="video">{{ f }}<br><video controls><source src="/downloads/{{ f }}"></video><br><a href="/downloads/{{ f }}" download style="color:red">⬇ Download</a></div>{% endfor %}</body></html>"""

def download_backup(url):
    try:
        # Cobalt API - no cookies needed!
        r = requests.post("https://api.cobalt.tools/api/json", json={"url": url, "vCodec":"h264","vQuality":"720"}, headers={"Accept":"application/json","Content-Type":"application/json"}, timeout=20)
        j = r.json()
        print(f"Cobalt response: {j}")
        if j.get('url'):
            file_url = j['url']
            fname = f"{DOWNLOAD_FOLDER}/video_{os.urandom(3).hex()}.mp4"
            with requests.get(file_url, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(fname,'wb') as f:
                    for chunk in resp.iter_content(8192): f.write(chunk)
            return True
    except Exception as e: print(f"Backup failed: {e}")
    return False

@app.route("/", methods=["GET","POST"])
def home():
    msg=""
    cookie_info = f"exists={os.path.exists('cookies.txt')} size={os.path.getsize('cookies.txt') if os.path.exists('cookies.txt') else 0}"
    if request.method=="POST":
        url=request.form.get("url","").strip()
        tried_backup=False
        try:
            # MAIN: try with android client - bypasses bot often WITHOUT cookies
            opts = {
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                'format': 'best',
                'noplaylist': True,
                'progress_hooks': [progress_hook],
                'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
                'nocheckcertificate': True,
                'geo_bypass': True,
            }
            if os.path.exists('cookies.txt'):
                opts['cookiefile'] = 'cookies.txt'
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            msg="✅ Downloaded via YouTube!"
        except Exception as e:
            err=str(e)
            print(f"YT fail: {err}")
            if "bot" in err.lower() or "Sign in" in err:
                msg="⚠️ YouTube blocked, trying backup engine..."
                if download_backup(url):
                    msg="✅ Downloaded via BACKUP ENGINE! (Bypassed bot)"
                else:
                    msg=f"❌ Bot blocked. Fix: 1) Logout/login youtube 2) Export ALL cookies 3) Paste. Error: {err[:200]}"
            else:
                msg=f"❌ {err[:300]}"
    files=sorted(os.listdir(DOWNLOAD_FOLDER), reverse=True) if os.path.exists(DOWNLOAD_FOLDER) else []
    return render_template_string(HTML, msg=msg, files=files, cookie_info=cookie_info)

@app.route("/downloads/<path:filename>")
def dl(filename): return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
