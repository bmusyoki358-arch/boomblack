import os, uuid, threading
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
app = Flask(__name__)
progress = {}
FOLDER = "/tmp"

@app.route("/")
def home():
    return """
<html><body style='background:black;color:gold;text-align:center;padding:20px;font-family:Arial'>
<h1>BOOM BLACK 🔥</h1>
<p>TikTok | YouTube | FB | Insta | Movies</p>
<input id='u' style='width:90%;padding:15px;font-size:18px' placeholder='Paste video link here'>
<br><br>
<button onclick='go()' style='padding:15px 30px;background:gold;color:black;font-weight:bold;font-size:20px'>DOWNLOAD VIDEO</button>
<div style='margin-top:20px;background:#333;height:30px;border-radius:10px;overflow:hidden'><div id='b' style='background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px;font-weight:bold'>0%</div></div>
<p id='t'></p>
<div id='r'></div>
<script>
let myid=null;
function go(){
 let url=document.getElementById('u').value;
 if(!url){alert('Paste link');return;}
 fetch('/start?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{myid=d.id; check();});
}
function check(){
 fetch('/progress/'+myid).then(r=>r.json()).then(d=>{
  document.getElementById('b').style.width=d.p+'%';
  document.getElementById('b').innerText=d.p+'%';
  document.getElementById('t').innerText=d.s;
  if(d.f){ document.getElementById('r').innerHTML='<a href="/get/'+d.f+'" download style="background:green;color:white;padding:15px;display:block;margin-top:15px;text-decoration:none;font-size:20px;border-radius:10px">✅ DOWNLOAD VIDEO TO PHONE</a>'; }
  else if(d.u){ document.getElementById('r').innerHTML='<a href="'+d.u+'" style="background:green;color:white;padding:15px;display:block;margin-top:15px;text-decoration:none">✅ DOWNLOAD VIDEO</a>'; }
  else if(!d.e){ setTimeout(check,800); }
  else{ document.getElementById('t').innerText=d.e; }
 });
}
</script>
</body></html>
"""

@app.route("/start")
def start():
    url=request.args.get('url','')
    did=str(uuid.uuid4())[:8]
    progress[did]={'p':0,'s':'Starting...','f':None,'u':None,'e':None}
    def run():
        try:
            def h(d):
                if d['status']=='downloading':
                    tot=d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    cur=d.get('downloaded_bytes',0)
                    progress[did]['p']=int(cur*100/tot)
                    progress[did]['s']=f'Downloading {progress[did]["p"]}%'
            opts={'outtmpl':f'{FOLDER}/%(title)s_{did}.%(ext)s','format':'best[height<=720]/best','noplaylist':True,'quiet':True,'progress_hooks':[h]}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(url,download=True)
                fn=ydl.prepare_filename(info)
                progress[did]['f']=os.path.basename(fn)
                progress[did]['p']=100
                progress[did]['s']='Done - Click green button to save!'
        except Exception as e:
            try:
                with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
                    info=ydl.extract_info(url,download=False)
                    progress[did]['u']=info.get('url') or info['formats'][-1]['url']
                    progress[did]['p']=100
                    progress[did]['s']='Done'
            except Exception as e2:
                progress[did]['e']=str(e2)
    threading.Thread(target=run).start()
    return jsonify({'id':did})

@app.route("/progress/<did>")
def prog(did): return jsonify(progress.get(did,{'p':0,'s':'wait'}))

@app.route("/get/<name>")
def getf(name): return send_from_directory(FOLDER,name,as_attachment=True)

if __name__=="__main__": app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
