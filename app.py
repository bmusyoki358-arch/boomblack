import os, uuid, threading
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
app = Flask(__name__)
progress = {}
FOLDER = "/tmp"
COOKIE_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_opts(outtmpl=None, hooks=None):
    o = {
        'format': 'best[height<=720]/best',
        'noplaylist': True,
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android','ios','web']}},
    }
    if COOKIE_FILE: o['cookiefile'] = COOKIE_FILE
    if outtmpl: o['outtmpl'] = outtmpl
    if hooks: o['progress_hooks'] = hooks
    return o

@app.route("/")
def home():
    has_cookie = "YES ✅" if COOKIE_FILE else "NO ❌ - Upload cookies.txt for YouTube"
    return f"""
<html><body style='background:black;color:gold;text-align:center;padding:20px;font-family:Arial'>
<h1>BOOM BLACK 🔥</h1>
<p>Cookie: {has_cookie}</p>
<input id='u' style='width:90%;padding:15px;font-size:18px' placeholder='Paste link'>
<br><br><button onclick='go()' style='padding:15px 30px;background:gold;color:black;font-weight:bold;font-size:20px'>DOWNLOAD</button>
<div style='margin-top:20px;background:#333;height:30px;border-radius:10px'><div id='b' style='background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px'>0%</div></div>
<p id='t'></p><div id='r'></div>
<script>
let myid=null;
function go(){{
 let url=document.getElementById('u').value;
 fetch('/start?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{{myid=d.id; check();}});
}}
function check(){{
 fetch('/progress/'+myid).then(r=>r.json()).then(d=>{{
  document.getElementById('b').style.width=d.p+'%';document.getElementById('b').innerText=d.p+'%';
  document.getElementById('t').innerText=d.s;
  if(d.f){{document.getElementById('r').innerHTML='<a href="/get/'+d.f+'" download style="background:green;color:white;padding:15px;display:block">✅ SAVE VIDEO</a>';}}
  else if(d.u){{document.getElementById('r').innerHTML='<a href="'+d.u+'" style="background:green;color:white;padding:15px;display:block">✅ SAVE VIDEO</a>';}}
  else if(!d.e){{setTimeout(check,800);}} else {{document.getElementById('t').innerText=d.e;}}
 }});
}}
</script></body></html>
"""

@app.route("/start")
def start():
    url=request.args.get('url',''); did=str(uuid.uuid4())[:8]
    progress[did]={'p':0,'s':'Starting...','f':None,'u':None,'e':None}
    def run():
        try:
            def h(d):
                if d['status']=='downloading':
                    tot=d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    progress[did]['p']=int(d.get('downloaded_bytes',0)*100/tot)
                    progress[did]['s']=f"Downloading {progress[did]['p']}%"
            with yt_dlp.YoutubeDL(get_opts(f'{FOLDER}/%(title)s_{did}.%(ext)s',[h])) as ydl:
                info=ydl.extract_info(url,download=True)
                progress[did]['f']=os.path.basename(ydl.prepare_filename(info)); progress[did]['p']=100; progress[did]['s']='Done!'
        except Exception as e:
            progress[did]['e']=str(e)[:400]; progress[did]['s']='Error'
    threading.Thread(target=run).start()
    return jsonify({'id':did})

@app.route("/progress/<did>")
def prog(did): return jsonify(progress.get(did))
@app.route("/get/<name>")
def getf(name): return send_from_directory(FOLDER,name,as_attachment=True)
if __name__=="__main__": app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
