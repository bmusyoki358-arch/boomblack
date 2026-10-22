import os, uuid, threading, glob
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__)
progress = {}
FOLDER = "/tmp"
COOKIE_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_opts(outtmpl=None, hooks=None):
    # NO FORMAT - Let YouTube choose whatever exists
    o = {
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
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
    files = [os.path.basename(f) for f in glob.glob(f"{FOLDER}/*.*") if os.path.getsize(f) > 1000][:20]
    files_html = ""
    for f in files:
        files_html += f'<div style="background:#222;padding:10px;margin:10px;border-radius:10px"><video src="/get/{f}" controls style="width:100%;max-height:200px;border-radius:10px"></video><p style="font-size:12px">{f[:40]}</p><a href="/get/{f}" download style="background:gold;color:black;padding:8px;display:block;text-decoration:none;border-radius:5px">DOWNLOAD</a></div>'
    if not files_html:
        files_html = "<p style='color:#777'>No downloads yet</p>"

    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="background:black;color:white;text-align:center;padding:15px;font-family:Arial">
<h1 style="color:gold">BOOM BLACK 🔥 V4</h1>
<p>Cookie: {has_cookie} | <a href="#downloads" style="color:gold">My Downloads ({len(files)})</a></p>
<input id="u" style="width:95%;padding:15px;border-radius:10px;border:none;font-size:18px" placeholder="Paste YouTube / TikTok link">
<br><br>
<button onclick="go()" style="width:95%;padding:15px;background:gold;color:black;font-weight:bold;font-size:20px;border:none;border-radius:10px">DOWNLOAD VIDEO</button>
<div style="margin-top:20px;background:#333;height:30px;border-radius:10px;overflow:hidden"><div id="b" style="background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px;font-weight:bold">0%</div></div>
<p id="t"></p>
<div id="r"></div>
<hr style="margin:30px 0;border-color:#333">
<h2 id="downloads">📁 YOUR DOWNLOADS</h2>
<button onclick="location.reload()" style="padding:8px 15px;background:#333;color:white;border:1px solid gold;border-radius:5px">Refresh Gallery</button>
<div style="max-width:600px;margin:auto">{files_html}</div>
<script>
let myid=null;
function go(){{
 let url=document.getElementById('u').value;
 if(!url){{alert('Paste link');return;}}
 document.getElementById('t').innerText='Starting...';
 fetch('/start?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{{myid=d.id;check();}});
}}
function check(){{
 fetch('/progress/'+myid).then(r=>r.json()).then(d=>{{
  document.getElementById('b').style.width=d.p+'%';
  document.getElementById('b').innerText=d.p+'%';
  document.getElementById('t').innerText=d.s;
  if(d.f){{
   document.getElementById('r').innerHTML='<div style="background:#111;padding:10px;border-radius:10px"><video src="/get/'+d.f+'" controls style="width:100%;border-radius:10px"></video><a href="/get/'+d.f+'" download style="background:green;color:white;padding:15px;display:block;margin-top:10px;text-decoration:none;border-radius:10px;font-size:20px">✅ PLAY & SAVE TO PHONE</a></div>';
  }} else if(!d.e){{
   setTimeout(check,800);
  }} else {{
   document.getElementById('t').innerText='Error: '+d.e;
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
        last = "Unknown"
        try:
            def h(d):
                if d['status']=='downloading':
                    tot = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    cur = d.get('downloaded_bytes',0)
                    pct = int(cur*100/tot) if tot>0 else 0
                    progress[did]['p']=pct
                    progress[did]['s']=f'Downloading {pct}%'
            opts = get_opts(f'{FOLDER}/%(title)s_{did}.%(ext)s',[h])
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
                progress[did]['s']='Done! Watch below'
                return
        except Exception as e:
            last = str(e)
        progress[did]['e']=last[:500]
        progress[did]['s']='Failed'
    threading.Thread(target=run).start()
    return jsonify({'id':did})

@app.route("/progress/<did>")
def prog(did):
    return jsonify(progress.get(did,{'p':0,'s':'wait'}))

@app.route("/get/<name>")
def getf(name):
    return send_from_directory(FOLDER, name, as_attachment=False)

if __name__=="__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
