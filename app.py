import os, uuid, threading
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__)
progress = {}
FOLDER = "/tmp"
COOKIE_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_opts(outtmpl=None, hooks=None):
    o = {
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
    has_cookie = "YES ✅" if COOKIE_FILE else "NO ❌"
    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="background:black;color:white;text-align:center;padding:15px;font-family:Arial">
<h1 style="color:gold">BOOM BLACK 🔥</h1>
<p>Cookie: {has_cookie} | TikTok YouTube FB Insta</p>
<input id="u" style="width:95%;padding:15px;border-radius:10px;border:none;font-size:18px" placeholder="Paste video link">
<br><br>
<button onclick="go()" style="width:95%;padding:15px;background:gold;color:black;font-weight:bold;font-size:20px;border:none;border-radius:10px">DOWNLOAD VIDEO</button>
<div style="margin-top:20px;background:#333;height:30px;border-radius:10px;overflow:hidden">
<div id="b" style="background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px;font-weight:bold">0%</div>
</div>
<p id="t"></p>
<div id="r"></div>
<script>
let myid=null;
function go(){{
 let url=document.getElementById('u').value;
 if(!url){{alert('Paste link');return;}}
 fetch('/start?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{{myid=d.id;check();}});
}}
function check(){{
 fetch('/progress/'+myid).then(r=>r.json()).then(d=>{{
  document.getElementById('b').style.width=d.p+'%';
  document.getElementById('b').innerText=d.p+'%';
  document.getElementById('t').innerText=d.s;
  if(d.f){{
   document.getElementById('r').innerHTML='<a href="/get/'+d.f+'" download style="background:green;color:white;padding:15px;display:block;margin-top:15px;text-decoration:none;border-radius:10px;font-size:20px">✅ SAVE TO PHONE</a>';
  }} else if(!d.e){{
   setTimeout(check,800);
  }} else {{
   document.getElementById('t').innerText=d.e;
  }}
 }});
}}
</script>
</body></html>
"""

@app.route("/start")
def start():
    url = request.args.get('url','')
    did = str(uuid.uuid4())[:8]
    progress[did] = {'p':0,'s':'Starting...','f':None,'e':None}
    def run():
        last = "Unknown error"
        for fmt in ['bestvideo+bestaudio/best','best','worst',None]:
            try:
                def h(d):
                    if d['status']=='downloading':
                        tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                        cur = d.get('downloaded_bytes',0)
                        pct = int(cur*100/tot) if tot>0 else 0
                        progress[did]['p']=pct
                        progress[did]['s']=f'Downloading {pct}%'
                opts = get_opts(f'{FOLDER}/%(title)s_{did}.%(ext)s',[h])
                if fmt:
                    opts['format']=fmt
                else:
                    opts.pop('format',None)
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    fn = ydl.prepare_filename(info)
                    base = os.path.basename(fn)
                    if not os.path.exists(f"{FOLDER}/{base}"):
                        for f in os.listdir(FOLDER):
                            if did in f:
                                base=f
                                break
                    progress[did]['f']=base
                    progress[did]['p']=100
                    progress[did]['s']='Done!'
                    return
            except Exception as e:
                last = str(e)
                continue
        progress[did]['e']=last[:500]
        progress[did]['s']='Failed: '+last[:200]
    threading.Thread(target=run).start()
    return jsonify({'id':did})

@app.route("/progress/<did>")
def prog(did):
    return jsonify(progress.get(did,{'p':0,'s':'wait'}))

@app.route("/get/<name>")
def getf(name):
    return send_from_directory(FOLDER,name,as_attachment=True)

if __name__=="__main__":
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
