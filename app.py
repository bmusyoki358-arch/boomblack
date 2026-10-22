import os, uuid, threading
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__)
progress = {}
FOLDER = "/tmp"
COOKIE_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_opts(outtmpl=None, hooks=None):
    o = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android','ios','web']}},
    }
    if COOKIE_FILE:
        o['cookiefile'] = COOKIE_FILE
    if outtmpl:
        o['outtmpl'] = outtmpl
    if hooks:
        o['progress_hooks'] = hooks
    return o

@app.route("/")
def home():
    has_cookie = "YES ✅ YouTube Ready" if COOKIE_FILE else "NO ❌ Upload cookies.txt for YouTube"
    return f"""
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{background:black;color:white;font-family:Arial;text-align:center;padding:10px}}
h1{{color:gold;text-shadow:0 0 10px gold}}
.box{{background:#111;border:2px solid gold;border-radius:15px;padding:20px;max-width:600px;margin:auto}}
input{{width:95%;padding:15px;border-radius:10px;border:none;font-size:18px}}
button{{width:95%;padding:15px;margin:15px 0;background:gold;color:black;font-weight:bold;font-size:20px;border:none;border-radius:10px}}
#bar{{background:#333;height:30px;border-radius:10px;overflow:hidden;margin-top:15px}}
#fill{{background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px;font-weight:bold;transition:0.3s}}
a.save{{background:green;color:white;padding:15px;display:block;margin-top:15px;text-decoration:none;font-size:20px;border-radius:10px}}
</style>
</head>
<body>
<h1>BOOM BLACK 🔥</h1>
<p>TikTok | YouTube | Facebook | Instagram</p>
<p style="font-size:12px;color:gold">{has_cookie}</p>
<div class="box">
<input id="u" placeholder="Paste ANY video link here...">
<button onclick="go()">⚡ DOWNLOAD VIDEO</button>
<div id="bar"><div id="fill">0%</div></div>
<p id="t"></p>
<div id="r"></div>
</div>
<script>
let myid=null;
function go(){{
 let url=document.getElementById('u').value;
 if(!url){{alert('Paste link');return;}}
 document.getElementById('fill').style.width='5%';
 document.getElementById('t').innerText='Starting...';
 fetch('/start?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{{myid=d.id; check();}});
}}
function check(){{
 fetch('/progress/'+myid).then(r=>r.json()).then(d=>{{
  document.getElementById('fill').style.width=d.p+'%';
  document.getElementById('fill').innerText=d.p+'%';
  document.getElementById('t').innerText=d.s;
  if(d.f){{
   document.getElementById('r').innerHTML='<a class="save" href="/get/'+d.f+'" download>✅ CLICK TO SAVE VIDEO TO PHONE</a>';
  }} else if(d.u){{
   document.getElementById('r').innerHTML='<a class="save" href="'+d.u+'" target="_blank">✅ CLICK TO SAVE</a>';
  }} else if(!d.e){{
   setTimeout(check,800);
  }} else {{
   document.getElementById('t').innerText='Error: '+d.e;
  }}
 }});
}}
</script>
</body>
</html>
"""

@app.route("/start")
def start():
    url = request.args.get('url','')
    did = str(uuid.uuid4())[:8]
    progress[did] = {'p':0,'s':'Starting...','f':None,'u':None,'e':None}
    def run():
        try:
            def h(d):
                if d['status']=='downloading':
                    tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    cur = d.get('downloaded_bytes',0)
                    pct = int(cur*100/tot) if tot>0 else 0
                    progress[did]['p']=pct
                    progress[did]['s']=f'Downloading {pct}%'
                elif d['status']=='finished':
                    progress[did]['s']='Processing...'
            opts = get_opts(f'{FOLDER}/%(title)s_{did}.%(ext)s', [h])
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                fn = ydl.prepare_filename(info)
                # find actual file (may be mp4 after merge)
                base = os.path.basename(fn)
                # check if merged file exists
                if not os.path.exists(f"{FOLDER}/{base}"):
                    # find file with same did
                    for f in os.listdir(FOLDER):
                        if did in f:
                            base=f
                            break
                progress[did]['f']=base
                progress[did]['p']=100
                progress[did]['s']='Done! Click green button'
        except Exception as e:
            progress[did]['e']=str(e)[:500]
            progress[did]['s']='Failed'
    threading.Thread(target=run).start()
    return jsonify({'id':did})

@app.route("/progress/<did>")
def prog(did):
    return jsonify(progress.get(did,{'p':0,'s':'waiting'}))

@app.route("/get/<name>")
def getf(name):
    return send_from_directory(FOLDER, name, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
